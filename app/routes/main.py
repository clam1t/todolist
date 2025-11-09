from flask import Blueprint, render_template, request, url_for, redirect

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/')
def home():
    return render_template('main/home.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('main.home'))
    return render_template('main/login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return redirect(url_for('main.login'))
    return render_template('main/register.html')