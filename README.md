# Rest API implemented with Flask Builder

## Prerequisites

- Python 3

## Setup

1. Create the virtualenv using the Python 3
    ```bash
    mkvirtualenv -p python3 api-fb-doc
    ```
2. Enter to the virtual env
    ```bash
    workon api-fb-doc
    ```
3. Install dependencies
    ```bash
    pip install -r requirements.txt
   ```
4. Crete the local DB
    ```bash
    fabmanager create-db
   ```
5. Create the admin user
    ```bash
    fabmanager create-admin
   ```
6. Run the application
    ```bash
    fabmanager run
   ```
## Application
You could access to the application using the url http://localhost:8080/
The Swager API documentation is on http://localhost:8080/swagger/v1 and you can try out the api.


## Credits

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter)
