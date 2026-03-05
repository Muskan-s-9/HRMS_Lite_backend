from rest_framework import serializers
from .models import Employee, Attendance
from django.core.exceptions import ValidationError


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'full_name', 'email', 'department', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_email(self, value):
        if Employee.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_employee_id(self, value):
        if Employee.objects.filter(employee_id=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("This employee ID already exists.")
        return value


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id_display = serializers.CharField(source='employee.employee_id', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_name', 'employee_id_display', 'date', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_employee(self, value):
        if not Employee.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Employee not found.")
        return value

    def validate(self, data):
        employee = data.get('employee')
        date = data.get('date')

        if employee and date:
            existing = Attendance.objects.filter(employee=employee, date=date)
            if self.instance:
                existing = existing.exclude(id=self.instance.id)
            if existing.exists():
                raise serializers.ValidationError("Attendance for this employee on this date already exists.")

        return data


class EmployeeDetailSerializer(serializers.ModelSerializer):
    attendance_records = serializers.SerializerMethodField()
    total_present_days = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'full_name', 'email', 'department', 'attendance_records', 'total_present_days', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_attendance_records(self, obj):
        attendance = obj.attendance_records.all()
        return AttendanceSerializer(attendance, many=True).data

    def get_total_present_days(self, obj):
        return obj.attendance_records.filter(status='present').count()
