import flask
from flask import g
import flask_jwt_extended
import flask_awscognito
import functools
from alchemy import application, models, db

def auth_enabled():
    return application.config['ALCHEMY_CONFIG'] in ('LocalDevelopmentConfig', 'RemoteDevelopmentConfig')

jwt_manager = flask_jwt_extended.JWTManager() if auth_enabled() else None
aws_auth = flask_awscognito.AWSCognitoAuthentication() if auth_enabled() else None

def init_app(application):
    if not auth_enabled():
        return
    jwt_manager.init_app(application)
    aws_auth.init_app(application)

def aws_user_from_payload(jwt_payload):
    'Returns an AwsUser object matching the user info in a JWT payload.'
    aws_client_id = jwt_payload.get('sub')
    username = jwt_payload.get('username')
    groups = jwt_payload.get('cognito:groups')
    for field in (aws_client_id, username, groups):
        if not field:
            raise ValueError(f'Error: field {field} not found in JWT payload: {jwt_payload}')
    if len(groups) > 1:
        raise ValueError('Error: only 1 group supported, but user {username} has multiple groups: {groups}')
    aws_user = models.AwsUser.query.filter_by(sub = aws_client_id).first()
    if aws_user is None:
        print(f'Creating new user: sub={aws_client_id}, username={username}, group={groups[0]}')
        aws_user = models.AwsUser(sub = aws_client_id, username = username, group = groups[0])
        db.session.add(aws_user)
        db.session.commit()
    return aws_user

# TODO support an arg specifying the authorized groups, e.g. 'staff', 'student'
def require_group(func):
    'Decorator function for routes that should only be accessible if authorized.'
    @functools.wraps(func)
    def deco(*args, **kwargs):
        if not auth_enabled():
            g.current_user = {'username': 'Alchemy User'}
        elif flask_jwt_extended.verify_jwt_in_request(optional=True):
            try:
                aws_user = aws_user_from_payload(flask_jwt_extended.get_jwt())
            except ValueError as err:
                print(err)
                flask.abort(401)
            g.current_user = aws_user
        else:
            # TODO instead of just showing 401 error, can make some nice page
            # that says "you need to sign in" with a link to the sign-in page.
            # return flask.redirect(aws_auth.get_sign_in_url())
            print('User tried to access endpoint %s, but not authenticated!' % flask.request.endpoint)
            flask.abort(401)
        return func(*args, **kwargs)
    return deco
