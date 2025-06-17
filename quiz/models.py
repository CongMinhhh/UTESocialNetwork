from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class EnglishQuestion(models.Model):
    question_text = models.TextField(help_text="The question text")
    option_a = models.CharField(max_length=255, help_text="Option A")
    option_b = models.CharField(max_length=255, help_text="Option B")
    option_c = models.CharField(max_length=255, help_text="Option C")
    option_d = models.CharField(max_length=255, help_text="Option D")
    correct_answer = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        help_text="The correct answer (A, B, C, or D)"
    )
    created_date = models.DateField(
        default=timezone.now,
        help_text="The date when the question was created"
    )

    class Meta:
        ordering = ['-created_date']
        verbose_name = "English Question"
        verbose_name_plural = "English Questions"

    def __str__(self):
        return f"Question {self.id} - {self.created_date}"

class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_answers')
    question = models.ForeignKey(EnglishQuestion, on_delete=models.CASCADE, related_name='user_answers')
    selected_answer = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        help_text="The answer selected by the user"
    )
    is_correct = models.BooleanField(default=False, help_text="Whether the answer is correct")
    answer_time = models.DateTimeField(auto_now_add=True, help_text="When the answer was submitted")

    class Meta:
        ordering = ['-answer_time']
        unique_together = ['user', 'question']  # One answer per user per question

    def __str__(self):
        return f"{self.user.username}'s answer to Question {self.question.id}"

    def save(self, *args, **kwargs):
        # Check if the answer is correct before saving
        self.is_correct = self.selected_answer == self.question.correct_answer
        super().save(*args, **kwargs)
