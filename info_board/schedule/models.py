from django.db import models

class Faculty(models.Model):
    short_name = models.CharField(max_length=64)

    class Meta:
        db_table = 'faculty'

    def __str__(self):
        return self.short_name


class StudentsGroup(models.Model):
    class CourseNumber(models.IntegerChoices):
        ONE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5
        SIX = 6

    name = models.CharField(max_length=64)
    course_number = models.IntegerField(choices=CourseNumber)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='students_groups')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students_group'

    def __str__(self):
        return self.name


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

    subject = models.CharField(max_length=256)
    day_of_week = models.CharField(max_length=32, choices=DaysOfWeek)
    type_of_week = models.CharField(max_length=32, choices=TypesOfWeek)
    study_time = models.CharField(max_length=32, choices=StudyTimes)
    students_group = models.ForeignKey(StudentsGroup, on_delete=models.CASCADE, related_name='schedule_entries')

    class Meta:
        db_table = 'schedule_entry'
