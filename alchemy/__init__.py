import flask
from flask import g
import flask_jwt_extended
import flask_awscognito
import flask_sqlalchemy
import os
import alchemy.config

application = flask.Flask(__name__)

def set_config():
    config_class_name = os.environ.get('ALCHEMY_CONFIG', 'DevelopmentConfig')
    config_class = getattr(alchemy.config, config_class_name)
    print('Loading Alchemy config:', config_class_name)
    application.config.from_object(config_class())
set_config()

# Initialize the database and its tables
db = flask_sqlalchemy.SQLAlchemy(application)

# Add index page endpoint
@application.route('/')
def index():
    return flask.render_template('index.html')

# Add jinja custom filter to strip trailing zero from a number, or convert
# to empty string if value is None.
@application.template_filter('prettify_number')
def prettify_number(arg):
    if arg is None:
        return ''
    if type(arg) == float and int(arg) == arg:
        return int(arg)
    return arg


from alchemy import models

from alchemy import auth_manager
auth_manager.init_app(application)

from alchemy.views import auth, account, course, clazz, paper, library, cohort

course.bp_course.register_blueprint(clazz.bp_clazz, url_prefix='/clazz/<clazz_id>')
course.bp_course.register_blueprint(paper.bp_paper, url_prefix='/paper/<paper_id>')
course.bp_course.register_blueprint(library.bp_library, url_prefix='/library')
course.bp_course.register_blueprint(cohort.bp_cohort, url_prefix='/cohort')
application.register_blueprint(course.bp_course, url_prefix='/course/<course_id>')
application.register_blueprint(account.bp_account, url_prefix='/account/<account_id>')
application.register_blueprint(auth.bp_auth, url_prefix='/auth')

# Create any tables not already in the db
db.create_all()
