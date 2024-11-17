import datetime

from peewee import *

db = SqliteDatabase("database.db")


class BaseModel(Model):
    DoesNotExist: Exception

    class Meta:
        database = db
        orm_mode = True


class Product(BaseModel):
    id: int = AutoField()
    title = CharField()
    cost = IntegerField()
    description = TextField()


class Order(BaseModel):
    id = AutoField()
    user_id = CharField()
    created_at = DateTimeField(default=datetime.datetime.now)


class OrderItem(BaseModel):
    id = AutoField()
    product = ForeignKeyField(Product, backref="order_items", on_delete="CASCADE")
    order = ForeignKeyField(Order, backref="order_items", on_delete="CASCADE")
    cost = IntegerField()
    count = IntegerField()


db.connect()
db.create_tables([Product, Order, OrderItem])
