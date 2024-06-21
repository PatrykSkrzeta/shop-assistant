from flask import Flask
from mongoengine import connect

app = Flask(__name__)

# Połącz się z bazą danych MongoDB
connect('shopassistant')

# Usuń wszystkie indeksy z kolekcji `product`
from mongoengine.connection import get_db

db = get_db()
db.product.drop_indexes()

print("All indexes except _id have been dropped.")