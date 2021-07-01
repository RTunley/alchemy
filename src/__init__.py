from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_login import LoginManager

application = Flask(__name__)

application.config['SECRET_KEY'] = '00f9181c26987b00e43e23834b26f1f3'
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///master.db'
application.config['MAX_CONTENT_LENGTH'] = 1000*1024*1025 #1 GB max upload limit

#config

application.config.from_object('sam.config.BaseConfig')
db = SQLAlchemy(application)

# Add jinja custom filter to strip trailing zero from a number, or convert
# to empty string if value is None.
@application.template_filter('prettify_number')
def prettify_number(arg):
    if arg is None:
        return ''
    if type(arg) == float and int(arg) == arg:
        return int(arg)
    return arg

from sam import models
from sam.views import account, course, clazz, paper, library

course.bp_course.register_blueprint(clazz.bp_clazz, url_prefix='/clazz/<clazz_id>')
course.bp_course.register_blueprint(paper.bp_paper, url_prefix='/paper/<paper_id>')
course.bp_course.register_blueprint(library.bp_library, url_prefix='/library')

application.register_blueprint(course.bp_course, url_prefix='/course/<course_id>')
application.register_blueprint(account.bp_account)
