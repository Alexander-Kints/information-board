from rest_framework.serializers import ModelSerializer, StringRelatedField
from info_board.schedule.models import StudentsGroup, ScheduleEntry, Faculty
from info_board.employee.serializers import EmployeeContactSerializer

class ScheduleEntrySerializer(ModelSerializer):
    employees = EmployeeContactSerializer(many=True, read_only=True)
    class Meta:
        model = ScheduleEntry
        exclude = ('id', 'students_group')


class GroupSerializer(ModelSerializer):
    faculty = StringRelatedField(read_only=True)
    class Meta:
        model = StudentsGroup
        fields = '__all__'


class GroupScheduleSerializer(GroupSerializer):
    schedule_entries = ScheduleEntrySerializer(many=True, read_only=True)


class FacultySerializer(ModelSerializer):
    class Meta:
        model = Faculty
        fields = '__all__'


class FacultyGroupSerializer(FacultySerializer):
    students_groups = GroupSerializer(many=True, read_only=True)
