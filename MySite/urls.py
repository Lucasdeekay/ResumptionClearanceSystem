from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .api_views import (
    ClearanceRequirementViewSet, DepartmentViewSet, FacultyViewSet, HostelViewSet,
    BursaryViewSet, StudentViewSet, StudentClearanceRequestsViewSet
)

router = DefaultRouter()
router.register('clearance_requirements', ClearanceRequirementViewSet, basename='clearance_requirements')
router.register('departments', DepartmentViewSet, basename='departments')
router.register('faculties', FacultyViewSet, basename='faculties')
router.register('hostels', HostelViewSet, basename='hostels')
router.register('bursaries', BursaryViewSet, basename='bursaries')
router.register('students', StudentViewSet, basename='students')
router.register('student_clearance_requests', StudentClearanceRequestsViewSet, basename='student_clearance_requests')

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<int:reset_uid>/', views.retrieve_password_view, name='retrieve_password'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('logout/', views.logout_view, name='logout'),
    path('api/', include(router.urls)),
]
