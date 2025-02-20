from django.db import models
from django.contrib.postgres.fields import ArrayField

class Employee(models.Model):
    first_name = models.CharField(max_length=64)
    patronymic = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    academic_degree = models.CharField(max_length=64, null=True, blank=True)
    academic_status = models.CharField(max_length=64, null=True, blank=True)
    current_positions = ArrayField(models.CharField(max_length=128), null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee'


class Contact(models.Model):
    class ContactType(models.Choices):
        PHONE = 'Phone'
        EMAIL = 'Email'
        ADDRESS = 'Address'

    contact_type = models.CharField(max_length=64, choices=ContactType)
    value = models.CharField(max_length=256)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='contacts')

    class Meta:
        db_table = 'contact'
