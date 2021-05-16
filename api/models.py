import mongoengine as me

class lemmasrae(me.Document):
    lemma = me.StringField(required=True)
    # source = me.StringField(require=True)
    # articles = me.ListField(me.StringField(), require=True)
    # articles = me.ListField(me.Document(), require=True)

class Crea(me.Document):
    lemma = me.StringField(required=True)
