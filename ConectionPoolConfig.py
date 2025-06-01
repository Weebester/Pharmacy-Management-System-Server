#################################################Connections Pool########################################################

from tortoise import Tortoise
from tortoise.exceptions import ConfigurationError

# DataBaseConfiguration
# "host": "localhost",
# "user": "root",
# "password": "K423",
# "database": "pharmacy_2.0",

DBurl = "mysql://root:K423@localhost:3306/pharmacy_2.0?minsize=5&maxsize=10"


async def Open_MySQLDB():
    try:
        await Tortoise.init(
            db_url=DBurl,
            modules={"models": ["datamodels"]},
            _create_db=False,
        )
        print("SQLDB Connected Successfully")
    except ConfigurationError as x:
        print("configuration error")
        print(x)
        raise


async def Close_MySQLDB():
    await Tortoise.close_connections()
    print("SQLDB Closed Successfully")
