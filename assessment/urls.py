from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.Assessments_Dashboard, name='Assessments_Dashboard'),
    path('start/', views.Start_Assessments, name='Start_Assessments'),
    path('assessment/begin/<str:assessment_code>/', views.start_assessment, name='start_assessment'),
    path('assessment/begin/<str:assessment_code>/upload/', views.upload_recording, name='upload_recording'),
    path('feedback/', views.feedback_page, name='feedback_page'),
]