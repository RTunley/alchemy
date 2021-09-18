import flask
from flask import g
import flask_jwt_extended
import flask_awscognito
import requests

import functools, datetime
from alchemy import application, models, db

def auth_enabled():
    return application.config['ALCHEMY_CONFIG'] != 'TestConfig'

jwt_manager = None
aws_auth = None

def init_app(application):
    if not auth_enabled():
        return
    global jwt_manager, aws_auth
    jwt_manager = flask_jwt_extended.JWTManager(application)
    aws_auth = flask_awscognito.AWSCognitoAuthentication(application)

    @jwt_manager.user_lookup_loader
    def user_lookup_loader(jwt_header, jwt_payload):
        'Returns an AwsUser object matching the user info in a JWT payload.'
        return models.AwsUser.query.filter_by(sub = jwt_payload.get('sub')).first()

    @jwt_manager.token_in_blocklist_loader
    def token_in_blocklist_loader(jwt_header, jwt_payload):
        'Called to check whether a token has been revoked (i.e. if user has signed out).'
        jti = jwt_payload["jti"]
        token = db.session.query(models.JwtBlocklist.id).filter_by(jti=jti).scalar()
        # While we're here, check whether any expired tokens should be removed.
        remove_expired_tokens()
        return token is not None

    @jwt_manager.revoked_token_loader
    def revoked_token_loader(jwt_header, jwt_payload):
        'Called when user tries to access a protected page after signing out.'
        return flask.redirect(flask.url_for('auth.sign_in'))

    @jwt_manager.expired_token_loader
    def expired_token_loader(jwt_header, jwt_payload):
        'Called when user tries to access a protected page after the access token has expired.'
        return flask.redirect(flask.url_for('auth.sign_in'))

    @jwt_manager.invalid_token_loader
    def invalid_token_loader(error_string):
        'Called when the JWT is invalid.'
        print('Invalid JWT encountered!', error_string)
        return flask.redirect(flask.url_for('auth.sign_in'))

    @jwt_manager.unauthorized_loader
    def unauthorized_loader(error_string):
        'Called when no JWT is found.'
        print('No JWT found!', error_string)
        return flask.redirect(flask.url_for('auth.sign_in'))

    @jwt_manager.user_lookup_error_loader
    def user_lookup_error_loader(jwt_header, jwt_payload):
        'Called a user cannot be found from the JWT payload.'
        print('Failed to find user from payload:', jwt_payload)
        return flask.redirect(flask.url_for('auth.sign_in'))

def remove_expired_tokens():
    now = datetime.datetime.now()
    tokens = models.JwtBlocklist.query.filter(now > models.JwtBlocklist.expires_at).all()
    for token in tokens:
        db.session.delete(token)
    if len(tokens) > 0:
        db.session.commit()

# TODO support an arg specifying the authorized groups, e.g. 'staff', 'student'
def require_group(func):
    'Decorator function for routes that should only be accessible if authorized.'
    @functools.wraps(func)
    def deco(*args, **kwargs):
        if not auth_enabled():
            g.current_user = None
        elif flask_jwt_extended.verify_jwt_in_request(optional=True):
            g.current_user = flask_jwt_extended.get_current_user()
        else:
            # User is not authorized.
            flask.abort(401)
        return func(*args, **kwargs)
    return deco

def create_or_update_aws_user(jwt_payload, user_info):
    try:
        aws_user = models.AwsUser.from_jwt(jwt_payload)
    except ValueError as value_error:
        print('Unable to load user!', value_error)
        flask.abort(401)
    is_new_user = False
    if not aws_user.id:
        db.session.add(aws_user)
        is_new_user = True
    if is_new_user or aws_user.update_user_attributes(user_info):
        db.session.commit()
    return aws_user

def aws_user_info(access_token):
    'Calls the AWS User Pools Auth API to request user info.'
    user_url = f'{aws_auth.cognito_service.domain}/oauth2/userInfo'
    header = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.post(user_url, headers=header)
        response_json = response.json()
    except requests.exceptions.RequestException as e:
        print('Unable to retrieve user info!', e)
        flask.abort(401)
    return response_json

@application.errorhandler(401)
def authorization_error(e):
    'Handles 401 (authorization) errors for e.g. when flask.abort(401) is called.'
    return flask.redirect(flask.url_for('auth.sign_in'))


### The following functions use flask_jwt_extended decorators for handling various features: ###
