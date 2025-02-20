from rest_framework.serializers import ModelSerializer
from info_board.employee.models import Employee, Contact

class ContactSerializer(ModelSerializer):
    class Meta:
        model = Contact
        fields = ('contact_type', 'value')


class EmployeeSerializer(ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'
