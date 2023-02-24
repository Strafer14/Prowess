# Prowess
Prowess is a project that interacts with Riot's Valorant API to retrieve data such as kills, damage, and wins for a play session. It then aggregates this data and exposes it through API endpoints served using AWS Lambda and AWS API Gateway.

## Development Environment Dependencies
Prowess requires the following dependencies to run:

* Python 3.8
* Node 16.16.0
* Serverless framework
* Docker
* Poetry
* Redis
* nose2
* mypy
* flake8

## Local Development
To run Prowess locally, follow these steps:
1. Clone the repository:
`git clone https://github.com/Strafer14/Prowess.git`
2. Run `npm install`
3. Run `pip install poetry`
4. Run `poetry install`
5. Run `docker-compose up -d`
6. Run `poetry shell`
7. Run `npm start`


## Deployment
To deploy, configure the correct AWS access key and secret then run `npm run deploy`

## Configuration
Prowess uses the following environment variables for configuration:

* REDIS_HOST: the hostname of the Redis server
* REDIS_PORT: the port number of the Redis server
* REDIS_PWD: the password of the Redis server
* PYTHON_ENV: the python environment
* DISCORD_WEBHOOK: this project uses a discord channel as an output for its' logs
* VALORANT_API_KEY: the Riot API key