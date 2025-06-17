import json
from datetime import date
from openai import OpenAI
from django.conf import settings
from .models import EnglishQuestion

def generate_daily_questions():
    """
    Generates 20 English multiple-choice questions using OpenAI's GPT model
    and saves them to the database.
    """
    # Check if API key is available
    if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
        print("OpenAI API key not found in settings")
        return 0

    try:
        # Initialize OpenAI client with API key from settings
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # Prepare the prompt
        prompt = """Give me 20 English multiple-choice questions (beginner to intermediate level). 
        Each question should have 4 options and only one correct answer. 
        Return the result as a JSON array like this: 
        [{ 'question': '...', 'a': '...', 'b': '...', 'c': '...', 'd': '...', 'answer': 'A' }, ...]
        
        Make sure the questions are diverse and cover different topics like:
        - Grammar
        - Vocabulary
        - Reading comprehension
        - Common expressions
        - Idioms
        
        Each question should be clear and unambiguous."""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful English language teacher."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )

        # Extract the JSON string from the response
        json_str = response.choices[0].message.content.strip()
        
        # Parse the JSON response
        questions_data = json.loads(json_str)

        # Save questions to database
        created_questions = []
        for q_data in questions_data:
            question = EnglishQuestion(
                question_text=q_data['question'],
                option_a=q_data['a'],
                option_b=q_data['b'],
                option_c=q_data['c'],
                option_d=q_data['d'],
                correct_answer=q_data['answer'],
                created_date=date.today()
            )
            created_questions.append(question)

        # Bulk create all questions
        EnglishQuestion.objects.bulk_create(created_questions)
        
        return len(created_questions)

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return 0
    except Exception as e:
        print(f"Error generating questions: {e}")
        return 0 