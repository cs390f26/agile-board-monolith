import os
from flask import Flask, render_template, g, current_app
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
import db

# function to get a connection from the connection pool. (our app object has a pool variable that is a ConnectionPool object)
# we use current_app to get the context of the current flask app that is running.
# g is essentially a hashmap made to cache variables for each http request, so each req needs to get a connection and return it.
# g's context/scope is exclusive to each http request. 
def get_db():
    if 'db_conn' not in g:
        g.db_conn = current_app.pool.getconn()
    return g.db_conn

# function to return the db connection to the pool of connections
def close_db():
    conn = g.pop('db_conn', None)
    if conn is not None:
        current_app.pool.putconn(conn)

def create_app():
    app = Flask(__name__)
    load_dotenv()
    
    DB_URL = os.getenv("DB_URL")
    if not DB_URL:
        raise RuntimeError("Environment Error: DB_URL env var not set")

    app.pool = ConnectionPool(conninfo=DB_URL, open=True)
    
    with app.pool.connection() as conn:
        db.init_db(conn)
        
    # anytime an http req is over, we tell app to run a function which returns the connection to the pool.
    app.teardown_appcontext(close_db)
    
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
