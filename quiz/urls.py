from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('daily/', views.daily_questions, name='daily_questions'),
    path('submit/<int:question_id>/', views.submit_answer, name='submit_answer'),
    path('history/', views.quiz_history, name='quiz_history'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('achievements/', views.achievements, name='achievements'),
] 