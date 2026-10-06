#!/bin/bash
yum install -y git

dnf install -y git postgresql15-server postgresql15
/usr/bin/postgresql-setup --initdb

# Allow unauthenticated local connections (trust mode)
PG_HBA="/var/lib/pgsql/data/pg_hba.conf"
sed -i 's/127.0.0.1\/32            ident/127.0.0.1\/32            trust/' "$PG_HBA"

systemctl enable --now postgresql
su - postgres -c "psql -c 'CREATE USER app_user;'"
su - postgres -c "psql -c 'CREATE DATABASE agile_board OWNER app_user;'"

git clone https://github.com/cs390f26/agile-board-monolith.git /agile-board-monolith
cd /agile-board-monolith
chmod +x scripts/redeploy.sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r deploy/requirements.txt

cat << 'ENVEOF' > .env
DB_URL=postgresql://app_user@127.0.0.1:5432/agile_board
ENVEOF

cp deploy/agile_board.service /etc/systemd/system
systemctl daemon-reload
systemctl enable agile_board.service
systemctl start agile_board.service
