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