import unittest
import json
from http import HTTPStatus

from mongo import app

class FlaskTestCase(unittest.TestCase):

    def test_index(self):
        tester = app.test_client(self)        
        response = tester.get('/')
        statuscode = response.status_code
        self.assertEqual(statuscode, HTTPStatus.OK)
        self.assertEqual(response.content_type, 'application/json')


    def test_complex_words(self):
        tester = app.test_client(self)        
        response = tester.get('/api/complex-word')
        statuscode = response.status_code
        self.assertEqual(statuscode, HTTPStatus.OK)
        self.assertEqual(response.content_type, 'application/json')


    def test_disambiguate(self):
        tester = app.test_client(self)        
        response = tester.get('/api/disambiguate')
        statuscode = response.status_code
        self.assertEqual(statuscode, HTTPStatus.OK)
        self.assertEqual(response.content_type, 'application/json')


    def test_synonyms(self):
        tester = app.test_client(self)        
        response = tester.get('/api/synonyms')
        statuscode = response.status_code
        self.assertEqual(statuscode, HTTPStatus.OK)
        self.assertEqual(response.content_type, 'application/json')


    def test_lemmatize(self):
        tester = app.test_client(self)        
        response = tester.get('/api/lemmatize')
        statuscode = response.status_code
        self.assertEqual(statuscode, HTTPStatus.OK)
        self.assertEqual(response.content_type, 'application/json')


    def test_lemmas_get(self):
        tester = app.test_client(self)        
        response = tester.get('/api/lemmas')
        statuscode = response.status_code
        self.assertEqual(statuscode, HTTPStatus.OK)
        self.assertEqual(response.content_type, 'application/json')


    def test_lemmas_get(self):
        tester = app.test_client(self)        
        response = tester.get('/api/lemmas/a')
        statuscode = response.status_code
        self.assertEqual(statuscode, HTTPStatus.OK)
        self.assertEqual(response.content_type, 'application/json')


    def test_lemmas_post(self):
        tester = app.test_client(self)        
        response = tester.post('/api/lemmas',data=json.dumps({"lemma": "a"}))
        statuscode = response.status_code
        self.assertEqual(statuscode, HTTPStatus.OK)
        self.assertEqual(response.content_type, 'application/json')


if __name__ == '__main__':
    unittest.main()