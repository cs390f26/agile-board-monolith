from flask import Flask, render_template


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index_page():
        return render_template('index.html')

    @app.route('/manager')
    def manager_view():
        return render_template('manager.html')

    @app.route('/engineer/<name>')
    def engineer_view(name):
        return render_template('engineer.html', name=name)

    @app.route('/api/summary_json', methods = (['GET']))
    def whole_summary():
        return {'name': 'John Doe', 'tasks': ['Task 1', 'Task 2']}

    @app.route('api/task/', methods = (['POST']))
    def create_task():
        return {'name': 'John Doe', 'tasks': ['Task 1', 'Task 2']}

    @app.route('/api/task/<task_Id>/assign', methods = (['POST']))
    def assign_task():
        return {'name': 'John Doe', 'tasks': ['Task 1', 'Task 2']}

    @app.route('/api/task/<task_Id>/<person_Id>/inprogress', methods = (['POST']))
    def update_task_in_progress():
        return {'name': 'John Doe', 'tasks': ['Task 1', 'Task 2']}

    @app.route('/api/task/<task_Id>/<person_Id>/done', methods = (['POST']))
    def update_task_done():
        return {'name': 'John Doe', 'tasks': ['Task 1', 'Task 2']}

    @app.route('/api/people/<people_Id>', methods = (['POST']))
    def create_person():
        return {'name': 'John Doe', 'tasks': ['Task 1', 'Task 2']}

    return app
