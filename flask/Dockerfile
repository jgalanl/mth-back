FROM python:3.7.2-stretch

RUN mkdir -p /app

WORKDIR /app

ADD . /app

RUN cd resources/babelnetpy && python setup.py install

RUN python -m spacy download es_core_news_md

RUN pip install -r requirements.txt

CMD ["uwsgi", "app.ini"]