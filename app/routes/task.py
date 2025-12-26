import time

import eventlet
eventlet.monkey_patch()
from sqlalchemy import case
from app import socketio
from flask import Blueprint, render_template, flash, redirect, url_for, session, request, jsonify, current_app
from app.extentions import db
from app.models.task import Task
from datetime import datetime

task = Blueprint('task', __name__)


@task.route('/tasks', methods=['GET', 'POST'])
def tasks_page():
    if 'user_id' not in session:
        flash('Сначала войдите в систему', 'error')
        return redirect(url_for('main.home'))


    if request.method == 'POST':
        sort_by = request.form.get('sort_by').lower()
        test = request.form.get('test').lower()

    else:
        sort_by = 'newest'
        test = 'desc'


    query = Task.query.filter_by(user_id=session['user_id'])
    print(f"'{test}'")
    if test=='desc':
        if sort_by == 'priority':
            priority_order = case(
                (Task.priority == 'high', 1),
                (Task.priority == 'medium', 2),
                (Task.priority == 'low', 3),
            )
            tasks = query.order_by(priority_order, Task.id.desc()).all()
        elif sort_by == 'deadline':
            tasks = query.order_by(Task.deadline.asc().nulls_last(), Task.id.desc()).all()
        elif sort_by == 'status':
            tasks = query.order_by(Task.is_done.asc(), Task.id.desc()).all()
        else:
            tasks = query.order_by(Task.id.desc()).all()

        return render_template('main/tasks.html', tasks=tasks, current_sort=sort_by)
    elif test=='asc':
        if sort_by == 'priority':
            priority_order = case(
                (Task.priority == 'high', 3),
                (Task.priority == 'medium', 2),
                (Task.priority == 'low', 1),
            )
            tasks = query.order_by(priority_order, Task.id.desc()).all()
        elif sort_by == 'deadline':
            tasks = query.order_by(Task.deadline.desc().nulls_last(), Task.id.desc()).all()
        elif sort_by == 'status':
            tasks = query.order_by(Task.is_done.desc(), Task.id.desc()).all()
        else:
            tasks = query.order_by(Task.id.asc()).all()

        return render_template('main/tasks.html', tasks=tasks, current_sort=sort_by)



@task.route('/create_task', methods=['GET', 'POST'])
def create_task_page():
    if 'user_id' not in session:
        flash('Сначала войдите в систему', 'error')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        title = request.form.get('title')
        priority = request.form.get('priority')
        deadline = request.form.get('deadline')

        if not title:
            flash('Task title is required', 'error')
            return render_template('main/create_task.html')

        try:
            new_task = Task(
                title=title,
                priority=priority,
                deadline=datetime.strptime(deadline, '%Y-%m-%d').date() if deadline else None,
                user_id=session['user_id']
            )

            db.session.add(new_task)
            db.session.commit()

            flash('Task created successfully!', 'success')
            return redirect(url_for('task.tasks_page'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating task: {str(e)}', 'error')

    return render_template('main/create_task.html')


@task.route('/task_by_id', methods=['GET', 'POST'])
def task_by_id_page():
    if 'user_id' not in session:
        flash('Сначала войдите в систему', 'error')
        return redirect(url_for('main.home'))

    task = None
    if request.method == 'POST':
        task_id = request.form.get('task_id')
        if task_id:
            task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
            if not task:
                flash('Task not found', 'error')
    elif request.args.get('task_id'):
        task = Task.query.filter_by(id=request.args.get('task_id'), user_id=session['user_id']).first()
    return render_template('main/task_by_id.html', task=task)


@task.route('/task/<int:task_id>/done')
def mark_task_done_page(task_id):
    if 'user_id' not in session:
        flash('Сначала войдите в систему', 'error')
        return redirect(url_for('main.home'))

    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    if task:
        task.is_done = True
        db.session.commit()
        flash('Task marked as done!', 'success')
    else:
        flash('Task not found', 'error')

    return redirect(url_for('task.tasks_page'))


@task.route('/task/<int:task_id>/delete')
def delete_task_page(task_id):
    if 'user_id' not in session:
        flash('Сначала войдите в систему', 'error')
        return redirect(url_for('main.home'))

    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    else:
        flash('Task not found', 'error')

    return redirect(url_for('task.tasks_page'))


@task.route('/tasks_json', methods=['GET'])
def tasks_json():
    if 'user_id' not in session:
        return jsonify({
            'access': False,
            'error': 'Not authenticated'
        }), 401

    sort_by = request.args.get('sort_by', 'newest')
    order = request.args.get('order', 'desc')

    user_id = session['user_id']
    query = Task.query.filter_by(user_id=user_id)

    if order == 'desc':
        if sort_by == 'priority':
            priority_order = case(
                (Task.priority == 'high', 1),
                (Task.priority == 'medium', 2),
                (Task.priority == 'low', 3),
            )
            tasks = query.order_by(priority_order, Task.id.desc()).all()
        elif sort_by == 'deadline':
            tasks = query.order_by(Task.deadline.asc().nulls_last(), Task.id.desc()).all()
        elif sort_by == 'status':
            tasks = query.order_by(Task.is_done.asc(), Task.id.desc()).all()
        else:
            tasks = query.order_by(Task.id.desc()).all()
    else:
        if sort_by == 'priority':
            priority_order = case(
                (Task.priority == 'high', 3),
                (Task.priority == 'medium', 2),
                (Task.priority == 'low', 1),
            )
            tasks = query.order_by(priority_order, Task.id.desc()).all()
        elif sort_by == 'deadline':
            tasks = query.order_by(Task.deadline.desc().nulls_last(), Task.id.desc()).all()
        elif sort_by == 'status':
            tasks = query.order_by(Task.is_done.desc(), Task.id.desc()).all()
        else:
            tasks = query.order_by(Task.id.asc()).all()

    tasks_list = []
    for task_item in tasks:
        tasks_list.append({
            'id': task_item.id,
            'title': task_item.title,
            'priority': task_item.priority,
            'deadline': task_item.deadline.strftime('%Y-%m-%d') if task_item.deadline else None,
            'is_done': task_item.is_done,
        })

    return jsonify({
        'access': True,
        'tasks': tasks_list,
        'count': len(tasks_list)
    }), 200


@task.route('/task/<int:task_id>/done_json', methods=['POST'])
def mark_task_done_json(task_id):
    if 'user_id' not in session:
        return jsonify({
            'access': False
        }), 401

    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    if task:
        task.is_done = True
        db.session.commit()
        task_done(session['user_id'], task_id)
        return jsonify({
            'access': True
        }), 200

    else:
        return jsonify({
            'access': False
        }), 404

def task_done(session_user_id, task_id):
    user_id = session_user_id
    sid = current_app.config.get('socket_users', {}).get(user_id)
    if sid:
        socketio.emit('task_done', {'task_id': task_id, 'done': True}, to=sid)
    else:
        print("Unauthenticated client connected")


@task.route('/task/<int:task_id>/delete_json', methods=['POST'])
def delete_task_json(task_id):
    if 'user_id' not in session:
        return jsonify({
            'access': False
        }), 401

    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        task_del(session['user_id'], task_id)
        return jsonify({
            'access': True
        }), 200
    else:
        return jsonify({
            'access': False
        }), 404


def task_del(session_user_id, task_id):
    user_id = session_user_id
    sid = current_app.config.get('socket_users', {}).get(user_id)
    if sid:
        socketio.emit('task_del', {'task_id': task_id, 'del': True}, to=sid)
    else:
        print("Unauthenticated client connected")

@task.route('/create_task_json', methods=['GET', 'POST'])
def create_task_page_json():
    data = request.get_json()
    if 'user_id' not in session:
        return jsonify({
            'access': False
        }), 401


    title = data.get('title')
    priority = data.get('priority')
    deadline = data.get('deadline')

    new_task = Task(
        title=title,
        priority=priority,
        deadline=datetime.strptime(deadline, '%Y-%m-%d').date() if deadline else None,
        user_id=session['user_id']
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({
        'access': True
    }), 200


@task.route('/task_by_id_json', methods=['GET', 'POST'])
def task_by_id_page_json():
    data = request.get_json()
    if 'user_id' not in session:
        return jsonify({'access': False}), 401

    task_id = data.get('task_id')
    if not task_id:
        return jsonify({'access': False, 'error': 'No task ID provided'}), 400


    task_obj = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()

    if not task_obj:
        return jsonify({'access': False, 'error': 'Task not found'}), 404


    task_data = {
        'id': task_obj.id,
        'title': task_obj.title,
        'priority': task_obj.priority,
        'deadline': task_obj.deadline.strftime('%Y-%m-%d') if task_obj.deadline else None,
        'is_done': task_obj.is_done,
    }

    return jsonify({
        'access': True,
        'task': task_data
    }), 200

