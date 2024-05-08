from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated

from .models import (
    Student, ClearanceRequirement, Department, Faculty, Hostel, Bursary, StudentClearanceRequests
)
from .serializers import (
    ClearanceRequirementSerializer, DepartmentSerializer, FacultySerializer, HostelSerializer,
    BursarySerializer, StudentSerializer, StudentClearanceRequestsSerializer
)


class ClearanceRequirementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing clearance requirements
    """
    permission_classes = [IsAuthenticated]  # Require authentication
    queryset = ClearanceRequirement.objects.all()
    serializer_class = ClearanceRequirementSerializer


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing departments
    """
    permission_classes = [IsAuthenticated]  # Require authentication
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing faculties
    """
    permission_classes = [IsAuthenticated]  # Require authentication
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer


class HostelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing hostels
    """
    permission_classes = [IsAuthenticated]  # Require authentication
    queryset = Hostel.objects.all()
    serializer_class = HostelSerializer


class BursaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing bursary information
    """
    permission_classes = [IsAuthenticated]  # Require authentication
    queryset = Bursary.objects.all()
    serializer_class = BursarySerializer


class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing student data (create, view, update, delete)
    """
    permission_classes = [IsAuthenticated]  # Require authentication
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentClearanceRequestsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing student clearance requests
    """
    permission_classes = [IsAuthenticated]  # Require authentication
    queryset = StudentClearanceRequests.objects.all()
    serializer_class = StudentClearanceRequestsSerializer
