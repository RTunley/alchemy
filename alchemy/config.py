import jwt.algorithms
import requests
import json, os, datetime

def download_cognito_public_keys(region, user_pool_id):
    # Cognito public keys are at well-known location
    url = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
    response = requests.get(url)
    return json.dumps(json.loads(response.text)['keys'][1]) # a dict with 'alg', 'kid' etc.

def non_production_flask_secret_key():
    # Flask secret key for non-production purposes.
    # Generate with: python -c "import os,base64; print(base64.b64encode(os.urandom(32)).decode('ascii'))"
    return '4Ptzk4hcvCenHt1mxB+/eamlqarCFfH5p5kte4ptdyk='

def configure_flask_awscognito(config, values):
    for key in ('AWS_DEFAULT_REGION',
            'AWS_COGNITO_DOMAIN',
            'AWS_COGNITO_USER_POOL_ID',
            'AWS_COGNITO_USER_POOL_CLIENT_ID',
            'AWS_COGNITO_USER_POOL_CLIENT_SECRET',
            'AWS_COGNITO_REDIRECT_URL'):
        if key in values:
            setattr(config, key, values[key])
        else:
            try:
                setattr(config, key, os.environ[key])
            except KeyError:
                raise KeyError(f'Missing environment variable: {key}')


def configure_flask_jwt_extended(config):
    config.JWT_TOKEN_LOCATION = ['cookies']
    config.JWT_COOKIE_SECURE = True
    config.JWT_COOKIE_CSRF_PROTECT = False  # CSRF attacks not relevant as we're using Cognito OAuth
    config.JWT_ALGORITHM = 'RS256'
    config.JWT_IDENTITY_CLAIM = 'sub'
    config.JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)
    config.JWT_PUBLIC_KEY = jwt.algorithms.RSAAlgorithm.from_jwk(
            download_cognito_public_keys(config.AWS_DEFAULT_REGION, config.AWS_COGNITO_USER_POOL_ID))
    # JWT_PRIVATE_KEY = '' # not set, we don't send any encoded requests at the moment
    # JWT_SECRET_KEY = ''  # not set, will default to Flask SECRET_KEY instead


class BaseConfig(object):
    MAX_CONTENT_LENGTH = 1000*1024*1025 #1 GB max upload limit

class TestConfig(BaseConfig):
    ALCHEMY_CONFIG = 'TestConfig'
    FLASK_ENV = 'development'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = non_production_flask_secret_key()

    TESTING = True
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False

class DevelopmentConfig(BaseConfig):
    ALCHEMY_CONFIG = 'DevelopmentConfig'
    FLASK_ENV = 'development'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///master.db'
    SECRET_KEY = non_production_flask_secret_key()

    def __init__(self):
        # Use the Alchemy Development user pool.
        flask_awscognito_config = {
            'AWS_DEFAULT_REGION': 'ap-southeast-1',
            'AWS_COGNITO_DOMAIN': 'https://alchemy.auth.ap-southeast-1.amazoncognito.com',
            'AWS_COGNITO_USER_POOL_ID': 'ap-southeast-1_k8sm2XbyZ',
            'AWS_COGNITO_USER_POOL_CLIENT_ID': '2fiehmng5ksikubsknapoe6efr',
            'AWS_COGNITO_USER_POOL_CLIENT_SECRET': '1v605kvedkhcjfpg6jchgs4nv4hkhhrc5og82og9363no77spsj2',
            'AWS_COGNITO_REDIRECT_URL': 'http://localhost:5000/auth/aws_cognito_callback',
        }
        configure_flask_awscognito(self, flask_awscognito_config)
        configure_flask_jwt_extended(self)

class ProductionConfig(BaseConfig):
    ALCHEMY_CONFIG = 'ProductionConfig'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///master.db'

    def __init__(self):
        self.SECRET_KEY = os.environ['SECRET_KEY']

        # Use the Alchemy Development user pool.
        flask_awscognito_config = {
            'AWS_DEFAULT_REGION': os.environ['AWS_DEFAULT_REGION'],
            'AWS_COGNITO_DOMAIN': os.environ['AWS_COGNITO_DOMAIN'],
            'AWS_COGNITO_USER_POOL_ID': os.environ['AWS_COGNITO_USER_POOL_ID'],
            'AWS_COGNITO_USER_POOL_CLIENT_ID': os.environ['AWS_COGNITO_USER_POOL_CLIENT_ID'],
            'AWS_COGNITO_USER_POOL_CLIENT_SECRET': os.environ['AWS_COGNITO_USER_POOL_CLIENT_SECRET'],
            'AWS_COGNITO_REDIRECT_URL': os.environ['AWS_COGNITO_REDIRECT_URL'],
        }
        configure_flask_awscognito(self, flask_awscognito_config)
        configure_flask_jwt_extended(self)
