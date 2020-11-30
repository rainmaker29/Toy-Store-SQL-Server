import datetime
import mongoengine


def mongo_global_init():
    mongoengine.register_connection(alias='core', name='customers')




class UserDB_Obj(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    email = mongoengine.StringField(required=True)
    password = mongoengine.StringField(required=True)
    token = mongoengine.StringField(required=False)
    meta = {
        'db_alias': 'core',
        'collection': 'users'
    }

class SellerDB_Obj(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    email = mongoengine.StringField(required=True)
    password = mongoengine.StringField(required=True)
    token = mongoengine.StringField(required=False)
    meta = {
        'db_alias': 'core',
        'collection': 'sellers'
    }
