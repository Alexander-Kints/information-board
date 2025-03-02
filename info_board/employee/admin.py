from django.contrib import admin

from info_board.employee.models import Contact, Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'first_name', 'patronymic', 'last_name', 'updated_at'
    ]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'contact_type']
