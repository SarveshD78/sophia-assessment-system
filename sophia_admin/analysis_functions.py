import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import os
import cv2
import numpy as np
from assessment.models import Recording, FinalResult

# Auto-download required NLTK data
def ensure_nltk_data():
    """Ensure required NLTK data is downloaded"""
    try:
        # Try newer punkt_tab first
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        try:
            print("[INFO] Downloading NLTK punkt_tab...")
            nltk.download('punkt_tab', quiet=True)
        except:
            # Fallback to older punkt
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                print("[INFO] Downloading NLTK punkt...")
                nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("[INFO] Downloading NLTK stopwords...")
        nltk.download('stopwords', quiet=True)
    
    print("[INFO] NLTK data ready")

ensure_nltk_data()

def detect_generic_noise(text):
    """
    Universal noise detection for ANY assessment system
    """
    text_lower = text.lower()
    total_words = len(text_lower.split())
    
    # Generic noise patterns (universal)
    noise_patterns = [
        r'\b\d+\b',  # Numbers: 1, 2, 3, etc.
        r'\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\b',
        r'\b(test|exam|quiz|interview|assessment)\b',
        r'\b(question|answer|response|recording|audio|video)\b',
        r'\b(begin|start|end|finish|complete|submit)\b',
        r'\b(one|two|three|four|five|six|seven|eight|nine|ten)\b',
        r'\b(please|now|next|then|number)\b'
    ]
    
    noise_count = 0
    for pattern in noise_patterns:
        matches = len(re.findall(pattern, text_lower))
        noise_count += matches
    
    # Calculate noise ratio
    noise_ratio = noise_count / max(total_words, 1)
    return noise_ratio, noise_count, total_words

def clean_student_response(text):
    """
    Remove generic assessment artifacts
    """
    cleaned = text.lower()
    
    # Remove common assessment patterns
    patterns_to_remove = [
        r'\b(test|exam|quiz|interview|assessment)\b',
        r'\b(question|answer|response|recording|audio|video)\b',
        r'\b(begin|start|end|finish|complete|submit)\b',
        r'\b(number|no\.?)\s*\d+\b',
        r'\b(one|two|three|four|five|six|seven|eight|nine|ten)\b',
        r'\b\d+\b',  # Remove standalone numbers
        r'[.,:;!?]+'  # Remove excessive punctuation
    ]
    
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, ' ', cleaned)
    
    # Clean up whitespace
    cleaned = ' '.join(cleaned.split())
    return cleaned.strip()

def Technical_Interviewer_Accuracy(correct_answer, student_answer):
    """
    Universal Technical Interviewer - Works for ANY assessment system
    """
    try:
        print("[INFO] 🌍 UNIVERSAL TECHNICAL INTERVIEWER")
        print(f"[INTERVIEWER] Expected: '{correct_answer}'")
        print(f"[INTERVIEWER] Student: '{student_answer}'")
        
        # Stage 1: Universal noise detection
        noise_ratio, noise_count, total_words = detect_generic_noise(student_answer)
        print(f"[STAGE 1] Noise Detection: {noise_count}/{total_words} words = {noise_ratio:.2f} ratio")
        
        # If response is mostly noise (>60%), reject it
        if noise_ratio > 0.6:
            print("[STAGE 1] ❌ REJECTED - Response is mostly assessment noise")
            return 0
        
        # Stage 2: Clean the response
        clean_student = clean_student_response(student_answer)
        print(f"[STAGE 2] Cleaned Response: '{clean_student}'")
        
        # Check if anything meaningful remains
        if len(clean_student.strip()) < 2:
            print("[STAGE 2] ❌ REJECTED - No meaningful content after cleanup")
            return 0
        
        # Stage 3: Technical content evaluation
        correct_clean = correct_answer.lower().strip()
        
        # Extract meaningful words
        correct_words = set(re.split(r'[ ,.!;"()-]', correct_clean))
        correct_words = {w for w in correct_words if w and len(w) > 1}
        
        student_words = set(re.split(r'[ ,.!;"()-]', clean_student))
        student_words = {w for w in student_words if w and len(w) > 1}
        
        print(f"[STAGE 3] Expected concepts: {correct_words}")
        print(f"[STAGE 3] Student concepts: {student_words}")
        
        # Calculate concept coverage
        core_matches = correct_words.intersection(student_words)
        coverage = len(core_matches) / len(correct_words) if correct_words else 0
        
        # Calculate precision (how much of student answer is relevant)
        precision = len(core_matches) / len(student_words) if student_words else 0
        
        print(f"[STAGE 3] Concept matches: {core_matches}")
        print(f"[STAGE 3] Coverage: {coverage:.2f}, Precision: {precision:.2f}")
        
        # Scoring logic
        if coverage >= 0.9 and precision >= 0.7:
            score = 95
            grade = "EXCELLENT - Perfect answer"
        elif coverage >= 0.7 and precision >= 0.6:
            score = 85
            grade = "VERY GOOD - Strong technical answer"
        elif coverage >= 0.5 and precision >= 0.5:
            score = 75
            grade = "GOOD - Solid understanding"
        elif coverage >= 0.4 and precision >= 0.3:
            score = 60
            grade = "ADEQUATE - Basic understanding"
        elif coverage >= 0.3:
            score = 45
            grade = "WEAK - Limited understanding"
        elif coverage >= 0.1:
            score = 25
            grade = "POOR - Minimal understanding"
        else:
            # Check for any technical keywords
            tech_indicators = ['program', 'code', 'software', 'computer', 'data', 'system']
            if any(word in clean_student for word in tech_indicators):
                score = 10
                grade = "INADEQUATE - Shows some technical awareness"
            else:
                score = 0
                grade = "COMPLETELY WRONG - No technical understanding"
        
        print(f"[FINAL] Score: {score}% - {grade}")
        return score
    
    except Exception as e:
        print(f"[ERROR] Technical interviewer evaluation failed: {e}")
        return 0

def FindAcc(S1, S2):
    """
    Enhanced version using Technical Interviewer Logic
    """
    return Technical_Interviewer_Accuracy(S1, S2)

def calculate_text_similarity(recorded_answer, correct_answer):
    """
    Wrapper function using your FindAcc logic
    """
    try:
        if not recorded_answer or not correct_answer:
            return 0
        
        # Use your original FindAcc function
        accuracy = FindAcc(correct_answer, recorded_answer)
        accuracy_percentage = int(accuracy)
        
        print(f"[SUCCESS] Text similarity using FindAcc: {accuracy_percentage}%")
        return accuracy_percentage
        
    except Exception as e:
        print(f"[ERROR] Text similarity failed: {str(e)}")
        return 0

def analyze_video_emotions(video_path):
    """
    Analyze emotions using OpenCV face detection
    """
    try:
        print(f"[INFO] Starting OpenCV emotion analysis for: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"[ERROR] Could not open video: {video_path}")
            return {'confidence': 50, 'nervousness': 30, 'neutral': 20}
        
        # Get video properties more safely
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Handle invalid frame counts
        if frame_count <= 0 or fps <= 0:
            print(f"[WARNING] Invalid video properties: frames={frame_count}, fps={fps}")
            cap.release()
            return {'confidence': 60, 'nervousness': 25, 'neutral': 15}
        
        # Load face cascade
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            if face_cascade.empty():
                print("[WARNING] Face cascade failed to load")
                cap.release()
                return {'confidence': 55, 'nervousness': 25, 'neutral': 20}
        except Exception as e:
            print(f"[WARNING] Face cascade error: {e}")
            cap.release()
            return {'confidence': 55, 'nervousness': 25, 'neutral': 20}
        
        face_detections = 0
        total_frames_checked = 0
        
        # Sample every 2 seconds, but limit total frames checked
        frame_interval = max(int(fps * 2), 30)
        max_frames_to_check = min(frame_count, 50)  # Limit to 50 frames max
        
        print(f"[INFO] Video: {frame_count} frames at {fps} fps, checking {max_frames_to_check} frames")
        
        for i in range(max_frames_to_check):
            frame_pos = int((frame_count / max_frames_to_check) * i)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = cap.read()
            
            if not ret:
                break
            
            total_frames_checked += 1
            
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    face_detections += 1
                    
            except Exception as e:
                print(f"[WARNING] Frame processing error: {e}")
                continue
        
        cap.release()
        
        # Calculate emotions based on face detection
        if total_frames_checked > 0:
            face_ratio = face_detections / total_frames_checked
            
            # More face detection = higher confidence
            confidence = int(40 + (face_ratio * 40))  # 40-80 range
            nervousness = int(35 - (face_ratio * 20))  # 15-35 range  
            neutral = 100 - confidence - nervousness
            
        else:
            confidence, nervousness, neutral = 55, 25, 20
        
        result = {
            'confidence': max(0, min(100, confidence)),
            'nervousness': max(0, min(100, nervousness)),
            'neutral': max(0, min(100, neutral))
        }
        
        print(f"[SUCCESS] OpenCV emotion analysis: {result}")
        print(f"[INFO] Face detection: {face_detections}/{total_frames_checked} frames ({face_ratio:.2f})")
        
        return result
        
    except Exception as e:
        print(f"[ERROR] OpenCV emotion analysis failed: {str(e)}")
        return {'confidence': 55, 'nervousness': 25, 'neutral': 20}

def generate_analysis_results(submission_id, assessment_type):
    """
    Main function to generate analysis results
    """
    try:
        print(f"[INFO] Starting analysis for submission: {submission_id}")
        print(f"[INFO] Assessment type: {assessment_type}")
        
        recordings = Recording.objects.filter(submission_id=submission_id)
        
        if not recordings.exists():
            print(f"[ERROR] No recordings found for submission: {submission_id}")
            return
        
        total_accuracy = 0
        processed_count = 0
        
        print(f"[INFO] Processing {recordings.count()} recordings...")
        
        for recording in recordings:
            try:
                print(f"[INFO] Processing recording {recording.ansId} - Question: {recording.que[:50]}...")
                
                # Always perform emotion analysis
                video_path = recording.video.path
                if os.path.exists(video_path):
                    emotions = analyze_video_emotions(video_path)
                    recording.confidence = emotions['confidence']
                    recording.nervousness = emotions['nervousness']
                    recording.neutral = emotions['neutral']
                    print(f"[SUCCESS] Emotion analysis completed for recording {recording.ansId}")
                else:
                    print(f"[WARNING] Video file not found: {video_path}")
                    recording.confidence = 55
                    recording.nervousness = 25
                    recording.neutral = 20
                
                # Text analysis only for Technical assessments
                if assessment_type.lower() == 'technical':
                    if recording.recorded_answer and recording.c_ans:
                        print(f"[INFO] Comparing texts for recording {recording.ansId}:")
                        print(f"[INFO] Correct answer: '{recording.c_ans}'")
                        print(f"[INFO] Recorded answer: '{recording.recorded_answer}'")
                        
                        accuracy = calculate_text_similarity(
                            recording.recorded_answer, 
                            recording.c_ans
                        )
                        recording.answer_accurecy = accuracy
                        total_accuracy += accuracy
                        processed_count += 1
                        print(f"[SUCCESS] FindAcc completed for recording {recording.ansId}: {accuracy}%")
                    else:
                        print(f"[WARNING] Missing transcript or correct answer for recording {recording.ansId}")
                        recording.answer_accurecy = 0
                else:
                    print(f"[INFO] Skipping text analysis for {assessment_type} assessment")
                
                recording.save()
                print(f"[SUCCESS] Saved recording {recording.ansId}")
                
            except Exception as e:
                print(f"[ERROR] Failed to process recording {recording.ansId}: {str(e)}")
                continue
        
        # Update final result
        final_result = FinalResult.objects.get(submission_id=submission_id)
        
        if assessment_type.lower() == 'technical' and processed_count > 0:
            overall_accuracy = total_accuracy // processed_count
            if hasattr(final_result, 'total_accurecy'):
                final_result.total_accurecy = overall_accuracy
                print(f"[INFO] Overall accuracy calculated: {overall_accuracy}%")
        
        if hasattr(final_result, 'result_generate'):
            final_result.result_generate = True
        
        final_result.save()
        
        print(f"[SUCCESS] Analysis generation completed for submission: {submission_id}")
        
    except Exception as e:
        print(f"[ERROR] Analysis generation failed for submission {submission_id}: {str(e)}")