from django import forms
from .models import UserAnswer

class QuizAnswerForm(forms.ModelForm):
    class Meta:
        model = UserAnswer
        fields = ['selected_answer']
        widgets = {
            'selected_answer': forms.RadioSelect(
                choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
                attrs={'class': 'answer-options'}
            )
        } 