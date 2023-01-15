import contextlib
from tinydb import TinyDB
from tinydb.storages import JSONStorage
from datetime import datetime
from tinydb_serialization.serializers import DateTimeSerializer
from tinydb_serialization import SerializationMiddleware

serialization = SerializationMiddleware(JSONStorage)
serialization.register_serializer(DateTimeSerializer(), "TinyDate")

db = TinyDB("./data/db.json", storage=serialization)

users = db.table("users")
payments = db.table("payments")
promocodes = db.table("promocodes")
