"""

@task.route('/api/tasks', methods=['POST'])
def create_task():

    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400

    try:
        new_task = Task(
            title=data['title'],
            priority=data.get('priority', 'medium'),
            deadline=datetime.strptime(data['deadline'], '%Y-%m-%d').date() if data.get('deadline') else None,
            user_id=session['user_id']
        )

        db.session.add(new_task)
        db.session.commit()

        return jsonify(new_task.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@task.route('/api/tasks', methods=['GET'])
def get_tasks():

    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    return jsonify([task.to_dict() for task in tasks])


@task.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):

    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify(task.to_dict())


@task.route('/api/tasks/<int:task_id>/done', methods=['POST'])
def mark_task_done(task_id):

    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    task.is_done = True
    db.session.commit()

    return jsonify(task.to_dict())


@task.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):

    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task deleted successfully'})
"""

