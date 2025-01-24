# test-install-chat

This repository is used for the backend of the test-install-chat App developed using Django.

## Docker Setup

To run this project in a Docker it is assumed you have a setup [Docker Compose](https://docs.docker.com/compose/).

**Install Docker:**

- Linux - [get.docker.com](https://get.docker.com/)
- Windows or MacOS - [Docker Desktop](https://www.docker.com/products/docker-desktop)

1. Open CLI and CD to project root.
2. Clone this repo and `git clone git@github.com:mugna-tech/test-install-chat.git`
3. Go to project folder where manage.py is located.
4. Execute `docker-compose up --build` This will build the docker container.
5. `docker exec -it test_install_chat_web python manage.py migrate`
6. `docker exec -it test_install_chat_web python manage.py createsuperuser`

### Docker Notes

You will only execute `docker-compose up --build` if you have changes in your Dockerfile. To start docker containers you can either use `docker-compose up` or `docker-compose start`

**Docker Django Environments**

1. To add or use different environment values copy `docker-compose.override.yml.example` and rename it to `docker-compose.override.yml`
   and change or add environment variables needed.
2. Add a `.env` file in your project root.

Any changes in the environment variable will need to re-execute the `docker-compose up`

**To add package to uv**

```sh
docker exec -it test_install_chat_web uv add new_package_name
```

**To update pyproject.toml and lock file after adding a package**

```sh
docker exec -it test_install_chat_web uv pip compile pyproject.toml -o uv.lock
```

**Example of executing Django manage.py commands**

```sh
docker exec -it test_install_chat_web python manage.py shell
docker exec -it test_install_chat_web python manage.py makemigrations
docker exec -it test_install_chat_web python manage.py loaddata appname
```

**To copy site-packages installed by uv from docker to your host machine**

```sh
docker cp test_install_chat_web:/usr/local/lib/python3.12.2/site-packages <path where you want to store the copy>
```

**DEBUG NOTES:**

1. When adding PDB to your code you can interact with it in your CLI by executing `docker start -i test_install_chat_web`.
2. If you experience this error in web docker container `port 5432 failed: FATAL:  the database system is starting up` -- automatically force restart the test_install_chat\_web docker container by executing.
3. If you encounter missing dependencies, sync with lock file `docker exec -it test_install_chat_web uv pip sync uv.lock`

```sh
docker restart test_install_chat_web
```

## Local Environment Setup

### Required Installations

1. [Python 3.12.2](https://www.python.org/downloads/)
   On macOS (with Homebrew): `brew install python3`
2. [uv 0.4.25](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)
   `curl -LsSf https://astral.sh/uv/install.sh | sh` or `pip install uv` or `brew install uv`
3. [PostgreSQL 14.0](https://www.postgresql.org/download/)
   On macOS (with Homebrew): `brew install postgres`

### Install Requirements

1. `uv sync` and `uv sync --all-extras`
   This installs the libraries required for this project. **Note** that this will create a virtual environment automatically.
2. `pre-commit install`
   This installs pre-commit hooks to enforce code style.

### Setup PostgreSQL Database

```bash
sudo -u postgres psql

CREATE USER test_install_chat WITH PASSWORD 'test_install_chat';
ALTER USER test_install_chat CREATEDB;

CREATE DATABASE test_install_chat owner test_install_chat;
```

### Configure .env File

1. Copy `.env.example` to `.env` and customize its values.
2. `SECRET_KEY` should be a random string, you can generate a new one using the following command:
   `python -c 'from secrets import token_urlsafe; print("SECRET_KEY=" + token_urlsafe(50))'`
3. Set `DATABASE_URL` to `POSTGRES_URL=postgres://test_install_chat:test_install_chat@localhost/test_install_chat`.

### Setup DB Schema

1. `./manage.py migrate`
   This applies the migrations to your database
2. `./manage.py createsuperuser`
   This creates your superuser account. Just follow the prompts.

## Running the App


1. `source venv/bin/activate`
   Run this if the virtual environment is not activated. Run `uv venv` to create one if it does not exist.
2. `uv run uvicorn test_install_chat.asgi:application --reload`

## Running Standalone Mailpit

1. `mailpit.yml` is located in `mailpit/` directory.

2. Run the following command. This will start the `mailpit-standalone` server on port `8025`.

```bash
   docker-compose -f mailpit/mailpit.yml up
```

## Running the Celery Server

1. Make sure you have a Redis server running on localhost with the default port (6379). More information on how to setup [here](https://redis.io/docs/getting-started/installation/install-redis-on-mac-os/)
2. Set the `CELERY_BROKER_URL` env var to `redis://localhost:6379/0`
3. `celery -A test_install_chat worker -l info`
   This starts a Celery worker that will process the background tasks.
4. `celery -A test_install_chat beat -l info`
   This starts the Celery beat scheduler that will trigger the periodic tasks.

## Running the Tests

1. `pytest`
   Run `pytest --cov=. --cov-report term-missing` to also show coverage report.

## FAQs

1. Changing the `.env` file variables has no effect.
   Run `export $(grep -v '^#' .env | xargs -0)` to source the file

## Django Unfold Documentation

Unfold is a theme for Django admin that incorporates common best practices for building full-fledged admin areas. It is designed to work on top of the default administration provided by Django.

- Documentation: Full docs are available at [unfoldadmin.com](https://unfoldadmin.com/).
- Unfold: Demo site is available at [demo.unfoldadmin.com/admin/](https://demo.unfoldadmin.com/admin/).
- Formula: Repository with demo implementation at [github.com/unfoldadmin/formula](https://github.com/unfoldadmin/formula).
- Turbo: Django & Next.js boilerplate implementing Unfold at [github.com/unfoldadmin/turbo](https://github.com/unfoldadmin/turbo).

## Installing a Django application via a Git submodule

To add Django applications that are hosted on different repositories, we've added a management command that allows you to easily import that repository as a Git submodule. Note that this project needs to have a Git repository of its own in order for the command to work. Follow the steps below to run the command:

1. **Ensure your project is a Git repository:**
   - If your project is not already a Git repository, initialize it by running:
     ```sh
     git init
     ```

2. **Copy the SSH link of your Django application from its repository:**
   - Go to the repository of the Django application you want to add.
   - Copy the SSH link (it should look something like `git@github.com:username/repo.git`).

3. **Run the management command to add the submodule:**
   - Open your terminal and navigate to the root directory of your project where `manage.py` is located.
   - Run the following command, replacing `<insert ssh link>` with the SSH link you copied and `<app_name>` with the desired name for the Django app:
     ```sh
     python manage.py add_git_submodule <insert ssh link> <app_name>
     ```
   - If you want to specify a branch, use the `--branch` option:
     ```sh
     python manage.py add_git_submodule <insert ssh link> <app_name> --branch <branch_name>
     ```

4. **Run migrations and other setup tasks:**
   - Depending on the Django application, you may need to run migrations or other setup tasks. Refer to the application's documentation for specific instructions.
   - You also need to add the application to your `INSTALLED_APPS` in your `settings.py` file.

**Note:** The command decouples the Git submodule from its repository so it will act as an independent application.

By following these steps, you should be able to successfully add a Django application as a Git submodule to your project.

