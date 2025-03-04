from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.generics import ListAPIView

from info_board.employee.models import Employee
from info_board.employee.serializers import EmployeeContactSerializer

@extend_schema(
    parameters=[
        OpenApiParameter(
            name='query',
            type=OpenApiTypes.STR,
            description='Запрос для поиска преподавателей',
            location=OpenApiParameter.QUERY,
            required=False
        )
    ]
)
class EmployeeListView(ListAPIView):
    serializer_class = EmployeeContactSerializer

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            queryset = Employee.find_by_query(query)
        else:
            queryset = Employee.objects.prefetch_related('contacts').all()
        return queryset
