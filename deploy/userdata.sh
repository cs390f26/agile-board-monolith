#!/bin/bash

dnf install -y git postgresql15-server postgresql15 python3.11 python3.11-pip
postgresql-setup --initdb

sed -i 's/ident/trust/' /var/lib/pgsql/data/pg_hba.conf

systemctl enable --now postgresql

su - postgres -c "psql -c 'CREATE USER app_user;'"
su - postgres -c "psql -c 'CREATE DATABASE agile_board OWNER app_user;'"

git clone https://github.com/cs390f26/agile-board-monolith.git /agile-board-monolith
cd /agile-board-monolith
python3.11 -m venv .venv
.venv/bin/pip install -r deploy/requirements.txt

echo "DB_URL=postgresql://app_user@127.0.0.1:5432/agile_board" > .env

cp deploy/agile_board.service /etc/systemd/system/agile_board.service
systemctl daemon-reload
systemctl enable --now agile_board.service