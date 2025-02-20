from rest_framework.generics import ListAPIView
from django.db.models import Q
from info_board.employee.models import Employee
from info_board.employee.serializers import EmployeeSerializer

class EmployeeListAPIView(ListAPIView):
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            queryset = Employee.objects.filter(
                Q(first_name__icontains=query) |
                Q(patronymic__icontains=query) |
                Q(last_name__icontains=query) |
                Q(academic_degree__icontains=query) |
                Q(academic_status__icontains=query)
            ).prefetch_related('contacts')
        else:
            queryset = Employee.objects.prefetch_related('contacts').all()

        return queryset
