from django.db import models
from info_board.employee.models import Employee

class Faculty(models.Model):
    short_name = models.CharField(max_length=64)

    class Meta:
        db_table = 'faculty'

    def __str__(self):
        return self.short_name


class StudentsGroup(models.Model):
    class CourseNumbers(models.IntegerChoices):
        ONE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5
        SIX = 6

    name = models.CharField(max_length=64)
    course_number = models.IntegerField(choices=CourseNumbers)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='students_groups')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students_group'

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        db_table = 'room'

    def __str__(self):
        return self.name


class Subgroup(models.Model):
    number = models.IntegerField()
    group = models.ForeignKey(StudentsGroup, on_delete=models.CASCADE, related_name='subgroups')

    class Meta:
        db_table = 'subgroup'

    def __str__(self):
        return self.number

class ScheduleEntry(models.Model):
    class DaysOfWeek(models.TextChoices):
        MONDAY = 'понедельник'
        TUESDAY = 'вторник'
        WEDNESDAY = 'среда'
        THURSDAY = 'четверг'
        FRIDAY = 'пятница'
        SATURDAY = 'суббота'
        SUNDAY = 'воскресенье'

    class TypesOfWeek(models.TextChoices):
        ODD = 'odd'
        EVEN = 'even'
        ALWAYS = 'always'

    class StudyTimes(models.TextChoices):
        FIRST = '900-1030'
        SECOND = '1045-1215'
        THIRD = '1315-1445'
        FOURTH = '1500-1630'
        FIFTH = '1645-1815'

    class SubjectTypes(models.TextChoices):
        LAB = 'Лабораторные занятия'
        PRACT = 'Практические занятия'
        LECT = 'Лекция'

    class SubjectNumbers(models.IntegerChoices):
        FIRST = 1
        SECOND = 2
        THIRD = 3
        FOURTH = 4
        FIFTH = 5

    subject = models.CharField(max_length=256)
    day_of_week = models.CharField(max_length=32, choices=DaysOfWeek)
    type_of_week = models.CharField(max_length=32, choices=TypesOfWeek)
    study_time = models.CharField(max_length=32, choices=StudyTimes)
    subject_number = models.IntegerField(choices=SubjectNumbers)
    subject_type = models.CharField(max_length=32, choices=SubjectTypes, null=True, blank=True)
    subgroup = models.ForeignKey(Subgroup, on_delete=models.CASCADE, related_name='schedule_entries')
    employees = models.ManyToManyField(Employee, related_name='schedule_entries', null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, related_name='schedule_entries', null=True, blank=True)

    class Meta:
        db_table = 'schedule_entry'
