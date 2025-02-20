from django.contrib import admin
from info_board.employee.models import Employee, Contact

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'patronymic', 'last_name']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['employee', 'contact_type']
