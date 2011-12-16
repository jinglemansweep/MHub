from mongoengine import *

class Item(Document):

    name = StringField(required=True, help_text="Name")
    value = StringField(help_text="Value")
 

class StoreItem(Item):
    
   meta = {"collection": "store"}


class StateItem(Item):

    meta = {"collection": "state"}


class Resource(StoreItem):

    item_type  = StringField(required=True, help_text="Type", default="resource") 
    item_class = StringField(help_text="Class")
    mimetype = StringField(help_text="MIME Type", default="text/plain")
    description = StringField(help_text="Description")
    

