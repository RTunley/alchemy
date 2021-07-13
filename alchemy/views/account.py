import flask
from flask import g
from alchemy import models, auth_manager

bp_account = flask.Blueprint('account', __name__)

@bp_account.url_value_preprocessor
def bp_account_endpoints(endpoint, values):
    g.account = models.Account.query.get_or_404(values.pop('account_id'))
    g.html_title = f'Account - {g.account.name}'

@bp_account.url_defaults
def bp_account_url_defaults(endpoint, values):
    if 'account_id' not in values:
        values['account_id'] = g.account.id

@bp_account.route('/')
@auth_manager.require_group
def index():
    return flask.render_template('account/index.html')
