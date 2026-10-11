#!/bin/bash

export AWS_DEFAULT_REGION=us-east-1

# ---------- 1. write the user data script to a file ----------
cat << 'USERDATA' > user-data.sh
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

cat << 'EOF' > /etc/systemd/system/agile_board.service
[Unit]
Description=Agile Board Web Application
After=network.target postgresql.service

[Service]
WorkingDirectory=/agile-board-monolith
EnvironmentFile=/agile-board-monolith/.env
ExecStart=/agile-board-monolith/.venv/bin/gunicorn 'agile_board.app:create_app()' --chdir /agile-board-monolith/src --bind 0.0.0.0:80 --workers 2
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now agile_board.service
USERDATA

# ---------- 2. delete the old security group if it exists ----------
OLD_SG=$(aws ec2 describe-security-groups \
  --filters Name=group-name,Values=agile_board \
  --query 'SecurityGroups[0].GroupId' --output text)

if [ "$OLD_SG" != "None" ]; then
  OLD_IDS=$(aws ec2 describe-instances \
    --filters Name=instance.group-id,Values=$OLD_SG Name=instance-state-name,Values=pending,running,stopping,stopped,shutting-down \
    --query 'Reservations[].Instances[].InstanceId' --output text)

  if [ -n "$OLD_IDS" ]; then
    aws ec2 terminate-instances --instance-ids $OLD_IDS
    aws ec2 wait instance-terminated --instance-ids $OLD_IDS
    sleep 30
  fi

  aws ec2 delete-security-group --group-id $OLD_SG
fi

# ---------- 3. create the new security group ----------
SG_ID=$(aws ec2 create-security-group \
  --group-name agile_board \
  --description "agile board ssh and http" \
  --query GroupId --output text)

aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0

# ---------- 4. find the latest Amazon Linux 2023 image ----------
AMI_ID=$(aws ssm get-parameter \
  --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query Parameter.Value --output text)

# ---------- 5. launch the instance ----------
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.micro \
  --key-name vockey \
  --security-group-ids $SG_ID \
  --user-data file://user-data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=agile_board}]' \
  --query 'Instances[0].InstanceId' --output text)

rm user-data.sh
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# ---------- 6. wait for the site, then print the IP only if running ----------
STATE=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].State.Name' --output text)

if [ "$STATE" == "running" ]; then
  IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

  echo "Instance is running at $IP. Waiting for the app to start (a few minutes)..."
  until curl -s -o /dev/null http://$IP; do sleep 10; done

  echo "Instance: $INSTANCE_ID"
  echo "Open:     http://$IP"
else
  echo "Instance is not running (state: $STATE). No IP to show."
fi