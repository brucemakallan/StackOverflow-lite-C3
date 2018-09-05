class Config(object):
    DEBUG = False
    DATABASE = 'stackoverflow'
    JWT_SECRET_KEY = 'kk38e1c32de0961d5d3bfb14f8a66e006cfb1cfbf3f0c0f5'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    DATABASE = 'stackoverflowtest'


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
