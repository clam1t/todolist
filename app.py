from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
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
