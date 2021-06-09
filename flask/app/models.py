from mongoengine import Document
from mongoengine import DateTimeField, StringField, ReferenceField, ListField

class lemmasrae(Document):
    lemma = StringField(required=True)
    # source = me.StringField(require=True)
    # articles = me.ListField(me.StringField(), require=True)
    # articles = me.ListField(me.Document(), require=True)

class Crea(Document):
    lemma = StringField(required=True)

