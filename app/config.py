

class Config(object):
    """Parent configuration class."""
    DEBUG = False


class DevelopmentConfig(Config):
    """Configurations for Development. Inherits from parent Configuration class"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Configurations for Testing, with a separate test database. Inherits from parent Configuration class"""
    TESTING = True
    DEBUG = True


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig
}
