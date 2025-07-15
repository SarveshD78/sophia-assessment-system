from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Assessment, Question


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set placeholders and IDs to match your CSS
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username',
            'id': 'uname',
            'class': 'form-input'
        })
        
        self.fields['first_name'].widget.attrs.update({
            'placeholder': 'First Name',
            'id': 'fname',
            'class': 'form-input'
        })
        
        self.fields['last_name'].widget.attrs.update({
            'placeholder': 'Last Name',
            'id': 'lname',
            'class': 'form-input'
        })
        
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Email',
            'id': 'email',
            'class': 'form-input'
        })
        
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Password',
            'id': 'passwd',
            'class': 'form-input'
        })
        
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm Password',
            'id': 'cpasswd',
            'class': 'form-input'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['assessment_name', 'assessment_type', 'assessment_discription']
        widgets = {
            'assessment_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter assessment name'
            }),
            'assessment_type': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('', 'Select assessment type'),
                ('Technical', 'Technical Assessment'),
                ('HR', 'HR Assessment'),
            ]),
            'assessment_discription': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter assessment description'
            })
        }
        labels = {
            'assessment_name': 'Assessment Name',
            'assessment_type': 'Assessment Type',
            'assessment_discription': 'Description'
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'correctanswer']
        widgets = {
            'question': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter the question'
            }),
            'correctanswer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the correct answer'
            })
        }
        labels = {
            'question': 'Question',
            'correctanswer': 'Correct Answer'
        }