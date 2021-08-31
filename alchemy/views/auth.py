import datetime
import flask
from flask import g
import flask_jwt_extended
import flask_awscognito
from alchemy import auth_manager, models, db

bp_auth = flask.Blueprint('auth', __name__)

@bp_auth.route('/redirect_to_user_home')
def redirect_to_user_home():
    if auth_manager.auth_enabled():
        if not flask_jwt_extended.verify_jwt_in_request():
            flask.abort(401)
    else:
        print('Warning: authentication is disabled! This should only happen if you are testing stuff!')
        first_account = models.Account.query.first()
        student = models.Student.query.first()
        response = flask.redirect(flask.url_for('account.student.index', account_id = first_account.id, student_id = student.id))
        return response

    # TODO when student users are added, can check here whether group is staff
    # or student, then redirect to the right page.
    g.current_user = flask_jwt_extended.get_current_user()
    if g.current_user.group == 'admin':
        # TODO instead of just returning the first available account, should find
        # the right account depending on the user.
        first_account = models.Account.query.first()
        response = flask.redirect(flask.url_for('account.index', account_id = first_account.id))
        return response
    elif g.current_user.group == 'student':
        # TODO once student is moved out of the account endpoint,
        # remove this first_account variable and account_id argument.
        first_account = models.Account.query.first()
        student = models.Student.query.get(g.current_user.id)
        if not student:
            print('Error! Cannot find student with id:', g.current_user.id)
            flask.abort(401)
        response = flask.redirect(flask.url_for('account.student.index', account_id = first_account.id, student_id = student.id))
        return response
    else:
        print('Error! Unrecognisable user group:', g.current_user.group)
        flask.abort(401)

@bp_auth.route('/aws_cognito_callback')
def aws_cognito_callback():
    # Put access token in a cookie that flask_jwt_extended can load later
    # to check token validity and return user info
    access_token = auth_manager.aws_auth.get_access_token(flask.request.args)
    auth_manager.create_or_update_aws_user(flask_jwt_extended.decode_token(access_token),
            auth_manager.aws_user_info(access_token))
    response = flask.redirect(flask.url_for('auth.redirect_to_user_home'))
    flask_jwt_extended.set_access_cookies(response, access_token, max_age=60*60)
    return response

@bp_auth.route('/sign_in')
def sign_in():
    if not auth_manager.auth_enabled():
        return flask.redirect(flask.url_for('auth.redirect_to_user_home'))
    return flask.redirect(auth_manager.aws_auth.get_sign_in_url())

@bp_auth.route('/sign_out')
def sign_out():
    response = flask.redirect('/')
    if flask_jwt_extended.verify_jwt_in_request(optional=True):
        # Block this token from being reused.
        payload = flask_jwt_extended.get_jwt()
        iat = datetime.datetime.fromtimestamp(payload['iat'])
        exp = datetime.datetime.fromtimestamp(payload['exp'])
        db.session.add(models.JwtBlocklist(jti=payload['jti'], issued_at=iat, expires_at=exp))
        db.session.commit()
        flask_jwt_extended.unset_jwt_cookies(response)
    return response
