from flask import Flask
from .extentions import db
from .routes.user import user
from .routes.task import task
from .routes.main import main

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.register_blueprint(user)
    app.register_blueprint(task)
    app.register_blueprint(main)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app