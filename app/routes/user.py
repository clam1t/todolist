import time

import eventlet
eventlet.monkey_patch()
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from ..extentions import db
from ..models.user import User
from app import socketio
import json
user = Blueprint('user', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'app/static/uploads/avatars'

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        flash('Заполните все поля', 'error')
        return redirect(url_for('main.home'))

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash('Пользователь с таким именем уже существует', 'error')
        return redirect(url_for('main.home'))

    try:
        avatar_filename = None
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import uuid
                unique_filename = f"{uuid.uuid4()}_{filename}"


                os.makedirs(UPLOAD_FOLDER, exist_ok=True)


                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(file_path)


                avatar_filename = f"uploads/avatars/{unique_filename}"


        new_user = User(
            username=username,
            password=password,
            avatar=avatar_filename
        )

        db.session.add(new_user)
        db.session.commit()


        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session['avatar'] = new_user.avatar

        return redirect(url_for('main.dashboard'))

    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при регистрации: {str(e)}', 'error')
        return redirect(url_for('main.home'))


@user.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        session['avatar'] = user.avatar

        return redirect(url_for('main.dashboard'))
    else:
        flash('Неверное имя пользователя или пароль', 'error')
        return redirect(url_for('main.home'))


@socketio.on('connect')
def on_connect():
    user_id = session.get('user_id')
    sid = request.sid
    if user_id:
        current_app.config['socket_users'][user_id] = sid
        print(f"User {user_id} connected with SID: {sid}")
    else:
        print("Unauthenticated client connected")

@user.route('/register_qt', methods=['POST'])
def register_qt():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'access': False
            }), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                'access': False
            }), 400

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({
                'access': False
            }), 409

        new_user = User(
            username=username,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()


        session['user_id'] = new_user.id
        session['username'] = new_user.username

        return jsonify({
            'access': True,
            'user': {
                'id': new_user.id,
                'username': new_user.username
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'access': False
        }), 500


@user.route('/login_qt', methods=['POST'])
def login_qt():
    data = request.get_json()

    if not data:
        return jsonify({
            'access': False
        }), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({
            'access': False
        }), 400

    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['user_id'] = user.id
        session['username'] = user.username

        return jsonify({
            'access': True,
            'user': {
                'id': user.id,
                'username': user.username,
            }
        }), 200
    else:
        return jsonify({
            'access': False
        }), 401

@user.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('main.home'))