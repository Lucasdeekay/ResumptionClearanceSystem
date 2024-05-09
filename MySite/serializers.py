from rest_framework import serializers
from .models import (
    Student, ClearanceRequirement, Department, Faculty, Hostel, Bursary, StudentClearanceRequests, ClearanceDocument
)

class ClearanceDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClearanceDocument
        fields = '__all__'  # Serialize all fields


class ClearanceRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClearanceRequirement
        fields = '__all__'  # Serialize all fields


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'  # Serialize all fields


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = '__all__'  # Serialize all fields


class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = '__all__'  # Serialize all fields


class BursarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Bursary
        fields = '__all__'  # Serialize all fields


class StudentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)  # Show username instead of user object

    class Meta:
        model = Student
        fields = ('user', 'first_name', 'last_name', 'middle_name', 'matric_number', 'email')


class StudentClearanceRequestsSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)  # Nested serializer for student details
    faculty_clearance = FacultySerializer(read_only=True)  # Nested serializer for faculty clearance details
    department_clearance = DepartmentSerializer(read_only=True)  # Nested serializer for department clearance details
    hostel_clearance = HostelSerializer(read_only=True)  # Nested serializer for hostel clearance details
    bursary_clearance = BursarySerializer(read_only=True)  # Nested serializer for bursary clearance details

    class Meta:
        model = StudentClearanceRequests
        fields = ('student', 'semester', 'session', 'faculty_clearance', 'department_clearance', 'hostel_clearance', 'bursary_clearance')
