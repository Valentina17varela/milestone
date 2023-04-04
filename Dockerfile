FROM    public.ecr.aws/d4f9u1m2/python:3.8-alpine3.14

WORKDIR /srv/milestone-service

COPY    ./requirements.txt .

RUN     \
        apk add --no-cache postgresql-libs libstdc++ bash && \
        apk add --no-cache --virtual .build-deps linux-headers make gcc musl-dev postgresql-dev git g++ && \
        python3 -m pip install -r requirements.txt --no-cache-dir && \
        apk --purge del .build-deps

COPY api ./api
COPY ./tests/ ./tests
COPY ./config.py ./config.py

CMD     ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
