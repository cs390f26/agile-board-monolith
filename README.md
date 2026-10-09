Agile Board Monolith
-------------------
![Tests](https://github.com/cs390f26/agile-board-monolith/actions/workflows/RunPytest.yaml/badge.svg)<br>
![Tests](https://github.com/cs390f26/agile-board-monolith/actions/workflows/RunRuff.yaml/badge.svg)<br>

This repo contains the specification for a simple agile board task manager that allows a project manager to create and manage tasks and assign them to a team member and view progress on a project.  We will deploy this application in a variety of ways using cloud technologies.

* [Use cases](docs/use-cases.md) - Describes what users will experience with the running system
* [API](docs/open-api.yaml) - Describes the HTTP contract betwen the web brower (client) and the backend (server).
* [UI-Mocks](src/agile_board) - This folder contains static HTML/CSS pages for the various views of the system.
* [Data Model](docs/schema.md) - Describes how data is stored in a SQL table.
* [Deploy Locally](docs/deploy-local.md) - Describes how to deploy the application locally.
* [Deploy to Ec2](docs/deploy-ec2.md) - Describes how to deploy the application to an EC2 instance.
* [Team Workflows](docs/workflows.md) - Describes our GitHub workflows and team strategies for managing with them.

Contributors
------------
* Jamell Alvarez
* Anthony Dayoub 
* William Kerr
