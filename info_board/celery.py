import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE','info_board.settings')
app = Celery('info_board')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'parse employee info': {
        'task': 'info_board.employee.tasks.parse_employee_info',
        'schedule': crontab(minute='0', hour='0', day_of_month='14,28')
    }
}
