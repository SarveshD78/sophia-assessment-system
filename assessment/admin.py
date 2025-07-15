from django.contrib import admin

from assessment.models import FinalResult, Recording,Feedback

# Register your models here.
admin.site.register(Recording)
admin.site.register(FinalResult)
admin.site.register(Feedback)