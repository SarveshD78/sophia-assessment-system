from django.db import models
import random
import string


class Assessment(models.Model):
    assId = models.AutoField(primary_key=True)
    assessment_name = models.CharField(max_length=255, null=True)
    assessment_code = models.CharField(max_length=300, null=True, default="None")
    assessment_type = models.CharField(max_length=255, null=True, default="None")
    assessment_discription = models.CharField(max_length=1000, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.assessment_code or self.assessment_code == "None":
            # Generate a random 6-character code
            self.assessment_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.assessment_name


class Question(models.Model):
    questionId = models.AutoField(primary_key=True)
    question = models.CharField(max_length=255, null=True)
    correctanswer = models.CharField(max_length=255, null=True)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"ID : {self.questionId}   -  Question_Text : {self.question}"