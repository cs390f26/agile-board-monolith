import os
from unittest.mock import patch

import psycopg
import pytest
from dotenv import load_dotenv

from agile_board import db
from agile_board.app import create_app

load_dotenv()

TEST_DB_URL = os.getenv("TEST_DB_URL")


@pytest.fixture
def db_conn():
    if not TEST_DB_URL:
        pytest.skip("TEST_DB_URL not set in environment; skipping DB integration test.")

    conn = psycopg.connect(TEST_DB_URL)
    db.init_db(conn)

    with conn.cursor() as cur:
        cur.execute("TRUNCATE person, task RESTART IDENTITY CASCADE;")
        conn.commit()

    yield conn

    conn.close()


@pytest.fixture
def client():
    with patch("agile_board.app.ConnectionPool"), patch("agile_board.app.db.init_db"), patch.dict(os.environ, {"DB_URL": TEST_DB_URL}):
        flask_app = create_app()
        flask_app.config["TESTING"] = True
        with flask_app.test_client() as test_client:
            yield test_client
