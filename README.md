# django-switcher
Django script to switch/move to a new database.

Dump database to a json file is not a good option and this is lazy, so I had to write this script.

This script may stop for timeout, it depends on the size of your database. You can edit it to do it in stages, or save what has already been imported somewhere to continue with a new attempt.

First of all you have to set 2 databases on your setting file, in my case I was moving from Mysql to Postgresql:

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


In some cases I had problems setting the maximum id of the tables and I had to run this snippet separately

```python
for table in tables:
    with connections[ db_destination ].cursor() as cursor:
        try:
            cursor.execute( "select setval('" + table + "_id_seq', max(id)) from " + table )
        except:
            continue
```
