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

    return app
