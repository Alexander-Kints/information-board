from django.contrib import admin

from info_board.schedule.models import Faculty, ScheduleEntry, StudentsGroup


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['id', 'short_name']


@admin.register(StudentsGroup)
class StudentsGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'course_number', 'faculty', 'updated_at']


@admin.register(ScheduleEntry)
class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'day_of_week', 'type_of_week', 'subject']
