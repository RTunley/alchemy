'''
Syncs the set of users in the local database to the Cognito user pool. The local database is taken
as the definitive source: any users not in the local db will be deleted from the user pool.

Optionally, this can also sync a set of user definitions from a CSV file or dummy data to the
local database before syncing with the Cognito user pool. Any users not in the source data will
be deleted from the local database.


Examples
========

These are run from the root Alchemy directory.

    # Syncs the local Student table with the 'student' group of the Cognito user pool:
    python -m tools.sync_users --group student --from-db

    # Syncs data from 'students_data.csv' with the local Student table, and syncs the resulting
    # user set with the 'student' group of the Cognito user pool:
    python -m tools.sync_users --group student --from-file students_data.csv

    # Same as the previous command, but uses a dummy data set instead of a file:
    python -m tools.sync_users --group student --from-dummy


AWS Credentials
===============

Note that the Cognito functionality requires the AWS CLI to be installed, as it uses the default
AWS CLI profile to connect to Cognito services. Essentially, this requires the ~/.aws/credentials
file specifying the aws_access_key_id and aws_secret_access_key values:

    [default]
    aws_access_key_id = <your_AWS_access_key_id>
    aws_secret_access_key = <your_AWS_secret_access_key>
'''

import argparse, collections, csv, os, sys, io
import sqlalchemy
import boto3
from alchemy import application, models, db

dummy_csv_data = {
    'student': '''
        School ID,Email address,Family Name,Given Name
        1000,Jimmy.Knuckle@example.com,Knuckle,Jimmy
        1001,AyAyRon.Dinglebop@example.com,Dinglebop,AyAyRon
        1002,Beefy.Taco@example.com,Taco,Beefy
        1003,Chaneese.Spankle@example.com,Spankle,Chaneese
        1004,Bobbins.Wiremack@example.com,Wiremack,Bobbins
        1005,Ranger.Gilespie@example.com,Gilespie,Ranger
        1006,Django.Meathead@example.com,Meathead,Django
        '''.strip(),
    'teacher': '''
        School ID,Email address,Family Name,Given Name
        2000,Katara.Waterbender@example.com,Waterbender,Katara
        2001,Zuko.Firenation@example.com,Firenation,Zuko
        '''.strip(),
    'admin': '''
        School ID,Email address,Family Name,Given Name
        3000,robin@example.com,Tunley,Robin
        3001,bea@example.com,Lam,Bea
        '''.strip(),
}

def model_class_for_group(group):
    if not hasattr(models, group.title()):
        raise ValueError(f'Cannot load group {group}, Alchemy does not have a model class named {group.title()}')
    return getattr(models, group.title())


class UserInfo:
    properties = {'id', 'email', 'username', 'family_name', 'given_name'}

    def __init__(self, group, model_object = None, **kwargs):
        self.group = group
        if set(kwargs.keys()) != UserInfo.properties:
            raise ValueError('Unexpected UserInfo properties:', kwargs.keys())
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.model_object = model_object or model_class_for_group(group).query.get(self.id)
        self.aws_user = models.AwsUser.query.get(self.id)

    def __repr__(self):
        return f'(id={self.id}, username={self.username})'

    @staticmethod
    def create_list_from_db(group):
        model_objects = model_class_for_group(group).query.all()
        user_infos = []
        for model_object in model_objects:
            properties = {}
            for prop in UserInfo.properties:
                properties[prop] = getattr(model_object.aws_user, prop)
            user_infos.append(UserInfo(group, model_object, **properties))
        return user_infos

    @staticmethod
    def create_list_from_csv(csv_data, group):
        skip_headers = csv.Sniffer().has_header(csv_data.read(1024))
        csv_data.seek(0)
        reader = csv.reader(csv_data)
        if skip_headers:
            next(reader)
        user_infos = []
        for row in reader:
            if len(row) != 4:
                raise ValueError(f'Expected 4 columns in CSV input file, got {len(row)}')
            id, email, family_name, given_name = row
            # Take the username from the email address, and lowercase it, since that's what AWS does.
            username = email.split('@')[0].lower()
            user_infos.append(UserInfo(group, id=int(id), email=email, username=username, family_name=family_name, given_name=given_name))
        return user_infos

    @staticmethod
    def find_username_in_list(user_list, username):
        for user in user_list:
            if user.username == username:
                return user
        return None


class CognitoUser:
    def matches_user_attributes(self, user_info):
        for key in models.AwsUser.USER_ATTRIBUTES:
            if getattr(self, key, '') != getattr(user_info, key, ''):
                return False
        return True

    def __repr__(self):
        return f'(id={self.id}, username={self.username})'

    @staticmethod
    def from_user_dict(user_dict):
        user_attrs = user_dict['Attributes']
        cognito_user = CognitoUser()
        cognito_user.username = user_dict['Username']
        cognito_user.id = ''
        for user_attr in user_attrs:
            key = user_attr['Name']
            value = user_attr['Value']
            if key in models.AwsUser.USER_ATTRIBUTES:
                setattr(cognito_user, key, value)
            elif key == 'custom:school_id':
                cognito_user.id = value
            elif key == 'sub':
                cognito_user.sub = value
        return cognito_user

    @staticmethod
    def find_username_in_list(cognito_users, username):
        for cognito_user in cognito_users:
            if cognito_user.username == username:
                return cognito_user
        return None

class CognitoOperator:
    def __init__(self, group):
        self.group = group
        self.aws_client = boto3.client('cognito-idp', region_name = application.config['AWS_DEFAULT_REGION'])
        self.existing_cognito_users = self.find_users_in_pool()
        print(f'Found {len(self.existing_cognito_users)} existing users in user pool "{group}" group:', self.existing_cognito_users)

    def sync_users_to_cognito(self, user_infos):
        # Upload a new user if it is not in the user pool. If it is already in the pool, update
        # attributes if needed.
        for user_info in user_infos:
            cognito_user = CognitoUser.find_username_in_list(self.existing_cognito_users, user_info.username)
            if cognito_user is None:
                # Upload this user to the user pool
                print(f'Add to user pool: {user_info}')
                self.add_user_to_pool(user_info)
            elif not cognito_user.matches_user_attributes(user_info):
                # Update the user pool entry for this user.
                print(f'Update details in user pool: {user_info}')
                self.update_user_in_pool(user_info)
            else:
                print(f'No change, already in user pool: {user_info}')

        # Remove users from the user pool if they are not in user_infos.
        # TODO add option to just disable user instead of removing it.
        for cognito_user in self.existing_cognito_users:
            if UserInfo.find_username_in_list(user_infos, cognito_user.username) is None:
                print(f'Remove from user pool: {cognito_user}')
                self.remove_user_from_pool(cognito_user)
        db.session.commit()

    def find_users_in_pool(self):
         # TODO use NextToken to paginate requests (otherwise limited to fetching 60 users?)
        response = self.aws_client.list_users_in_group(
                UserPoolId=application.config['AWS_COGNITO_USER_POOL_ID'],
                GroupName=self.group)
        cognito_users = []
        for user_dict in response['Users']:
            cognito_users.append(CognitoUser.from_user_dict(user_dict))
        return cognito_users

    def add_user_to_pool(self, user_info):
        response = self.aws_client.admin_create_user(
                UserPoolId=application.config['AWS_COGNITO_USER_POOL_ID'],
                Username=user_info.username,
                UserAttributes=CognitoOperator.cognito_user_attributes(user_info),
                MessageAction='SUPPRESS',    # TODO add arg option to send the welcome email to real users
                DesiredDeliveryMediums=['EMAIL'])
        # Set AwsUser.sub to the one assigned by Cognito
        sub = CognitoOperator.find_aws_user_attr('sub', response.get('User', {}).get('Attributes', {}))
        if sub:
            user_info.aws_user.sub = sub
        else:
            print('AWS admin_create_user() did not return user sub value! Response was:', response)
        self.aws_client.admin_add_user_to_group(
                UserPoolId=application.config['AWS_COGNITO_USER_POOL_ID'],
                Username=user_info.username,
                GroupName=self.group)

    def update_user_in_pool(self, user_info):
        self.aws_client.admin_update_user_attributes(
                UserPoolId=application.config['AWS_COGNITO_USER_POOL_ID'],
                Username=user_info.username,
                UserAttributes=CognitoOperator.cognito_user_attributes(user_info))

    def remove_user_from_pool(self, cognito_user):
        self.aws_client.admin_delete_user(
                UserPoolId=application.config['AWS_COGNITO_USER_POOL_ID'],
                Username=cognito_user.username)

    @staticmethod
    def find_aws_user_attr(key, user_attrs):
        for user_attr in user_attrs:
            if user_attr.get('Name') == key:
                return user_attr.get('Value')
        return None

    @staticmethod
    def cognito_user_attributes(user_info):
        return [
            { 'Name': 'email', 'Value': user_info.email },
            { 'Name': 'given_name', 'Value': user_info.given_name },
            { 'Name': 'family_name', 'Value': user_info.family_name },
            { 'Name': 'email_verified', 'Value': "true" },
            { 'Name': 'custom:school_id', 'Value': str(user_info.id) },
        ]


def sync_users_to_db(user_infos, group):
    existing_aws_users = models.AwsUser.query.filter_by(group=group)

    # Add a new AwsUser if it is not in the db. If it is already in the db, update attributes if needed.
    for user_info in user_infos:
        if user_info.aws_user is None:
            # This is a new user. Add it to the db.
            print(f'Add new user: {user_info.id} {user_info.username}')
            user_info.aws_user = models.AwsUser(
                    id = user_info.id,
                    username=user_info.username,
                    group=user_info.group,
                    email=user_info.email,
                    family_name=user_info.family_name,
                    given_name=user_info.given_name)
            db.session.add(user_info.aws_user)
        elif user_info.aws_user.update_user_attributes(user_info):
            # User already exists, so just the db data for it.
            print(f'Update details in db: {user_info}')
        else:
            print(f'No change, already in db: {user_info}')

        # Add the specific model user if it doesn't yet exist.
        if user_info.model_object is None:
            model_class = model_class_for_group(user_info.group)
            user_info.model_object = model_class(id=user_info.id, aws_user=user_info.aws_user)
            db.session.add(user_info.model_object)

    # Remove AwsUser and specific model entries from the db if they are not in user_infos.
    for aws_user in existing_aws_users:
        if aws_user.group != group:
            continue
        if UserInfo.find_username_in_list(user_infos, aws_user.username) is None:
            aws_user = models.AwsUser.query.get(aws_user.id)
            model_class = model_class_for_group(aws_user.group)
            model_object = model_class.query.get(aws_user.id)
            print(f'Remove from db: AwsUser({aws_user.id}, {aws_user.username}), {model_class.__name__}({aws_user.id})')
            db.session.delete(aws_user)
            db.session.delete(model_object)
    db.session.commit()


def main():
    parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--group', help='Name of group in Cognito user pool', required=True)
    parser.add_argument('--from-db', help='Load users from the db', action='store_true')
    parser.add_argument('--from-file', help='Load users from the specified CSV file', required=False)
    parser.add_argument('--from-dummy', help='Load users from dummy data', action='store_true')
    args = parser.parse_args()

    # Read the user data input
    user_infos = []
    print('\nLoading input data...')
    if args.from_file:
        if not os.path.exists(args.from_file):
            raise ValueError(f'No such file: {args.from_file}')
        with open(args.from_file) as csv_file:
            user_infos = UserInfo.create_list_from_csv(csv_file, args.group)
            print(f'Found {len(user_infos)} {args.group.title()} entries in {csv_file.name}.')
    elif args.from_db:
        user_infos = UserInfo.create_list_from_db(args.group)
        print(f'Found {len(user_infos)} {args.group.title()} entries in db.')
    elif args.from_dummy:
        if args.group not in dummy_csv_data:
            raise ValueError(f'No dummy data available for group: {args.group}, available dummy groups are: {list(dummy_csv_data.keys())}')
        user_infos = UserInfo.create_list_from_csv(io.StringIO(dummy_csv_data[args.group]), args.group)
        print(f'Found {len(user_infos)} {args.group.title()} entries in dummy data.')
    else:
        raise ValueError('One of the --from options must be set! See --help for options.')

    cognito_operator = CognitoOperator(args.group)

    if not args.from_db:
        print('\nSyncing to local database...')
        sync_users_to_db(user_infos, args.group)

    print(f'\nSyncing to Cognito user pool "{args.group}" group...')
    cognito_operator.sync_users_to_cognito(user_infos)

if __name__ == '__main__':
    main()
