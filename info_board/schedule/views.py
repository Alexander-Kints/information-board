from django.db.models import Prefetch, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from info_board.employee.models import Employee
from info_board.schedule.models import (Faculty, ScheduleEntry, StudentsGroup,
                                        Subgroup)
from info_board.schedule.serializers import (FacultyGroupSerializer,
                                             FacultySerializer,
                                             GroupScheduleSerializer,
                                             EmployeeScheduleSerializer)


class GroupScheduleView(APIView):
    serializer_class = GroupScheduleSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='week',
                type=OpenApiTypes.STR,
                description='Четность недели: even, odd, now(в разработке)',
                location=OpenApiParameter.QUERY,
                required=False
            )
        ]
    )
    def get(self, request, group_id):
        type_of_week = request.GET.get('week')
        choices = [el[0] for el in ScheduleEntry.TypesOfWeek.choices]

        if type_of_week and type_of_week in choices:
            group = StudentsGroup.objects.filter(pk=group_id).prefetch_related(
                Prefetch(
                    'subgroups',
                    queryset=Subgroup.objects.prefetch_related(
                        Prefetch(
                            'schedule_entries',
                            queryset=ScheduleEntry.objects.filter(
                                Q(type_of_week=type_of_week) |
                                Q(type_of_week=ScheduleEntry.TypesOfWeek.ALWAYS)
                            )
                        )
                    )
                )
            ).first()
        else:
            group = StudentsGroup.objects.filter(
                pk=group_id
            ).prefetch_related('subgroups').first()

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='course',
                type=OpenApiTypes.INT,
                description='Номер курса',
                location=OpenApiParameter.QUERY,
                required=False
            )
        ]
    )
    def get(self, request, faculty_id):
        course_number = request.GET.get('course')

        if course_number and int(course_number) in range(1, 6):
            faculty_groups = Faculty.objects.filter(
                pk=faculty_id
            ).prefetch_related(
                Prefetch(
                    'students_groups',
                    queryset=StudentsGroup.objects.filter(
                        course_number=course_number
                    )
                )
            ).first()
        else:
            faculty_groups = Faculty.objects.filter(
                pk=faculty_id
            ).prefetch_related(
                'students_groups'
            ).first()

        if not faculty_groups:
            return Response(
                {'message': f'faculty {faculty_id} does not exist'},
                status=404
            )

        serializer = self.serializer_class(instance=faculty_groups)
        return Response(serializer.data)


class EmployeeScheduleView(APIView):
    serializer_class = EmployeeScheduleSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='week',
                type=OpenApiTypes.STR,
                description='Четность недели: even, odd, now(в разработке)',
                location=OpenApiParameter.QUERY,
                required=False
            )
        ]
    )
    def get(self, request, employee_id):
        type_of_week = request.GET.get('week')
        choices = [el[0] for el in ScheduleEntry.TypesOfWeek.choices]

        if type_of_week and type_of_week in choices:
            employee = Employee.objects.filter(id=employee_id).prefetch_related(
                Prefetch(
                    'schedule_entries',
                    queryset=ScheduleEntry.objects.filter(
                        Q(type_of_week=type_of_week) |
                        Q(type_of_week=ScheduleEntry.TypesOfWeek.ALWAYS)
                    )
                )
            ).first()
        else:
            employee = Employee.objects.filter(id=employee_id).prefetch_related(
                'schedule_entries'
            ).first()

        if not employee:
            return Response(
                {'message': f'schedule does not exist'},
                status=404
            )

        serializer = self.serializer_class(instance=employee)

        return Response(serializer.data)
