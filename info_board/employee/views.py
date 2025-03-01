from info_board.employee.models import Employee
from info_board.employee.serializers import EmployeeContactSerializer
from rest_framework.generics import ListAPIView


class EmployeeListView(ListAPIView):
    serializer_class = EmployeeContactSerializer

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            queryset = Employee.find_by_query(query)
        else:
            queryset = Employee.objects.prefetch_related('contacts').all()
        return queryset
