from rest_framework.serializers import ModelSerializer, StringRelatedField

from info_board.employee.models import Employee
from info_board.schedule.models import (Faculty, ScheduleEntry, StudentsGroup,
                                        Subgroup)


class EmployeeSerializer(ModelSerializer):
    class Meta:
        model = Employee
        exclude = ('current_positions', 'updated_at')


class ScheduleEntrySerializer(ModelSerializer):
    employees = EmployeeSerializer(many=True, read_only=True)
    room = StringRelatedField(read_only=True)

    class Meta:
        model = ScheduleEntry
        exclude = ('id', 'subgroup')


class SubgroupSerializer(ModelSerializer):
    class Meta:
        model = Subgroup
        exclude = ('id',)


class SubgroupScheduleSerializer(SubgroupSerializer):
    schedule_entries = ScheduleEntrySerializer(many=True, read_only=True)


class GroupSerializer(ModelSerializer):
    faculty = StringRelatedField(read_only=True)

    class Meta:
        model = StudentsGroup
        fields = '__all__'


class GroupScheduleSerializer(GroupSerializer):
    subgroups = SubgroupScheduleSerializer(many=True, read_only=True)


class FacultySerializer(ModelSerializer):
    class Meta:
        model = Faculty
        fields = '__all__'


class FacultyGroupSerializer(FacultySerializer):
    students_groups = GroupSerializer(many=True, read_only=True)
