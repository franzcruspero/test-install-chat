# Django Chat Blueprint

The **Django Chat Blueprint** is a chat messaging Django application built using **Django Channels**. This simple app supports:
- **1-to-1 messaging**
- **Group chats**
- **File and image attachments**

## Installation

### Prerequisites

Ensure you have the following libraries installed in your main Django project:
1. Django Channels
2. Daphne
3. Channels Redis

To install the following libraries, input the following commands in your terminal
   ```sh
   uv add 'channels[daphne]' channels-redis
   ```

Add `daphne` at the start of your INSTALLED_APPS before all other applications

   ```python
      INSTALLED_APPS = [
         "daphne",
         ...,
      ]
   ```

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

## Note: The command decouples the git submodule from its repository so it will act as an independent application

5. **Add chat to Installed Applications.**
   - Add `chat` to your `INSTALLED_APPS` in `settings.py`

6. **Update ASGI Configuration**
   - Remove the WSGI_APPLICATION line and add the following line:

    `ASGI_APPLICATION = "chat.asgi.application`

   Example:
    ```python
      # settings.py
      # Remove this line
      # WSGI_APPLICATION = "mugna203.wsgi.application"

      # Add this line
      ASGI_APPLICATION = "chat.asgi.application"
    ```

7. **Add Channel layers to settings**
   - Add the following line in your settings.py file
   
   ```python
      # Channel Layers
      CHANNEL_LAYERS = {
         "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                  "hosts": [
                     (env.str("REDIS_HOST", "127.0.0.1"), env.int("REDIS_PORT", 6379))
                  ],
                  "prefix": "channels",  # Use a prefix to avoid conflicts
            },
         },
      }
   ```

8. **Add the Chat URLs to Your Main Project's URL Configuration**
   - Open your main project's `urls.py` file.
   - Add the following import at the top of the file (if they're not imported yet else ignore this):
     ```python
     from django.urls import path, include
     ```
   - Add the chat application's URLs to your project's URL patterns:
     ```python
     urlpatterns = [
         # ...existing url patterns...
         path("chat/", include("chat.api.v1.urls", namespace="chat")),
     ]
     ```
    

## Running the application locally

Once you've successfully installed and setup the application, you can run it by inputting the following command to your terminal:    
`python manage.py runserver`

##### NOTE: this assumes you added `daphne` at the start of your INSTALLED_APPS before all other applications
