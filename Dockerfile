FROM python:alpine AS build-image

RUN apk add --no-cache --update curl-dev musl-dev gcc
COPY requirements.txt ./

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

FROM python:alpine
RUN apk add --no-cache --update curl
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=build-image /opt/venv /opt/venv
COPY auto-dns.py ./

ENV TIMEOUT 5
ENV MAIN_DOMAIN "oscarr.nl"
ENV REGEX_DOMAIN "k8s-[0-9]+\.oscarr\.nl"
ENV KUBERNETES_DOMAIN "kubernetes.oscarr.nl"
ENV TEST_DOMAIN "ninoo.nl"

USER nobody
CMD [ "python", "auto-dns.py" ]
