import os
from unittest.mock import patch

import pytest
from dotenv import load_dotenv

from agile_board.app import create_app

load_dotenv()

TEST_DB_URL = os.environ.get("TEST_DB_URL")
if not TEST_DB_URL:
    raise RuntimeError("TEST_DB_URL environment variable not set. Add it to your .env file.")


@pytest.fixture
def client():
    with patch("agile_board.app.ConnectionPool"), patch("agile_board.app.db.init_db"), patch.dict(os.environ, {"DB_URL": TEST_DB_URL}):
        flask_app = create_app()
        flask_app.config["TESTING"] = True
        with flask_app.test_client() as test_client:
            yield test_client
