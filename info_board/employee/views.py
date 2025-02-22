from info_board.employee.models import Employee
from info_board.employee.serializers import EmployeeSerializer
from rest_framework.generics import ListAPIView


class EmployeeListAPIView(ListAPIView):
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            queryset = Employee.find_by_query(query)
        else:
            queryset = Employee.objects.prefetch_related('contacts').all()
        return queryset
