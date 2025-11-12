from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename
from ..extentions import db
from ..models.user import User

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

@user.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('main.home'))