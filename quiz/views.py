from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import EnglishQuestion, UserAnswer
from .forms import QuizAnswerForm
from .tasks import generate_daily_questions

# Create your views here.

@login_required
def daily_questions(request):
    # Get today's date
    today = timezone.now().date()
    
    # Query questions created today
    questions = EnglishQuestion.objects.filter(created_date=today)
    
    # If no questions exist for today or less than 20 questions, generate them
    if not questions.exists() or questions.count() < 20:
        # Delete any existing questions for today if there are less than 20
        if questions.exists():
            questions.delete()
            
        # Try to generate new questions
        num_questions = generate_daily_questions()
        
        # If generation fails or returns less than 20 questions, use fallback questions
        if num_questions < 20:
            # Create a comprehensive set of fallback questions
            fallback_questions = [
                {
                    'question_text': 'What is the past tense of "go"?',
                    'option_a': 'went',
                    'option_b': 'gone',
                    'option_c': 'going',
                    'option_d': 'goes',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Which word is a synonym for "happy"?',
                    'option_a': 'sad',
                    'option_b': 'angry',
                    'option_c': 'joyful',
                    'option_d': 'tired',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Choose the correct sentence:',
                    'option_a': 'I have been to Paris last year',
                    'option_b': 'I went to Paris last year',
                    'option_c': 'I am going to Paris last year',
                    'option_d': 'I go to Paris last year',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'What is the opposite of "begin"?',
                    'option_a': 'start',
                    'option_b': 'continue',
                    'option_c': 'end',
                    'option_d': 'pause',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Which word is a noun?',
                    'option_a': 'run',
                    'option_b': 'beautiful',
                    'option_c': 'happiness',
                    'option_d': 'quickly',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Choose the correct preposition: "I am good ___ math."',
                    'option_a': 'in',
                    'option_b': 'at',
                    'option_c': 'on',
                    'option_d': 'with',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'What is the plural of "child"?',
                    'option_a': 'childs',
                    'option_b': 'children',
                    'option_c': 'childes',
                    'option_d': 'childrens',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Which sentence is grammatically correct?',
                    'option_a': 'She don\'t like coffee',
                    'option_b': 'She doesn\'t likes coffee',
                    'option_c': 'She doesn\'t like coffee',
                    'option_d': 'She not like coffee',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'What is the meaning of "break a leg"?',
                    'option_a': 'To hurt yourself',
                    'option_b': 'Good luck',
                    'option_c': 'To run fast',
                    'option_d': 'To fall down',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Choose the correct article: "___ sun rises in the east."',
                    'option_a': 'A',
                    'option_b': 'An',
                    'option_c': 'The',
                    'option_d': 'No article needed',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Which word is an adverb?',
                    'option_a': 'happy',
                    'option_b': 'quickly',
                    'option_c': 'beauty',
                    'option_d': 'run',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'What is the past participle of "write"?',
                    'option_a': 'wrote',
                    'option_b': 'written',
                    'option_c': 'writed',
                    'option_d': 'writing',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Choose the correct word: "I ___ to the store yesterday."',
                    'option_a': 'go',
                    'option_b': 'went',
                    'option_c': 'gone',
                    'option_d': 'going',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'What is the meaning of "piece of cake"?',
                    'option_a': 'Something delicious',
                    'option_b': 'Something easy',
                    'option_c': 'Something difficult',
                    'option_d': 'Something expensive',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'Which sentence uses the present perfect tense?',
                    'option_a': 'I am eating',
                    'option_b': 'I eat',
                    'option_c': 'I have eaten',
                    'option_d': 'I will eat',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'What is the comparative form of "good"?',
                    'option_a': 'gooder',
                    'option_b': 'more good',
                    'option_c': 'better',
                    'option_d': 'best',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'Choose the correct word: "She is ___ than her sister."',
                    'option_a': 'tall',
                    'option_b': 'taller',
                    'option_c': 'tallest',
                    'option_d': 'more tall',
                    'correct_answer': 'B'
                },
                {
                    'question_text': 'What is the meaning of "hit the books"?',
                    'option_a': 'To study',
                    'option_b': 'To exercise',
                    'option_c': 'To cook',
                    'option_d': 'To sleep',
                    'correct_answer': 'A'
                },
                {
                    'question_text': 'Which word is a conjunction?',
                    'option_a': 'happy',
                    'option_b': 'run',
                    'option_c': 'and',
                    'option_d': 'quickly',
                    'correct_answer': 'C'
                },
                {
                    'question_text': 'What is the superlative form of "bad"?',
                    'option_a': 'badder',
                    'option_b': 'more bad',
                    'option_c': 'worse',
                    'option_d': 'worst',
                    'correct_answer': 'D'
                }
            ]
            
            # Create all fallback questions
            for q_data in fallback_questions:
                question = EnglishQuestion(
                    question_text=q_data['question_text'],
                    option_a=q_data['option_a'],
                    option_b=q_data['option_b'],
                    option_c=q_data['option_c'],
                    option_d=q_data['option_d'],
                    correct_answer=q_data['correct_answer'],
                    created_date=today
                )
                question.save()
            
            # Get the newly created questions
            questions = EnglishQuestion.objects.filter(created_date=today)
    
    # Get user's answers for today's questions
    user_answers = UserAnswer.objects.filter(
        user=request.user,
        question__in=questions
    )
    
    # Check if user has attempted today's quiz
    has_attempted_today = user_answers.exists()
    
    # Calculate user's score
    user_score = user_answers.filter(is_correct=True).count() if has_attempted_today else 0
    
    # Prepare the context
    context = {
        'questions': questions,
        'total_questions': questions.count(),
        'user_profile': request.user.profile,
        'has_attempted_today': has_attempted_today,
        'user_score': user_score,
        'time_taken': None,  # You can implement this based on your timing system
        'daily_rank': None,  # You can implement this based on your ranking system
        'top_attempts': [],  # You can implement this based on your attempt model
        'quiz_status': 'Completed' if has_attempted_today else 'Not Started'
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
    
    # Get the selected answer from POST data
    selected_answer = request.POST.get('answer')
    if not selected_answer or selected_answer not in ['A', 'B', 'C', 'D']:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid answer'
        })
    
    # Create and save the answer
    answer = UserAnswer(
        user=request.user,
        question=question,
        selected_answer=selected_answer
    )
    answer.save()
    
    return JsonResponse({
        'status': 'success',
        'is_correct': answer.is_correct,
        'correct_answer': question.correct_answer
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
