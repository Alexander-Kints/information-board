from django.db import models
from django.db.models import Q

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
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name='students_groups'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students_group'

    def __str__(self):
        return self.name

    @classmethod
    def find_by_query(cls, query: str):
        return cls.objects.filter(
            Q(name__icontains=query) |
            Q(faculty__short_name__icontains=query)
        ).order_by('name')


class Room(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        db_table = 'room'

    def __str__(self):
        return self.name

    @classmethod
    def find_by_query(cls, query: str):
        return cls.objects.filter(name__icontains=query)


class Subgroup(models.Model):
    number = models.IntegerField()
    group = models.ForeignKey(
        StudentsGroup, on_delete=models.CASCADE, related_name='subgroups'
    )

    class Meta:
        db_table = 'subgroup'

    def __str__(self):
        return str(self.number)


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
        FIRST = '09:00-10:30'
        SECOND = '10:45-12:15'
        THIRD = '13:15-14:45'
        FOURTH = '15:00-16:30'
        FIFTH = '16:45-18:15'
        SIXTH = '18:25-19:55'

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
        SIXTH = 6

    subject = models.CharField(max_length=256)
    day_of_week = models.CharField(max_length=32, choices=DaysOfWeek)
    type_of_week = models.CharField(max_length=32, choices=TypesOfWeek)
    study_time = models.CharField(max_length=32, choices=StudyTimes)
    subject_number = models.IntegerField(choices=SubjectNumbers)
    subject_type = models.CharField(
        max_length=32, choices=SubjectTypes, null=True, blank=True
    )
    subgroup = models.ForeignKey(
        Subgroup, on_delete=models.CASCADE, related_name='schedule_entries'
    )
    employees = models.ManyToManyField(
        Employee, related_name='schedule_entries', null=True, blank=True
    )
    room = models.ForeignKey(
        Room, on_delete=models.SET_NULL, related_name='schedule_entries',
        null=True, blank=True
    )

    class Meta:
        db_table = 'schedule_entry'

    @classmethod
    def format_study_time(cls, time_range: str) -> str | None:
        try:
            start_time, end_time = time_range.split('-')
            start_time = start_time.zfill(4)
            end_time = end_time.zfill(4)
            start_hour = int(start_time[:2])
            start_minute = int(start_time[2:])
            end_hour = int(end_time[:2])
            end_minute = int(end_time[2:])

            formatted_start_time = f"{start_hour:02}:{start_minute:02}"
            formatted_end_time = f"{end_hour:02}:{end_minute:02}"

            return f"{formatted_start_time}-{formatted_end_time}"

        except ValueError:
            return None

    @classmethod
    def time_to_number(cls, time_value):
        change_data = {
            cls.StudyTimes.FIRST: cls.SubjectNumbers.FIRST,
            cls.StudyTimes.SECOND: cls.SubjectNumbers.SECOND,
            cls.StudyTimes.THIRD: cls.SubjectNumbers.THIRD,
            cls.StudyTimes.FOURTH: cls.SubjectNumbers.FOURTH,
            cls.StudyTimes.FIFTH: cls.SubjectNumbers.FIFTH,
            cls.StudyTimes.SIXTH: cls.SubjectNumbers.SIXTH,
        }

        return change_data.get(time_value)

    @property
    def group_name(self):
        return self.subgroup.group.name
