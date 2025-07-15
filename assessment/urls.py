from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('dashboard/', views.Assessments_Dashboard, name='Assessments_Dashboard'),
    path('start/', views.Start_Assessments, name='Start_Assessments'),
    path('assessment/begin/<str:assessment_code>/', views.start_assessment, name='start_assessment'),
    path('assessment/begin/<str:assessment_code>/upload/', views.upload_recording, name='upload_recording'),
    path('feedback/', views.feedback_page, name='feedback_page'),
]

if settings.DEBUG or True:  # For production, you might want to handle this differently
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)