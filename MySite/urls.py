from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .api_views import ( DepartmentViewSet, FacultyViewSet, HostelViewSet,
    BursaryViewSet, StudentViewSet, StudentClearanceRequestsViewSet, ClearanceDocumentViewSet
)

router = DefaultRouter()
router.register('clearance_documents', ClearanceDocumentViewSet, basename='clearance_documents')
router.register('departments', DepartmentViewSet, basename='departments')
router.register('faculties', FacultyViewSet, basename='faculties')
router.register('hostels', HostelViewSet, basename='hostels')
router.register('bursaries', BursaryViewSet, basename='bursaries')
router.register('students', StudentViewSet, basename='students')
router.register('student_clearance_requests', StudentClearanceRequestsViewSet, basename='student_clearance_requests')

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<int:reset_uid>/', views.retrieve_password_view, name='retrieve_password'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('logout/', views.logout_view, name='logout'),
    path('student-dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('student-clearance-request/', views.student_clearance_request, name='student_clearance_request'),
    path('student-upload-clearance/', views.student_upload_clearance, name='student_upload_clearance'),
    path('student-clearance-status/', views.student_clearance_status, name='student_clearance_status'),
    path('api/', include(router.urls)),
]
