import uuid
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from assessment.models import Feedback, FinalResult, Recording
from sophia_admin.functions import start_background_transcription
from sophia_admin.models import Assessment, Question
from sophia_admin.views import logout
from django.views.decorators.csrf import csrf_exempt


@login_required
def Assessments_Dashboard(request):
    """Assessment Dashboard for regular users"""
    if not request.user.is_authenticated:
        return redirect('Home')
    return render(request, 'assessment/dashboard.html')


@login_required
def Start_Assessments(request):
    """Assessment instructions page before starting"""
    if request.method == 'GET':
        assessment_code = request.GET.get('assessment_code')
        if assessment_code:
            try:
                assessment = Assessment.objects.get(assessment_code=assessment_code)
                context = {
                    'assessment_code': assessment_code,
                    'username': request.user.first_name or request.user.username,
                    'assessment_name': assessment.assessment_name,
                    'assessment_type': assessment.assessment_type,
                    'assessment_description': assessment.assessment_discription,
                    'assessment': assessment
                }
                return render(request, 'assessment/start_assessments.html', context)
            except Assessment.DoesNotExist:
                messages.error(request, 'Invalid assessment code. Please check and try again.')
                return redirect('Assessments_Dashboard')
        else:
            messages.warning(request, 'Please enter an assessment code.')
            return redirect('Assessments_Dashboard')
        

@login_required
def start_assessment(request, assessment_code):
    """Assessment page - Video recording interface"""
    try:
        assessment = Assessment.objects.get(assessment_code=assessment_code)
        allque = assessment.question_set.all()
        username = request.user.first_name or request.user.username
        assessment_name = assessment.assessment_name
        
        context = {
            'question': allque,
            'username': username,
            'assessment_name': assessment_name,
            'assessment_code': assessment_code,
            'assessment': assessment,
        }
        return render(request, 'assessment/assessment.html', context)
    except Assessment.DoesNotExist:
        messages.error(request, 'Invalid assessment code. Please check and try again.')
        return redirect('Assessments_Dashboard')
    

# views.py - Add this new view (don't change anything else)
def generate_random_code():
    """Generate unique submission ID"""
    return str(uuid.uuid4())[:8].upper()



@login_required
@csrf_exempt  # Add this if you're having CSRF issues with file uploads
def upload_recording(request, assessment_code):
    """
    Handle blob uploads from assessment.html and start background transcription for Technical assessments
    URL: assessment/begin/<assessment_code>/upload/
    """
    if request.method == 'POST':
        try:
            # Get form data exactly as your current JS sends it
            assessment_name = request.POST.get('ass_name')
            question_ids_str = request.POST.get('question_ids')
            
            print(f"[INFO] Received assessment: {assessment_name}")
            print(f"[INFO] Question IDs: {question_ids_str}")
            
            # Validate required data
            if not assessment_name or not question_ids_str:
                return JsonResponse({
                    'error': 'Missing assessment name or question IDs'
                }, status=400)
            
            # Parse question IDs
            question_ids = []
            for i in question_ids_str.split(','):
                question_ids.append(i.strip())
            
            print(f"[INFO] Parsed {len(question_ids)} question IDs")
            
            # Get assessment type
            try:
                assessment = Assessment.objects.get(assessment_name=assessment_name)
                assessment_type = assessment.assessment_type
                print(f"[INFO] Assessment type: {assessment_type}")
            except Assessment.DoesNotExist:
                return JsonResponse({
                    'error': f'Assessment "{assessment_name}" not found'
                }, status=404)
            
            # Get uploaded files (blobs) - THIS IS WHERE BLOBS ARE PROCESSED
            uploaded_files = []
            for key in sorted(request.FILES.keys()):  # Sort to maintain order
                if key.startswith('blob'):
                    blob_file = request.FILES[key]
                    uploaded_files.append(blob_file)
                    print(f"[INFO] Found blob: {key}, size: {blob_file.size} bytes")
            
            print(f"[INFO] Total blobs received: {len(uploaded_files)}")
            
            # Validate that we have the same number of files and questions
            if len(uploaded_files) != len(question_ids):
                return JsonResponse({
                    'error': f'Mismatch: {len(uploaded_files)} files vs {len(question_ids)} questions'
                }, status=400)
            
            # Generate unique submission ID
            submission_id = generate_random_code()
            print(f"[INFO] Generated submission ID: {submission_id}")
            
            # Process each blob and STORE IN RECORDING MODEL
            recordings_created = 0
            for index, uploaded_file in enumerate(uploaded_files):
                try:
                    question_id = question_ids[index]
                    print(f"[INFO] Processing blob {index + 1}/{len(uploaded_files)} for question ID: {question_id}")
                    
                    # Get question details
                    try:
                        question_obj = Question.objects.get(questionId=question_id)
                        question_text = question_obj.question
                        correct_answer = question_obj.correctanswer
                    except Question.DoesNotExist:
                        print(f"[WARNING] Question {question_id} not found, skipping...")
                        continue
                    
                    # CREATE RECORDING ENTRY - BLOB STORED IN video FIELD
                    recording = Recording.objects.create(
                        video=uploaded_file,  # ← BLOB STORED HERE IN FileField
                        user_name=str(request.user),  # Convert to string
                        assessment_name=assessment_name,
                        submission_id=submission_id,
                        question_id=question_id,
                        que=question_text,
                        c_ans=correct_answer,
                        assessmenttype=assessment_type
                    )
                    
                    recordings_created += 1
                    print(f"[SUCCESS] Saved recording {recording.ansId} with video: {recording.video.name}")
                    
                except Exception as e:
                    print(f"[ERROR] Failed to process blob {index}: {str(e)}")
                    continue
            
            if recordings_created == 0:
                return JsonResponse({
                    'error': 'No recordings were successfully saved'
                }, status=500)
            
            # Create final result entry
            try:
                final_result = FinalResult.objects.create(
                    submission_id=submission_id,
                    user_name=str(request.user),
                    assessment_name=assessment_name,
                    assessment_type=assessment_type,
                    total_recordings=recordings_created
                )
                print(f"[SUCCESS] Created FinalResult entry: {final_result}")
            except Exception as e:
                print(f"[ERROR] Failed to create FinalResult: {str(e)}")
                return JsonResponse({
                    'error': 'Failed to create final result entry'
                }, status=500)
            
            # ✅ NEW: Start background transcription for Technical assessments ONLY
            transcription_started = False
            if assessment_type.lower() == 'technical':
                try:
                    print(f"[INFO] Starting background transcription for Technical assessment: {submission_id}")
                    start_background_transcription(submission_id)
                    transcription_started = True
                    print(f"[SUCCESS] Background transcription started successfully")
                except Exception as e:
                    print(f"[ERROR] Failed to start background transcription: {str(e)}")
                    # Don't fail the whole request, just log the error
            else:
                print(f"[INFO] Skipping transcription for {assessment_type} assessment: {submission_id}")
            
            # ✅ STORE SESSION DATA FOR FEEDBACK PAGE
            request.session['assessment_name'] = assessment_name
            request.session['submission_id'] = submission_id
            request.session['assessment_type'] = assessment_type
            
            print(f"[SUCCESS] Assessment completed successfully. Submission ID: {submission_id}")
            print(f"[INFO] Session data stored: {assessment_name}, {submission_id}")
            
            # Return success response
            return JsonResponse({
                'success': True,
                'submission_id': submission_id,
                'recordings_saved': recordings_created,
                'total_expected': len(uploaded_files),
                'assessment_type': assessment_type,
                'transcription_started': transcription_started,
                'message': f'Assessment submitted successfully. {recordings_created} recordings saved.'
            })
            
        except Exception as e:
            print(f"[ERROR] Upload error: {str(e)}")
            return JsonResponse({
                'error': f'An unexpected error occurred: {str(e)}'
            }, status=500)
    
    else:
        return JsonResponse({
            'error': 'Invalid request method. Only POST allowed.'
        }, status=405)

@login_required(login_url='login')
def feedback_page(request):
    if request.method == 'POST':
        feedback_type = request.POST.get('feedback_type')
        
        # Save feedback
        Feedback.objects.create(
            user_name=request.user,
            feedback_type=feedback_type,
            assessment_name=request.session.get('assessment_name', ''),
            submission_id=request.session.get('submission_id', '')
        )
        
        # Logout and redirect
        logout(request)
        return redirect('login')
    
    # Show form
    context = {'user_name': request.user.first_name or request.user.username}
    return render(request, 'assessment/feedback.html', context)