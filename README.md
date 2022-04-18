# django-switcher
Django script to switch/move to a new database

First of all you have to set 2 databases on your setting file:

```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': os.environ['RDS_DATABASE'],
           'USER': os.environ['RDS_USER'],
           'PASSWORD': os.environ['RDS_PASSWORD'],
           'HOST': os.environ['RDS_HOST'],
           'PORT': '3306',
           'init_command': "SET sql_mode='STRICT_ALL_TABLES'",
       },
       'postgresql': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': os.environ['RDS_PG_DATABASE'],
           'USER': os.environ['RDS_PG_USER'],
           'PASSWORD': os.environ['RDS_PG_PASSWORD'],
           'HOST': os.environ['RDS_PG_HOST'],
           'PORT': os.environ['RDS_PG_PORT'],
       }
   }
```

After this you need to edit **dbmove.py** file 

```python
db_origin = 'default'
db_destination = 'postgresql'
```

Copy **dbmove.py** on a **management** path on your project and run:

```
python manage.py dbmove
```
