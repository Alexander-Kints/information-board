from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from info_board.schedule.models import StudentsGroup, ScheduleEntry, Faculty
from info_board.schedule.serializers import GroupScheduleSerializer, FacultySerializer, FacultyGroupSerializer
from rest_framework.response import Response
from django.db.models import Prefetch
from django.db.models import Q

class GroupScheduleView(APIView):
    serializer_class = GroupScheduleSerializer
    def get(self, request, group_id):
        type_of_week = request.GET.get('week')
        choices = [el[0] for el in ScheduleEntry.TypesOfWeek.choices]

        if type_of_week and type_of_week in choices:
            group = StudentsGroup.objects.filter(pk=group_id).prefetch_related(
                Prefetch(
                    'schedule_entries',
                    queryset=ScheduleEntry.objects.filter(
                        Q(type_of_week=type_of_week) |
                        Q(type_of_week=ScheduleEntry.TypesOfWeek.ALWAYS)
                    )
                )
            ).first()
        else:
            group = StudentsGroup.objects.filter(pk=group_id).prefetch_related('schedule_entries').first()

        if not group:
            return Response(
                {'message': f'group {group_id} does not exist'},
                status=404
            )

        serializer = self.serializer_class(instance=group)
        return Response(serializer.data)


class FacultyListView(ListAPIView):
    serializer_class = FacultySerializer
    queryset = Faculty.objects.all()


class FacultyGroupListView(ListAPIView):
    serializer_class = FacultyGroupSerializer
    queryset = Faculty.objects.prefetch_related('students_groups').all()


class FacultyGroupView(APIView):
    serializer_class = FacultyGroupSerializer

    def get(self, request, faculty_id):
        course_number = request.GET.get('course')

        if course_number and int(course_number) in range(1, 6):
            faculty_groups = Faculty.objects.filter(pk=faculty_id).prefetch_related(
                Prefetch(
                    'students_groups',
                    queryset=StudentsGroup.objects.filter(
                        course_number=course_number
                    )
                )
            ).first()
        else:
            faculty_groups = Faculty.objects.filter(pk=faculty_id).prefetch_related(
                'students_groups'
            ).first()

        if not faculty_groups:
            return Response(
                {'message': f'faculty {faculty_id} does not exist'},
                status=404
            )

        serializer = self.serializer_class(instance=faculty_groups)
        return Response(serializer.data)
