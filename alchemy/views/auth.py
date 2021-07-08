import flask
from flask import g
import flask_jwt_extended
import flask_awscognito
from alchemy import auth_manager, models

bp_auth = flask.Blueprint('auth', __name__)

@bp_auth.route('/redirect_to_user_home')
def redirect_to_user_home():
    if auth_manager.auth_enabled():
        if not flask_jwt_extended.verify_jwt_in_request():
            flask.abort(401)
    # TODO when student users are added, can check here whether group is staff
    # or student, then redirect to the right page.
    # TODO instead of just returning the first available account, should find
    # the right account depending on the user.
    first_account = models.Account.query.first()
    response = flask.redirect(flask.url_for('account.index', account_id = first_account.id))
    return response

@bp_auth.route('/aws_cognito_callback')
def aws_cognito_callback():
    # Put access token in a cookie that flask_jwt_extended can load later
    # to check token validity and return user info
    access_token = auth_manager.aws_auth.get_access_token(flask.request.args)
    response = flask.redirect(flask.url_for('auth.redirect_to_user_home'))
    flask_jwt_extended.set_access_cookies(response, access_token, max_age=30*60)
    return response

@bp_auth.route('/sign_in')
def sign_in():
    if not auth_manager.auth_enabled():
        return flask.redirect(flask.url_for('auth.redirect_to_user_home'))
    return flask.redirect(auth_manager.aws_auth.get_sign_in_url())

@bp_auth.route('/sign_out')
def sign_out():
    return 'Nope, you are stuck here forever. Or at least, until the access token expires.'
