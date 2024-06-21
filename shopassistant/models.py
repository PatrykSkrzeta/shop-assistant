from mongoengine import Document, StringField, IntField, FloatField, DateTimeField, connect
from flask_login import UserMixin
from datetime import *



class User(UserMixin, Document):
    email = StringField(required=True, unique=True)
    password = StringField(required=True)

    def get_id(self):
        return self.email


class Product(Document):
    name = StringField(required=True, unique=True)
    category = StringField(required=True)
    type = StringField(required=True)
    date_added = DateTimeField(default=lambda: datetime.now(timezone.utc))
    value = IntField(required=True)
    price = FloatField(required=True)

class Order(Document):
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    address = StringField(required=True)
    date_added = DateTimeField(default=lambda: datetime.now(timezone.utc))
    pesel = StringField(required=True)
    contact = StringField(required=True)
    product_name = StringField(required=True)
    total = IntField(required=True)
    quantity = IntField(required=True)
    discount = FloatField(default=0)





