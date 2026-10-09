Deploy local 
-------------
This document explains how to deploy the Agile Board Web App locally on your machine.

1) Install Python and pip
   - Follow the instructions on the official Python website to install Python and pip. 
   - [Python Website](https://www.python.org/)
2) Install git 
   - Follow the instructions on the official git website to install git.
   - [git Website](https://git-scm.com/install/)
3) Install postgresql via brew 
   - Make sure brew is installed on your machine `brew version` or visit [Brew Website](https://brew.sh/) for more installation instructions.
   - Download Postgresql using `brew install postgresql` or visit [Postgresql Website](https://wiki.postgresql.org/wiki/Homebrew) for more installation instructions.
   - Start Postgresql server `brew services start postgresql` or `brew services run postgresql` to not have it restart on boot time.
4) Clone the repository
   - Clone the Agile Board Web App repository from GitHub in an ide or terminal using the following command `https://github.com/cs390f26/agile-board-monolith.git`
4) Create a Virtual Environment and Install dependencies
   - Create a virtual env `python3 -m venv venv` and activate it using `source venv/bin/activate`.
   - Install dependencies using `pip install -r requirements.txt`
5) Create local postgresql database
   - In your terminal activate psql `psql postgres`.
   - Create a database for the app `create database agile_board`.
   - Check which port Postgres is running on `psql -c "SHOW port;"` (usually 5432).
   - Exit psql `exit` or `\q` .
   - Create a env file using nano or your preferred text editor. `nano .env` and add the following line to the file:
  ```
   DB_URL=postgresql://localhost:<port>/<database_name>
   TEST_DB_URL=MockLink
   ```
   - `DB_URL` is the real local database from step 5. 
   - `TEST_DB_URL` is only used by the mocked test suite and is never used to connect to anything (Any non-empty value works).
5) Run the app
   - Activate permissions for run script `chmod +x script/up-local.sh`.
   - Run the app using `./script/up-local.sh`.

## Run pytest
- `pytest` - runs the tests in the test folder

## Commands For Postgresql 
   - `psql postgres` - Connect to the postgresql database.
   - `create database <database_name>` - Create a new database.
   - `drop database <database_name>` - Delete a database.
   - `psql -c "SHOW port;"` - Show the port that postgresql is running on.
   - `\c database_name` - Connect to a specific database.
   - `\q` - Exit the postgresql command line interface.
   - `\dt` - List all tables in the current database (must be connected to a database).

## Commands For Ruff Linter 
   - `ruff check src tests scripts` - Run the ruff linter on the current directory.
   - `ruff format .` - Format the code using ruff.
