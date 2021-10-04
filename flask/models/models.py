﻿from mongoengine import Document, StringField
from mongoengine.fields import DateTimeField

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
    lemma = StringField()
    prev_lemma = StringField()
    next_lemma = StringField()
    date_insert = DateTimeField()

    def __init__(self, lemma, date_insert, prev_lemma=None, next_lemma=None, *args, **kwargs):
        super(Lemma, self).__init__(*args, **kwargs)
        self.lemma = lemma
        self.prev_lemma = prev_lemma
        self.next_lemma = next_lemma
        self.date_insert = date_insert


    @property
    def serialize(self):
        return {
            "name": self.lemma,
            "prev_lemma": self.prev_lemma,
            "next_lemma": self.next_lemma,
            "date_insert": self.date_insert
        }