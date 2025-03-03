FROM python:3.12-slim

WORKDIR /app/
COPY . /app/
ENV PYTHONUNBUFFERED=1
RUN pip install -r requirements.txt

CMD python manage.py makemigrations \
    && python manage.py migrate \
    && python manage.py runserver 0.0.0.0:8000
