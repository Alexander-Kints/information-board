from django.contrib.postgres.fields import ArrayField
from django.db import models


class Employee(models.Model):
    first_name = models.CharField(max_length=64)
    patronymic = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64)
    academic_degree = models.CharField(max_length=64, null=True, blank=True)
    academic_status = models.CharField(max_length=64, null=True, blank=True)
    current_positions = ArrayField(
        models.CharField(max_length=256), null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    photo = models.CharField(max_length=256)

    class Meta:
        db_table = 'employee'

    def __str__(self):
        return '{} {} {}'.format(
            self.first_name,
            self.patronymic if self.patronymic else '',
            self.last_name
        )

    @classmethod
    def find_by_query(cls, query: str) -> models.QuerySet:
        queryset = cls.objects.filter(
            models.Q(first_name__icontains=query) |
            models.Q(patronymic__icontains=query) |
            models.Q(last_name__icontains=query) |
            models.Q(academic_degree__icontains=query) |
            models.Q(academic_status__icontains=query)
        ).prefetch_related('contacts')

        return queryset


class Contact(models.Model):
    class ContactType(models.TextChoices):
        PHONE = 'Phone'
        EMAIL = 'Email'
        ADDRESS = 'Address'

    contact_type = models.CharField(max_length=64, choices=ContactType)
    value = models.CharField(max_length=256)
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='contacts'
    )

    class Meta:
        db_table = 'contact'
