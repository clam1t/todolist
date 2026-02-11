from flask import Flask
from .extentions import db, migrate
from flask_socketio import SocketIO

socketio = SocketIO()


def create_app(debug=True):
    from .routes.user import user
    from .routes.task import task
    from .routes.main import main

    app = Flask(__name__, template_folder='templates')
    app.config['socket_users'] = {}
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SECRET_KEY'] = '111'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(task, url_prefix='/task')
    app.register_blueprint(main)

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    with app.app_context():
        db.create_all()

    return socketio, app