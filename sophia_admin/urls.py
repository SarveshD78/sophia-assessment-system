from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='Home'),
    path('signin/', views.signIn, name='login'),
    path('signup/', views.signUp, name='signup'),
    path('logout/', views.logoutUser, name='logout'),
    path('dashboard/', views.Dashboard, name='Dashboard'),
    path('add-assessments/', views.Add_Assessments, name='Add_Assessments'),
    path('all-submissions/', views.All_Submissions, name='All_Submissions'),
    path('add-questions/<int:assessment_id>/', views.Add_Questions, name='Add_Questions'),
    path('all-submissions/', views.All_Submissions, name='All_Submissions'),
    path('analysis/<slug:submission_id>/', views.Analysis, name='Result'),
    # In your urls.py
path('download-pdf/<str:submission_id>/', views.download_analysis_pdf, name='download_pdf'),
]