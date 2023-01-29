from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb_serialization.serializers import DateTimeSerializer
from tinydb_serialization import SerializationMiddleware

serialization = SerializationMiddleware(JSONStorage)
serialization.register_serializer(DateTimeSerializer(), "TinyDate")

mock_db = TinyDB("./data/test_db.json", storage=serialization)

mock_users = mock_db.table("users")
mock_payments = mock_db.table("payments")
mock_promocodes = mock_db.table("promocodes")
