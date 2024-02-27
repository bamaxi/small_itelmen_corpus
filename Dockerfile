# syntax=docker/dockerfile-upstream:master
FROM python:3.11-slim

COPY requirements.txt requirements.txt

# RUN pip3 install --no-cache-dir --upgrade pip -r requirements.txt
RUN pip3 install --upgrade pip -r requirements.txt


COPY app app
COPY migrations migrations
COPY config.py run.py start_db.py ./
# COPY app.db app.db

COPY texts texts 

ARG PORT=5000
EXPOSE ${PORT}

# RUN python -m start_db
RUN python -m start_db add --folder "texts/"
RUN python -m pip freeze
CMD flask run --host 0.0.0.0 -p 5000