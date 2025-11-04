from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

@app.route('/')
def index():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            return redirect('/dashboard')
        else:
            return "Неверные данные для входа"

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Пользователь с таким именем уже существует"

        new_user = User(username=username, password=password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/dashboard')
        except Exception as e:
            return f"При регистрации произошла ошибка: {str(e)}"

    return render_template('register.html')

# Dashboard routes
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/tasks')
def tasks():
    return render_template('tasks.html')

@app.route('/create-task')
def create_task():
    return render_template('create_task.html')

@app.route('/task-by-id')
def task_by_id():
    return render_template('task_by_id.html')

if __name__ == '__main__':
    app.run(debug=True)
