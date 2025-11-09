from flask import Blueprint
from ..extentions import db
from ..models.task import Task

task = Blueprint('task', __name__)

@task.route('/task/<title>')
def create_task(title):
    task = Task(title=title)
    db.session.add(task)
    db.session.commit()
    return f"Task {title} created"