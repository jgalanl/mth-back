FROM python:3.7.2-stretch

RUN mkdir -p /flask

WORKDIR /flask

ADD . /flask

# Spacy config
RUN pip install -U pip setuptools wheel &&\
    pip install -U spacy &&\
    python -m spacy download es_core_news_md

# Babelnet config
RUN cd resources/babelnetpy && python setup.py install

RUN pip install -r requirements.txt

CMD ["uwsgi", "app.ini"]