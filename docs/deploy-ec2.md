Deploy on ec2
--------------
This document explains how to run the monolithic voting app on an EC2 instance.

1) Launch an EC2 instance
   - Go to the AWS Management Console and navigate to the EC2 service.
   - Click on "Launch Instance" and select an Amazon Machine Image (AMI) of your choice (e.g., Ubuntu Server).
   - Choose an instance type (e.g., t3.micro for free tier).
   - Configure instance details, add storage, and configure security groups to allow HTTP (port 80) and SSH (port 22) access.
   - Copy the userdata script in the Deploy folder to the EC2 instance.
2) User data script
   - The userdata script includes setting up Postgresql (initialize db, setting up user, setting local connections)
   - Installing dependencies in a virtual environment
   - Creating a env file for Postgresql localhost url 
   - Running the app with gunicorn within a service file on port 80 
3) Connect to Agile Board Web App 
   - SSH into your instance and `curl -I http://localhost` to check if the app is running.
   - Open a browser and paste the ipv4 ip address to access the Agile Board Web App.
4) Check Postgresql db 
   - SSH into your instance and run the following command to check the postgresql db:
     ```
     sudo -u postgres psql
     ```
     This will open a postgresql shell.
     - To list all databases, run `\l`.
     - To list all tables in a specific database, run `\dt+ <database_name>`.
     - To exit the postgresql shell, run `\q`.
5) Check status of service file 
     - Use the following command to check the status of the service file:
       ```
       sudo systemctl status agile_board.service
       ```
