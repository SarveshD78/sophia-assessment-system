from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# models.py - Both models needed for storing blobs

class Recording(models.Model):
    """Main model for storing video blobs and assessment data"""
    ansId = models.AutoField(primary_key=True)
    submission_id = models.CharField(max_length=255, null=True)
    user_name = models.CharField(max_length=255, null=True)
    assessment_name = models.CharField(max_length=300, null=True)
    assessmenttype = models.CharField(max_length=300, null=True)
    question_id = models.IntegerField(null=True)
    video = models.FileField(upload_to='assessment_videos/', blank=True)  # ← BLOBS STORED HERE
    que = models.CharField(max_length=300, null=True)
    c_ans = models.CharField(max_length=300, null=True)
    recorded_answer = models.CharField(max_length=300, null=True)
    answer_accurecy = models.IntegerField(null=True, default=0)
    confidence = models.IntegerField(null=True, default=0)
    nervousness = models.IntegerField(null=True, default=0)
    neutral = models.IntegerField(null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ansId} - {self.user_name} - {self.assessment_name}"

# In your models.py
class FinalResult(models.Model):
    submission_id = models.CharField(max_length=255, unique=True)
    user_name = models.CharField(max_length=255)
    assessment_name = models.CharField(max_length=300)
    assessment_type = models.CharField(max_length=300)
    completion_date = models.DateTimeField(auto_now_add=True)
    total_recordings = models.IntegerField(default=0)
    
    # ADD THESE MISSING FIELDS:
    result_generate = models.BooleanField(default=False)  # ← ADD THIS
    total_accurecy = models.IntegerField(null=True, default=0)  # ← ADD THIS TOO
    
    def __str__(self):
        return f"{self.submission_id} - {self.user_name}"



class Feedback(models.Model):
    FEEDBACK_CHOICES = [
        ('ImprovementNeeded', 'Improvement Needed'),
        ('CouldBeBetter', 'Could Be Better'),
        ('Good', 'Good'),
        ('Excellent', 'Excellent'),
    ]
    
    user_name = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    feedback_type = models.CharField(max_length=100, choices=FEEDBACK_CHOICES)
    assessment_name = models.CharField(max_length=300, null=True, blank=True)
    submission_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user_name} - {self.feedback_type}"
    
    class Meta:
        ordering = ['-created_at']