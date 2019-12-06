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
* bundle exec rake test:unit
* bundle exec rake test:capybara

That will build the containers and do migration after postgres be running.