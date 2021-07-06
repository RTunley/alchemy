
class BaseConfig(object):
    DEBUG = True
    SECRET_KEY = "00f9181c26987b00e43e23834b26f1f3"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///master.db'
    MAX_CONTENT_LENGTH = 1000*1024*1025 #1 GB max upload limit


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
