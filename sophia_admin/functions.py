import threading
import os
from django.conf import settings
from assessment.models import Recording
import requests

API_KEY = "15deebc06d324f68a49861f3ad44043e"

def transcribe_video_to_text(video_file_path):
    """
    Transcribe video file using AssemblyAI API
    """
    transcript = ""
    try:
        print(f"[INFO] Starting transcription for file: {video_file_path}")
        
        def read_file(filename, chunk_size=5242880):
            with open(filename, 'rb') as _file:
                while True:
                    data = _file.read(chunk_size)
                    if not data:
                        break
                    yield data

        headers = {'authorization': API_KEY}
        
        # Upload video file
        print("[INFO] Uploading video...")
        response = requests.post(
            'https://api.assemblyai.com/v2/upload', 
            headers=headers, 
            data=read_file(video_file_path)
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Upload failed: {response.status_code}")
            return ""
        
        upload_response = response.json()
        
        # Create transcription job
        print("[INFO] Creating transcription job...")
        transcript_request = {
            "audio_url": upload_response["upload_url"]
        }
        
        response = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            json=transcript_request,
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Transcription request failed: {response.status_code}")
            return ""
        
        transcript_response = response.json()
        transcript_id = transcript_response["id"]
        
        # Poll for completion
        polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        print(f"[INFO] Polling for completion: {transcript_id}")
        
        while True:
            response = requests.get(polling_endpoint, headers=headers)
            result = response.json()
            
            if result["status"] == "completed":
                transcript = result["text"]
                print(f"[SUCCESS] Transcription completed: {transcript[:100]}...")
                break
            elif result["status"] == "error":
                print(f"[ERROR] Transcription failed: {result}")
                break
            else:
                print(f"[INFO] Status: {result['status']}, waiting...")
                threading.Event().wait(3)  # Wait 3 seconds before polling again
        
    except Exception as e:
        print(f"[ERROR] Transcription failed: {str(e)}")
    
    return transcript


def process_technical_assessment_transcription(submission_id):
    """
    Background function to transcribe all videos for a technical assessment
    """
    try:
        print(f"[INFO] Starting background transcription for submission: {submission_id}")
        
        # Get all recordings for this submission
        recordings = Recording.objects.filter(submission_id=submission_id)
        
        if not recordings.exists():
            print(f"[WARNING] No recordings found for submission: {submission_id}")
            return
        
        print(f"[INFO] Found {recordings.count()} recordings to process")
        
        # Process each recording
        for recording in recordings:
            try:
                print(f"[INFO] Processing recording {recording.ansId} - Question: {recording.que[:50]}...")
                
                # Get video file path
                video_path = recording.video.path
                
                if not os.path.exists(video_path):
                    print(f"[ERROR] Video file not found: {video_path}")
                    continue
                
                # Transcribe video
                transcript = transcribe_video_to_text(video_path)
                
                if transcript:
                    # Update recording with transcript
                    recording.recorded_answer = transcript
                    recording.save()
                    print(f"[SUCCESS] Saved transcript for recording {recording.ansId}")
                else:
                    print(f"[WARNING] Empty transcript for recording {recording.ansId}")
                
            except Exception as e:
                print(f"[ERROR] Failed to process recording {recording.ansId}: {str(e)}")
                continue
        
        print(f"[SUCCESS] Background transcription completed for submission: {submission_id}")
        
    except Exception as e:
        print(f"[ERROR] Background transcription failed for submission {submission_id}: {str(e)}")


def start_background_transcription(submission_id):
    """
    Start background transcription in a separate thread
    """
    thread = threading.Thread(
        target=process_technical_assessment_transcription, 
        args=(submission_id,)
    )
    thread.daemon = True
    thread.start()
    print(f"[INFO] Background transcription started for submission: {submission_id}")