import flask
from flask import g
from alchemy import models

bp_account = flask.Blueprint('bp_account', __name__)

@bp_account.url_value_preprocessor
def bp_account_endpoints(endpoint, values):
    g.account = models.Account.query.first()
    g.html_title = f'Account - {g.account.name}'

@bp_account.url_defaults
def bp_account_url_defaults(endpoint, values):
    if 'account_id' not in values:
        values['account_id'] = g.account.id

@bp_account.route('/')
def index():
    return flask.render_template('account/index.html')
