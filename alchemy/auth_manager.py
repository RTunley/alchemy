import flask
from flask import g
import flask_jwt_extended
import flask_awscognito
import functools, datetime
from alchemy import application, models, db

def auth_enabled():
    return application.config['ALCHEMY_CONFIG'] != 'TestConfig'

jwt_manager = flask_jwt_extended.JWTManager() if auth_enabled() else None
aws_auth = flask_awscognito.AWSCognitoAuthentication() if auth_enabled() else None

def init_app(application):
    if not auth_enabled():
        return
    jwt_manager.init_app(application)
    aws_auth.init_app(application)

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
            g.current_user = {'username': 'Alchemy User'}
        elif flask_jwt_extended.verify_jwt_in_request(optional=True):
            g.current_user = flask_jwt_extended.get_current_user()
        else:
            # User is not authorized.
            flask.abort(401)
        return func(*args, **kwargs)
    return deco

@application.errorhandler(401)
def authorization_error(e):
    return flask.redirect(flask.url_for('auth.sign_in'))


### The following functions use flask_jwt_extended decorators for handling various features: ###

@jwt_manager.user_lookup_loader
def user_lookup_loader(jwt_header, jwt_payload):
    'Returns an AwsUser object matching the user info in a JWT payload.'
    aws_client_id = jwt_payload.get('sub')
    username = jwt_payload.get('username')
    groups = jwt_payload.get('cognito:groups')
    for field in (aws_client_id, username, groups):
        if not field:
            print(f'Error: field {field} not found in JWT payload: {jwt_payload}')
            return None
    if len(groups) > 1:
        raise ValueError('Error: only 1 group supported, but user {username} has multiple groups: {groups}')
    aws_user = models.AwsUser.query.filter_by(sub = aws_client_id).first()
    if aws_user is None:
        print(f'Creating new user: sub={aws_client_id}, username={username}, group={groups[0]}')
        aws_user = models.AwsUser(sub = aws_client_id, username = username, group = groups[0])
        db.session.add(aws_user)
        db.session.commit()
    return aws_user

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
