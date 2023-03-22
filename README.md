# QA api Assessment 

Django Api



 
The project is hosted at [this Heroku App](https://qa-test.avenuecode.com/).<br>
The project is build [Jenkins](https://jenkins.avenuecode.com/job/QA-TEST/). 
## Main gems/libraries used ##

* [Django](https://www.djangoproject.com/)
* [psycopg2](https://pypi.org/project/psycopg2/)
* [djangorestframework](https://www.django-rest-framework.org/)

## Contributing ##

Any help is encouraged. Here are some ways you can contribute:

* by using it
* by telling people
* by reporting bugs or suggesting new features on github issue tracker
* by fixing bugs or implementing features

## Documentation ##

The api documentation was generated using drf_yasg library. There are four endpoints available for viewing the documentation: 
* /redoc/ - Redoc UI  
* /swagger/ - Swagger UI
* /swagger.json
* /swagger.yaml

## Maintenance ##

Running in containers;

There is 2 containers; postgres, api.

<b>Running:</b>
* docker-compose up api_db
* docker-compose up qaapit_app

That will be running two containers.

<b>New envi:</b><br>
It's required to create manually your local database
* docker-compose build
* docker-compose up api_db
* connect into the database and create table

the config of local variables is:

        'NAME': 'todo_avenue_development',
        'USER': os.environ.get('TODO_AVENUE_DATABASE_USER'),
        'PASSWORD': os.environ.get('TODO_AVENUE_DATABASE_PASSWORD'),
        'HOST': os.environ.get('TODO_AVENUE_DATABASE_SERVER_NAME'),
        'PORT': os.environ.get('TODO_AVENUE_DATABASE_SERVER_PORT')

<b>Run tests:</b>
* python manage.py test

That will build the containers and do migration after postgres be running.

<b>Apply migrations:</b>

If you are running the application through Docker, here's how you can apply any new migrations to the project:

1. First, make sure all containers are down. Go to the project folder and run:
    ```console
    $ docker-compose down
    ```
2. Now, build the application container:
    ```console
    $ docker-compose build qaapit_app
    ```
3. After that, run the container:
    ```console
    $ docker-compose up qaapit_app
    ```
4. Finally, you can access the container and run your migrations. To do so, run `docker ps` to check the container ID and change it accordingly when running the following command:
    ```console
    $ docker ps 
    CONTAINER ID        IMAGE                    COMMAND                  CREATED             STATUS              PORTS                    NAMES
    fefff84edd9b        qa-test-api_qaapit_app   "bash -c 'python man…"   7 seconds ago       Up 5 seconds        0.0.0.0:8000->8000/tcp   qaapi_app
    1bab273ebc1a        postgres                 "docker-entrypoint.s…"   8 seconds ago       Up 7 seconds        0.0.0.0:5432->5432/tcp   qa-test-api_api_db_1
    $ docker exec -it fefff84edd9b /bin/bash                                                                                                                        develop
    root@fefff84edd9b:/qaapitest# python manage.py migrate
    ```