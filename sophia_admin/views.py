from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .analysis_functions import generate_analysis_results
import threading
from assessment.models import FinalResult, Recording
from .forms import UserRegistrationForm, AssessmentForm, QuestionForm
from .models import Assessment, Question
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
from django.shortcuts import get_object_or_404


def Home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('Dashboard')
        return redirect('Assessments_Dashboard')
    else:
        return render(request, 'sophia_admin/index.html')


def signIn(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('Dashboard')
        return redirect('Assessments_Dashboard')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if request.user.is_staff:
                    return redirect('Dashboard')
                return redirect('Assessments_Dashboard')  # Regular users go to Assessment Dashboard
            else:
                messages.warning(request, 'Incorrect Credentials')
        return render(request, 'sophia_admin/signin.html')

def signUp(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('Dashboard')
        return redirect('Assessments_Dashboard')
    else:
        form = UserRegistrationForm()
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Account created successfully! Please sign in.')
                return redirect('login')
            else:
                messages.error(request, 'Please correct the errors below.')
        return render(request, 'sophia_admin/signup.html', {'form': form})


def logoutUser(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('Home')


@login_required
def Dashboard(request):
    """Admin Dashboard for staff users"""
    if not request.user.is_staff:
        return redirect('Home')
    
    assessments = Assessment.objects.all()
    
    context = {
        'assessments': assessments,
        'total_assessments': assessments.count(),
    }
    
    return render(request, 'sophia_admin/dashboard.html', context)


@login_required
def Assessments_Dashboard(request):
    """Assessment Dashboard for regular users"""
    if not request.user.is_authenticated:
        return redirect('Home')
    return render(request, 'assessment/dashboard.html')


@login_required
def Add_Assessments(request):
    """Add new assessment"""
    if not request.user.is_staff:
        return redirect('Home')
    
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save()
            messages.success(request, f'Assessment "{assessment.assessment_name}" created successfully! Assessment Code: {assessment.assessment_code}')
            return redirect('Dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AssessmentForm()
    
    context = {
        'form': form
    }
    
    return render(request, 'sophia_admin/add_assessment.html', context)


@login_required
def Add_Questions(request, assessment_id):
    """Add questions to an assessment"""
    if not request.user.is_staff:
        return redirect('Home')
    
    assessment = get_object_or_404(Assessment, assId=assessment_id)
    questions = Question.objects.filter(assessment=assessment)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.assessment = assessment
            question.save()
            messages.success(request, 'Question added successfully!')
            return redirect('Add_Questions', assessment_id=assessment_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = QuestionForm()
    
    context = {
        'form': form,
        'assessment': assessment,
        'questions': questions,
        'total_questions': questions.count(),
    }
    
    return render(request, 'sophia_admin/add_questions.html', context)



@login_required(login_url='login')
def All_Submissions(request):
    url = settings.MEDIA_URL
    all_data = Recording.objects.all().values('user_name', 'assessment_name', 'submission_id', 'assessmenttype').distinct()
    return render(request, 'sophia_admin/all_submissions.html', {'all_data': all_data, 'url': url})




@login_required
def Analysis(request, submission_id):
    """
    Single view to handle both display and analysis generation
    """
    url = settings.MEDIA_URL
    recordings = Recording.objects.filter(submission_id=submission_id)
    F_result = FinalResult.objects.filter(submission_id=submission_id)
    
    # Handle POST request (Generate Analysis)
    if request.method == 'POST':
        try:
            # Get final result to check assessment type
            final_result = get_object_or_404(FinalResult, submission_id=submission_id)
            
            # Check if already generated
            if hasattr(final_result, 'result_generate') and final_result.result_generate:
                return JsonResponse({
                    'success': False,
                    'message': 'Analysis already generated for this submission'
                })
            
            # Check if recordings exist
            if not recordings.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'No recordings found for this submission'
                })
            
            # Start background analysis
            print(f"[INFO] Starting analysis generation for submission: {submission_id}")
            print(f"[INFO] Assessment type: {final_result.assessment_type}")
            
            # Start analysis in background thread
            thread = threading.Thread(
                target=generate_analysis_results,
                args=(submission_id, final_result.assessment_type)
            )
            thread.daemon = True
            thread.start()
            
            return JsonResponse({
                'success': True,
                'message': 'Analysis generation started',
                'submission_id': submission_id
            })
            
        except Exception as e:
            print(f"[ERROR] Failed to start analysis generation: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error starting analysis: {str(e)}'
            })
    
    # Handle GET request (Display Analysis)
    else:
        return render(request, 'sophia_admin/analysis.html', {
            'recordings': recordings,
            'F_result': F_result,
            'url': url
        })
    

# In your views.py




def download_analysis_pdf(request, submission_id):
    """
    Generate and download real PDF report
    """
    try:
        import weasyprint
        
        # Get data
        recordings = Recording.objects.filter(submission_id=submission_id)
        result = get_object_or_404(FinalResult, submission_id=submission_id)
        
        context = {
            'recordings': recordings,
            'result': result,
        }
        
        # Render HTML template
        html_string = render_to_string('sophia_admin/pdf_report.html', context)
        
        # Generate actual PDF
        pdf = weasyprint.HTML(string=html_string).write_pdf()
        
        # Return PDF for download
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="analysis_report_{submission_id}.pdf"'
        return response
        
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)