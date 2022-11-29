FROM python:alpine

WORKDIR /usr/src/app

RUN apk add --no-cache --update curl-dev libressl-dev musl-dev gcc
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY auto-dns.py ./

ENV TIMEOUT 5
ENV MAIN_DOMAIN "oscarr.nl"
ENV REGEX_DOMAIN "k8s-[0-9]+\.oscarr\.nl"
ENV KUBERNETES_DOMAIN "kubernetes.oscarr.nl"
ENV TEST_DOMAIN "ninoo.nl"

CMD [ "python", "./auto-dns.py" ]
