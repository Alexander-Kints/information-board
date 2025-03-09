from django.db.models import Prefetch, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.serializers import CharField

import info_board.schedule.serializers as serializers
from info_board.employee.models import Employee
from info_board.schedule.models import (Faculty, Room, ScheduleEntry,
                                        StudentsGroup, Subgroup)


class GroupScheduleView(APIView):
    serializer_class = serializers.GroupScheduleSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='week',
                type=OpenApiTypes.STR,
                description='Четность недели: even, odd',
                location=OpenApiParameter.QUERY,
                required=False
            )
        ]
    )
    def get(self, request, group_id):
        type_of_week = request.GET.get('week')
        choices = [el[0] for el in ScheduleEntry.TypesOfWeek.choices]

        if not type_of_week or type_of_week not in choices:
            type_of_week = ScheduleEntry.week_type_now()

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

        if not group:
            return Response(
                {'message': f'group {group_id} does not exist'},
                status=404
            )

        serializer = self.serializer_class(instance=group)
        return Response(serializer.data)


class FacultyListView(ListAPIView):
    serializer_class = serializers.FacultySerializer
    queryset = Faculty.objects.all()


class FacultyGroupListView(ListAPIView):
    serializer_class = serializers.FacultyGroupSerializer
    queryset = Faculty.objects.prefetch_related('students_groups').all()


class FacultyGroupView(APIView):
    serializer_class = serializers.FacultyGroupSerializer

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
    serializer_class = serializers.EmployeeScheduleSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='week',
                type=OpenApiTypes.STR,
                description='Четность недели: even, odd',
                location=OpenApiParameter.QUERY,
                required=False
            )
        ]
    )
    def get(self, request, employee_id):
        type_of_week = request.GET.get('week')
        choices = [el[0] for el in ScheduleEntry.TypesOfWeek.choices]

        if not type_of_week or type_of_week not in choices:
            type_of_week = ScheduleEntry.week_type_now()

        employee = Employee.objects.filter(
            id=employee_id
        ).prefetch_related(
            Prefetch(
                'schedule_entries',
                queryset=ScheduleEntry.objects.filter(
                    Q(type_of_week=type_of_week) |
                    Q(type_of_week=ScheduleEntry.TypesOfWeek.ALWAYS)
                )
            )
        ).first()

        if not employee:
            return Response(
                {'message': 'schedule does not exist'},
                status=404
            )

        serializer = self.serializer_class(instance=employee)
        return Response(serializer.data)


class SearchScheduleView(APIView):
    serializer_class = serializers.SearchSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='query',
                type=OpenApiTypes.STR,
                description='Поиск групп, преподавателей, аудиторий',
                location=OpenApiParameter.QUERY,
                required=True
            )
        ]
    )
    def get(self, request):
        query = request.GET.get('query')

        if not query:
            return Response({})

        data = dict()

        groups = StudentsGroup.find_by_query(query)
        if groups:
            data['groups'] = [
                serializers.GroupSerializer(instance=group).data
                for group in groups
            ]

        employees = Employee.find_by_query(query)
        if employees:
            data['employees'] = list(employees.values())

        rooms = Room.find_by_query(query)
        if rooms:
            data['rooms'] = list(rooms.values())

        return Response(data)


class WeekTypeView(APIView):
    @extend_schema(
        description='Четность текущей недели',
        responses={
            200: inline_serializer(
                name='WeekType',
                fields={
                    'week': CharField()
                }
            )
        }
    )
    def get(self, request):
        return Response({
                "week": ScheduleEntry.week_type_now()
        })
