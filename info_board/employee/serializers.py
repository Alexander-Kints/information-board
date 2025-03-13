from rest_framework.serializers import ModelSerializer

from info_board.employee.models import Contact, Employee


class EmployeeSerializer(ModelSerializer):
    class Meta:
        model = Employee
        exclude = ('updated_at',)


class ContactSerializer(ModelSerializer):
    class Meta:
        model = Contact
        fields = ('contact_type', 'value')


class EmployeeContactSerializer(EmployeeSerializer):
    contacts = ContactSerializer(many=True, read_only=True)
