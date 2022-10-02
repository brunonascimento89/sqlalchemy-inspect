# sqlalchemy-inspect

Get your database schema into your SQLAlchemy model

## First steps:

    1. virtualenv venv (recomended)
        a. venv/Scripts/activate (windows) or source venv/bin/activate (linux)
    2. pip install -r requirements.txt
    3. configure database connections into .env file

## Examples of How To Use sqlalchemy-inspect

Creating a SQLAlchemy model

```python
from sqlalchemy_inspect import database
from decouple import config

conn = database.MySQL(
        host=config('DB_HOST'),
        port=config('DB_PORT'),
        database=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASS')
    )
conn.extract_model(filename='test_abc.py', engine_args=True)
```

Configuring .env file

```python
DB_NAME=db_name
DB_USER=db_user
DB_PASS=db_pass
DB_HOST=db_host
DB_PORT=db_port
```

Developed by Bruno Nascimento (c) 2022