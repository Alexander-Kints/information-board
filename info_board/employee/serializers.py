from info_board.employee.models import Contact, Employee
from rest_framework.serializers import ModelSerializer

class EmployeeSerializer(ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class ContactSerializer(ModelSerializer):
    class Meta:
        model = Contact
        fields = ('contact_type', 'value')


class EmployeeContactSerializer(EmployeeSerializer):
    contacts = ContactSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'
