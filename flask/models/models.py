﻿from mongoengine import Document
from mongoengine.fields import DateTimeField, ListField, IntField, FloatField, StringField

from resources.clasificador import clasificador
from resources.worddictionarybabel import worddictionarybabel
from resources.worddictionary import worddictionary
from resources.lemma import lemma

class Config(object):
    def __init__(self):
        self.clasificadorobj = clasificador()
        
        self.unigrams = {}
        self.totalUnis = 1
        self.maxValue = 1
        
        self.bigrams = {}
        self.totalBis = 1

        self.trigrams = {}
        self.totalTris = 1

        # path = 'flask/resources/ngrams/vocab_cs.wngram'
        # self.unigrams = self.clasificadorobj.loadDic(path)
        # self.totalUnis = sum(self.unigrams.values())
        # self.maxValue = max(self.unigrams.values())
        # path = 'flask/resources/ngrams/2gm-0005.wngram'
        # self.bigrams = self.clasificadorobj.loadDic(path)
        # self.totalBis = sum(self.bigrams.values())
        # path = 'flask/resources/ngrams/3gm-0006.wngram'
        # self.trigrams = self.clasificadorobj.loadDic(path)
        # self.totalTris = sum(self.trigrams.values())

	    # DICCIONARIOE2R
        path = 'resources/stop_words/unigram2_non_stop_words.csv'
        self.uniE2R = self.clasificadorobj.loadDic3(path)
        self.uniE2R = {}

        # Diccionario babel
        self.diccionario_babel = worddictionarybabel()

        # Thesaurus
        self.dictionario_palabras=worddictionary()

        # Lematizador
        self.lematizador = lemma()

        # PPDB
        path = 'resources/dicuniwords.csv'
        self.diccionarioparafrases=self.clasificadorobj.loadDicuniparafrases2(path)


class Text(object):

    def __init__(self, original_text):
        self.original_text = original_text
        self.complex_words = []

    def check_word(self, word):
        for complex_word in self.complex_words:
            if complex_word.original_word == word:
                return True
        return False    

class Word(object):

    def __init__(self):
        self.synonyms = []
    
    def set_word(self, original_word, synonyms, definition_easy, definition_rae, pictogram):
        self.original_word = original_word
        self.synonyms = synonyms
        self.definition_easy = definition_easy
        self.definition_rae = definition_rae
        self.pictogram = pictogram

    def mostrar(self):
        print("Palabra compleja: "+ self.original_word)
        print("Sinónimos:")
        for synonym in self.synonyms:
            print(synonym)


class Lemma(Document):
    lemma = StringField(required=True)
    prev_lemma = StringField(required=False)
    next_lemma = StringField(required=False)
    date_insert = DateTimeField(required=True)
    source = StringField(required=False)
    femenine = StringField(required=False, null=True)
    references = StringField(required=False)
    articles = ListField(required=False)
    articles_facil = ListField(required=False)
    abs_freq = IntField(required=False)
    norm_freq = FloatField(required=False, null=True)
    pictos = ListField(required=False, null=True)


    def __init__(self, lemma, date_insert, prev_lemma='', next_lemma='', source='', femenine='', 
                    references='', articles=[], articles_facil=[], abs_freq='', norm_freq='', pictos=[], *args, **kwargs):
            super(Lemma, self).__init__(*args, **kwargs)
            self.lemma = lemma
            self.prev_lemma = prev_lemma
            self.next_lemma = next_lemma
            self.date_insert = date_insert
            self.source = source
            self.femenine = femenine
            self.references = references
            self.articles = articles
            self.articles_facil = articles_facil
            self.abs_freq = abs_freq
            self.norm_freq = norm_freq
            self.pictos = pictos

    def update(self, newdata):
        for key,value in newdata.items():
            setattr(self,key, value)
        self.save()

    @property
    def serialize(self):
        return {
            "lemma": self.lemma,
            "prev_lemma": self.prev_lemma,
            "next_lemma": self.next_lemma,
            "date_insert": self.date_insert,
            "source": self.source,
            "femenine": self.femenine,
            "references": self.references,
            "articles": self.articles,
            "articles_facil": self.articles_facil,
            "abs_freq": self.abs_freq,
            "norm_freq": self.norm_freq,
            "pictos": self.pictos
        }