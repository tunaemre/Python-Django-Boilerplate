A boilerplate project written in Python and built using Django, Django REST Framework, Celery and common packages.
Auth0 used for authentication purposes.

Run the following command to start project:
    
    python manage.py runserver

## Migrations
Before starting the project, make sure your development DB is up-to-date. 
Run the following command in the root folder:

    python manage.py migrate

If you make a change that requires a DB schema update, create a migration:

    python manage.py makemigrations

If you want to create an empty revision file, create with this command:

    python manage.py makemigrations <app_name> --empty --name <migration_name>

If you want to downgrade to a specific revision of a migration:

    python manage.py migrate <app_name> <revision_id>

## Tests
Before running tests, a `test.env` file must be created in the env folder.
To run tests, run the following command in the root folder:
    
    python manage.py test --verbosity 2 --failfast

The test suite automatically creates a test database, runs migrations and drops it when finished.
If to prevent drop the test database after finish, add following argument into the command:

    --keepdb

## OpenAPI
After running project, visit to access Swagger UI and OpenAPI schemes:

    http(s)://<domain>/swagger/
    http(s)://<domain>/swagger.json
    http(s)://<domain>/swagger.yaml

Visit to discover OpenAPI specifications:

    http(s)://<domain>/redoc/
