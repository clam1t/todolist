from flask import Blueprint, render_template, session, redirect, url_for, flash

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('main/home.html')

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Сначала войдите в систему', 'error')
        return redirect(url_for('main.home'))
    return render_template('main/dashboard.html')

@main.route('/tasks')
def tasks():
    if 'user_id' not in session:
        flash('Сначала войдите в систему', 'error')
        return redirect(url_for('main.home'))
    return render_template('main/tasks.html')

@main.route('/create_task')
def create_task():
    if 'user_id' not in session:
        flash('Сначала войдите в систему', 'error')
        return redirect(url_for('main.home'))
    return render_template('main/create_task.html')

@main.route('/task_by_id')
def task_by_id():
    if 'user_id' not in session:
        flash('Сначала войдите в систему', 'error')
        return redirect(url_for('main.home'))
    return render_template('main/task_by_id.html')

@main.route('/about')
def about():
    return render_template('main/about.html')