import jwt.algorithms
import requests
import json, os

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

class LocalDevelopmentConfig(BaseConfig):
    ALCHEMY_CONFIG = 'LocalDevelopmentConfig'
    FLASK_ENV = 'development'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///master.db'
    SECRET_KEY = non_production_flask_secret_key()

    def __init__(self):
        # Use the Alchemy Development user pool.
        flask_awscognito_config = {
            'AWS_DEFAULT_REGION': 'ap-southeast-1',
            'AWS_COGNITO_DOMAIN': 'https://alchemy-dev.auth.ap-southeast-1.amazoncognito.com',
            'AWS_COGNITO_USER_POOL_ID': 'ap-southeast-1_O0rRyXHZH',
            'AWS_COGNITO_USER_POOL_CLIENT_ID': '2chtn4uoa9bv9pbtc0g87v5uv',
            'AWS_COGNITO_USER_POOL_CLIENT_SECRET': 'teli8ecv2jt87ohjod95v1q9lqjfknem4eu4lkji9nlsqrcr8t2',
            'AWS_COGNITO_REDIRECT_URL': 'http://localhost:5000/auth/aws_cognito_callback',
        }
        configure_flask_awscognito(self, flask_awscognito_config)
        configure_flask_jwt_extended(self)

class RemoteDevelopmentConfig(BaseConfig):
    ALCHEMY_CONFIG = 'RemoteDevelopmentConfig'
    FLASK_ENV = 'development'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///master.db'
    SECRET_KEY = non_production_flask_secret_key()

    def __init__(self):
        # Use the Alchemy Development user pool.
        flask_awscognito_config = {
            'AWS_DEFAULT_REGION': 'ap-southeast-1',
            'AWS_COGNITO_DOMAIN': 'https://alchemy-dev.auth.ap-southeast-1.amazoncognito.com',
            'AWS_COGNITO_USER_POOL_ID': 'ap-southeast-1_O0rRyXHZH',
            'AWS_COGNITO_USER_POOL_CLIENT_ID': '1rp5emoi14vmkrgv2fcj9tar55',
            'AWS_COGNITO_USER_POOL_CLIENT_SECRET': '1qfo8m4gg6ch1mii9mlm0glv803fm8foe9a5jlaci7248cm6uq3c',
            'AWS_COGNITO_REDIRECT_URL': 'https://alchemydev-env.eba-nk3jmbzp.ap-southeast-1.elasticbeanstalk.com/auth/aws_cognito_callback',
        }
        configure_flask_awscognito(self, flask_awscognito_config)
        configure_flask_jwt_extended(self)
