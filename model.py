import os
from peewee import *

db = SqliteDatabase("bot.db")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class LastRequest(Model):
    data = CharField()
    time = DateTimeField()

    class Meta:
        database = db


def create_db(new_data, new_time):
    LastRequest.create_table()
    field = LastRequest(data=new_data, time=new_time)
    field.save()
    db.close()


def update_db(new_data, new_time):
    field = (LastRequest.update(data=new_data,
                                time=new_time).where(LastRequest.id == 1))
    field.execute()
