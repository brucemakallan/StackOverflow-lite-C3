from flask_jwt_extended import JWTManager

from app.views import app

if __name__ == '__main__':
    app.config['JWT_SECRET_KEY'] = 'kk38e1c32de0961d5d3bfb14f8a66e006cfb1cfbf3f0c0f5'
    jwt = JWTManager(app)
    app.run()
