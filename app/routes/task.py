from flask import Blueprint, render_template, flash, redirect, url_for, session, request, jsonify
from ..extentions import db
from ..models.task import Task
from datetime import datetime

task = Blueprint('task', __name__)


@task.route('/tasks')
def tasks_page():
	
	if 'user_id' not in session:
		flash('Сначала войдите в систему', 'error')
		return redirect(url_for('main.home'))

	# Получаем задачи пользователя
	tasks = Task.query.filter_by(user_id=session['user_id']).order_by(Task.id.desc()).all()
	return render_template('main/tasks.html', tasks=tasks)


@task.route('/create_task', methods=['GET', 'POST'])
def create_task_page():
	if 'user_id' not in session:
		flash('Сначала войдите в систему', 'error')
		return redirect(url_for('main.home'))

	if request.method == 'POST':
		# Обработка формы
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