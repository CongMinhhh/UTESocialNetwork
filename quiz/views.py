from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import EnglishQuestion, UserAnswer
from .forms import QuizAnswerForm
from .tasks import generate_daily_questions, clean_text
from django.contrib.auth.models import User
from core.models import Profile
import json
from django.utils.html import escape
from django.core.serializers.json import DjangoJSONEncoder
import html

# Create your views here.

@login_required
def daily_questions(request):
    # Get user profile
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    
    # Get today's date
    today = timezone.now().date()
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timezone.timedelta(days=1)
    
    # Query questions created today
    questions = EnglishQuestion.objects.filter(created_date=today)
    
    # If no questions exist for today or less than 20 questions, generate them
    if not questions.exists() or questions.count() < 20:
        # Delete any existing questions for today if there are less than 20
        if questions.exists():
            questions.delete()
            
        # Try to generate new questions
        num_questions = generate_daily_questions()
        questions = EnglishQuestion.objects.filter(created_date=today)
    
    # Clean and prepare questions data for JSON
    questions_data = []
    for q in questions:
        questions_data.append({
            'id': q.id,
            'question_text': clean_text(html.unescape(q.question_text)),
            'option_a': clean_text(html.unescape(q.option_a)),
            'option_b': clean_text(html.unescape(q.option_b)),
            'option_c': clean_text(html.unescape(q.option_c)),
            'option_d': clean_text(html.unescape(q.option_d)),
        })
    
    # Convert to JSON with proper encoding
    questions_json = json.dumps(questions_data, cls=DjangoJSONEncoder, ensure_ascii=False)
    
    # Get today's attempts and calculate rankings
    today_attempts = UserAnswer.objects.filter(
        answer_time__gte=today_start,
        answer_time__lt=today_end
    )
    
    # Group attempts by user and calculate scores
    user_scores = {}
    for attempt in today_attempts:
        if attempt.user not in user_scores:
            user_scores[attempt.user] = {
                'correct_answers': 0,
                'completion_time': attempt.completion_time,
                'username': attempt.user.username,
                'profile': Profile.objects.get(user=attempt.user)
            }
        if attempt.is_correct:
            user_scores[attempt.user]['correct_answers'] += 1
    
    # Convert to list and sort by score and completion time
    rankings = [
        {
            'username': data['username'],
            'score': data['correct_answers'],
            'completion_time': data['completion_time'],
            'profile': data['profile']
        }
        for user, data in user_scores.items()
    ]
    rankings.sort(key=lambda x: (-x['score'], x['completion_time']))
    
    # Get user's rank if they've attempted today
    user_rank = None
    user_score = None
    user_time = None
    for i, rank in enumerate(rankings, 1):
        if rank['username'] == request.user.username:
            user_rank = i
            user_score = rank['score']
            user_time = rank['completion_time']
            break
    
    context = {
        'user_profile': user_profile,
        'questions': questions,
        'questions_json': questions_json,
        'total_questions': questions.count(),
        'has_attempted_today': UserAnswer.objects.filter(
            user=request.user,
            answer_time__gte=today_start,
            answer_time__lt=today_end
        ).exists(),
        'top_attempts': rankings[:10],  # Top 10 users
        'user_score': user_score,
        'time_taken': user_time // 60 if user_time else None,  # Convert seconds to minutes
        'daily_rank': user_rank
    }
    
    return render(request, 'EnglishQuiz.html', context)

@login_required
@require_POST
def submit_answer(request, question_id):
    question = get_object_or_404(EnglishQuestion, id=question_id)
    
    # Check if user has already answered this question
    existing_answer = UserAnswer.objects.filter(
        user=request.user,
        question=question
    ).first()
    
    if existing_answer:
        return JsonResponse({
            'status': 'error',
            'message': 'You have already answered this question'
        })
    
    # Get the selected answer and completion time from POST data
    selected_answer = request.POST.get('answer')
    completion_time = request.POST.get('completion_time', 0)
    
    if not selected_answer or selected_answer not in ['A', 'B', 'C', 'D']:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid answer'
        })
    
    try:
        completion_time = int(completion_time)
    except (ValueError, TypeError):
        completion_time = 0
    
    # Create and save the answer
    answer = UserAnswer(
        user=request.user,
        question=question,
        selected_answer=selected_answer,
        completion_time=completion_time
    )
    answer.save()
    
    # Check if this was the last question for today
    today = timezone.now().date()
    today_questions = EnglishQuestion.objects.filter(created_date=today).count()
    user_answers_today = UserAnswer.objects.filter(
        user=request.user,
        answer_time__date=today
    ).count()
    
    is_last_question = user_answers_today >= today_questions
    
    return JsonResponse({
        'status': 'success',
        'is_correct': answer.is_correct,
        'correct_answer': question.correct_answer,
        'is_last_question': is_last_question
    })

@login_required
def quiz_history(request):
    # Get user's quiz history
    user_answers = UserAnswer.objects.filter(user=request.user).order_by('-created_at')
    
    # Group answers by date
    history_by_date = {}
    for answer in user_answers:
        date = answer.created_at.date()
        if date not in history_by_date:
            history_by_date[date] = []
        history_by_date[date].append(answer)
    
    context = {
        'user_profile': request.user.profile,
        'history_by_date': history_by_date,
    }
    return render(request, 'EnglishQuiz.html', context)

@login_required
def leaderboard(request):
    # Get all users' scores
    user_scores = {}
    for answer in UserAnswer.objects.all():
        if answer.user not in user_scores:
            user_scores[answer.user] = 0
        if answer.is_correct:
            user_scores[answer.user] += 1
    
    # Sort users by score
    sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
    
    context = {
        'user_profile': request.user.profile,
        'leaderboard': sorted_users,
    }
    return render(request, 'EnglishQuiz.html', context)

@login_required
def achievements(request):
    # Get user's achievements
    user_answers = UserAnswer.objects.filter(user=request.user)
    total_correct = user_answers.filter(is_correct=True).count()
    total_attempts = user_answers.count()
    
    # Calculate achievements
    achievements = {
        'total_questions_answered': total_attempts,
        'total_correct_answers': total_correct,
        'accuracy': round((total_correct / total_attempts * 100) if total_attempts > 0 else 0, 2),
    }
    
    context = {
        'user_profile': request.user.profile,
        'achievements': achievements,
    }
    return render(request, 'EnglishQuiz.html', context)
