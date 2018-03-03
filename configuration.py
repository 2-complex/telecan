class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "SECRET"
    CSRF_ENABLED = True

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
