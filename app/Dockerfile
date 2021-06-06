FROM python:3.6.8-alpine3.9

LABEL MAINTAINER="FirstName LastName <example@domain.com>"

ENV GROUP_ID=1000 \
    USER_ID=1000

WORKDIR /var/www/

ADD . /var/www/
RUN apk add --no-cache build-base libffi-dev openssl-dev ncurses-dev
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

RUN addgroup -g $GROUP_ID www
RUN adduser -D -u $USER_ID -G www www -s /bin/sh

USER www

EXPOSE 5000

CMD [ "gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "wsgi:app"]