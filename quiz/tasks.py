import json
from datetime import date
from django.conf import settings
from .models import EnglishQuestion
import logging
from django.utils import timezone
import random
import cohere
import re
import html
from html.parser import HTMLParser
import unicodedata

logger = logging.getLogger(__name__)

def clean_text(text):
    """
    Clean text by:
    1. Decoding HTML entities
    2. Converting smart quotes to regular quotes
    3. Removing extra whitespace
    4. Handling special characters
    5. Normalizing Unicode characters
    """
    if not text:
        return text
        
    # Decode HTML entities
    text = html.unescape(text)
    
    # Convert smart quotes to regular quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Handle other special characters
    replacements = {
        '&quot;': '"',
        '&apos;': "'",
        '&#x27;': "'",
        '&#39;': "'",
        '&#34;': '"',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '\u2018': "'",  # Left single quotation mark
        '\u2019': "'",  # Right single quotation mark
        '\u201C': '"',  # Left double quotation mark
        '\u201D': '"',  # Right double quotation mark
        '\u2013': '-',  # En dash
        '\u2014': '-',  # Em dash
        '\u2026': '...',  # Horizontal ellipsis
        '\u00A0': ' ',  # Non-breaking space
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Normalize Unicode characters (convert to their closest ASCII representation)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    
    return text.strip()

def get_fallback_questions():
    """
    Returns a list of predefined questions when API fails.
    """
    fallback_questions = [
        {
            "question": "Choose the correct form of the verb: 'She ___ to school every day.'",
            "a": "go",
            "b": "goes",
            "c": "going",
            "d": "went",
            "answer": "B"
        },
        {
            "question": "Which word is a synonym for 'happy'?",
            "a": "sad",
            "b": "angry",
            "c": "joyful",
            "d": "tired",
            "answer": "C"
        },
        {
            "question": "Select the correct preposition: 'I'm interested ___ learning English.'",
            "a": "in",
            "b": "on",
            "c": "at",
            "d": "for",
            "answer": "A"
        },
        {
            "question": "What is the past tense of 'eat'?",
            "a": "eat",
            "b": "eaten",
            "c": "ate",
            "d": "eating",
            "answer": "C"
        },
        {
            "question": "Choose the correct article: '___ sun rises in the east.'",
            "a": "A",
            "b": "An",
            "c": "The",
            "d": "No article needed",
            "answer": "C"
        },
        {
            "question": "Which sentence is grammatically correct?",
            "a": "She don't like coffee",
            "b": "She doesn't likes coffee",
            "c": "She doesn't like coffee",
            "d": "She not like coffee",
            "answer": "C"
        },
        {
            "question": "What is the opposite of 'expensive'?",
            "a": "cheap",
            "b": "costly",
            "c": "price",
            "d": "money",
            "answer": "A"
        },
        {
            "question": "Choose the correct word order: 'I ___ my homework yesterday.'",
            "a": "did finish",
            "b": "finished",
            "c": "have finish",
            "d": "finishing",
            "answer": "B"
        },
        {
            "question": "Which is a proper noun?",
            "a": "city",
            "b": "London",
            "c": "beautiful",
            "d": "building",
            "answer": "B"
        },
        {
            "question": "Select the correct comparative form: 'This book is ___ than that one.'",
            "a": "more better",
            "b": "more good",
            "c": "better",
            "d": "gooder",
            "answer": "C"
        },
        {
            "question": "What is the meaning of the idiom 'piece of cake'?",
            "a": "a slice of dessert",
            "b": "something very easy",
            "c": "something sweet",
            "d": "a type of food",
            "answer": "B"
        },
        {
            "question": "Choose the correct plural form of 'child':",
            "a": "childs",
            "b": "childes",
            "c": "children",
            "d": "childrens",
            "answer": "C"
        },
        {
            "question": "Which word is an adverb?",
            "a": "quick",
            "b": "quickly",
            "c": "quickness",
            "d": "quicken",
            "answer": "B"
        },
        {
            "question": "What is the present perfect form of 'write'?",
            "a": "wrote",
            "b": "written",
            "c": "have wrote",
            "d": "have written",
            "answer": "D"
        },
        {
            "question": "Choose the correct possessive form: 'This is ___ car.'",
            "a": "John's",
            "b": "Johns",
            "c": "Johnes",
            "d": "John is",
            "answer": "A"
        },
        {
            "question": "Which sentence uses the correct verb tense?",
            "a": "I am study English",
            "b": "I studying English",
            "c": "I am studying English",
            "d": "I study English now",
            "answer": "C"
        },
        {
            "question": "What is the correct question tag: 'You are a student, ___?'",
            "a": "aren't you",
            "b": "are you",
            "c": "isn't you",
            "d": "is you",
            "answer": "A"
        },
        {
            "question": "Select the correct relative pronoun: 'The person ___ called yesterday is my teacher.'",
            "a": "who",
            "b": "which",
            "c": "what",
            "d": "whose",
            "answer": "A"
        },
        {
            "question": "Choose the correct modal verb: 'You ___ smoke in the hospital.'",
            "a": "don't have to",
            "b": "mustn't",
            "c": "shouldn't",
            "d": "couldn't",
            "answer": "B"
        },
        {
            "question": "What is the correct passive voice: 'They build houses.'",
            "a": "Houses build",
            "b": "Houses are build",
            "c": "Houses are built",
            "d": "Houses were build",
            "answer": "C"
        }
    ]
    # Shuffle the questions to add randomness
    random.shuffle(fallback_questions)
    return fallback_questions

def parse_question(text):
    """
    Safely parses a question from generated text.
    Returns None if the format is invalid.
    """
    try:
        # Clean the text first
        text = clean_text(text)
        logger.debug(f"Attempting to parse cleaned question text: {text}")
        
        # Clean up the text format
        text = text.replace('\n', ' ').strip()
        text = re.sub(r'\s+', ' ', text)
        
        # Use regex to extract components with more flexible matching
        pattern = r"Question:\s*([^A)]+)A\)\s*([^B)]+)B\)\s*([^C)]+)C\)\s*([^D)]+)D\)\s*([^A]+)Answer:\s*([ABCD])"
        match = re.search(pattern, text, re.DOTALL)
        
        if not match:
            logger.warning(f"Failed to match pattern in text: {text}")
            return None
            
        # Extract and validate each component
        question = clean_text(match.group(1).strip())
        option_a = clean_text(match.group(2).strip())
        option_b = clean_text(match.group(3).strip())
        option_c = clean_text(match.group(4).strip())
        option_d = clean_text(match.group(5).strip())
        answer = match.group(6).strip()
        
        # Additional validation
        if not all([question, option_a, option_b, option_c, option_d, answer]):
            logger.warning("One or more components are empty")
            return None
            
        if answer not in ['A', 'B', 'C', 'D']:
            logger.warning(f"Invalid answer: {answer}")
            return None
            
        return {
            'question': question,
            'a': option_a,
            'b': option_b,
            'c': option_c,
            'd': option_d,
            'answer': answer
        }
    except Exception as e:
        logger.error(f"Error parsing question text: {e}")
        return None

def generate_questions_with_cohere():
    """
    Generates English questions using Cohere AI API.
    """
    try:
        # Initialize Cohere client
        co = cohere.Client(settings.COHERE_API_KEY)
        
        questions = []
        topics = [
            {"topic": "grammar past tense", "example": "What is the past tense of 'eat'?", "correct": "ate", "wrong": ["eated", "eaten", "eating"]},
            {"topic": "vocabulary synonyms", "example": "What is a synonym for 'happy'?", "correct": "joyful", "wrong": ["sad", "angry", "tired"]},
            {"topic": "prepositions usage", "example": "The book is ___ the table.", "correct": "on", "wrong": ["in", "at", "by"]},
            {"topic": "common idioms", "example": "What does 'break a leg' mean?", "correct": "good luck", "wrong": ["get hurt", "dance well", "take a break"]},
            {"topic": "verb forms", "example": "She ___ to school every day.", "correct": "goes", "wrong": ["go", "going", "gone"]}
        ]
        
        prompt_template = """You are an English teacher creating multiple choice questions. Create ONE question exactly following this format:

Question: {example_type}
A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}
Answer: {correct_letter}

STRICT RULES:
1. Use EXACTLY this format with "Question:", "A)", "B)", "C)", "D)", and "Answer:"
2. Topic: {topic}
3. Question must be clear and simple
4. Options must be reasonable
5. Answer MUST be exactly one letter: A, B, C, or D
6. No explanations or additional text

Example of CORRECT format:
Question: What is the past tense of "go"?
A) goed
B) went
C) gone
D) going
Answer: B

Now create ONE new question about {topic} following the EXACT format above. Do not include any other text."""

        for _ in range(4):  # Generate 4 questions for each topic
            for topic_info in topics:
                # Prepare example options
                options = [topic_info["correct"]] + topic_info["wrong"]
                random.shuffle(options)
                correct_index = options.index(topic_info["correct"])
                correct_letter = chr(65 + correct_index)  # Convert 0-3 to A-D
                
                # Generate with Cohere
                response = co.generate(
                    model='command',
                    prompt=prompt_template.format(
                        topic=topic_info["topic"],
                        example_type=topic_info["example"],
                        option_a=options[0],
                        option_b=options[1],
                        option_c=options[2],
                        option_d=options[3],
                        correct_letter=correct_letter
                    ),
                    max_tokens=200,
            temperature=0.7,
                    k=0,
                    stop_sequences=["\n\n", "Now create"],
                    num_generations=1,
                )
                
                result = response.generations[0].text.strip()
                logger.debug(f"Generated text for {topic_info['topic']}: {result}")
                
                question_data = parse_question(result)
                if question_data:
                    questions.append(question_data)
                else:
                    logger.warning(f"Failed to parse question for topic {topic_info['topic']}")
                    continue
        
        # Ensure we have enough questions or fall back
        if len(questions) < 15:
            logger.warning(f"Only generated {len(questions)} valid questions, using fallback")
            return None
            
        return questions[:20]  # Return only 20 questions
    except Exception as e:
        logger.error(f"Error in Cohere generation: {e}")
        return None

def generate_daily_questions():
    """
    Generates 20 English multiple-choice questions using Cohere AI
    or falls back to predefined questions if generation fails.
    """
    today = timezone.now().date()

    try:
        # Delete any existing questions for today
        EnglishQuestion.objects.filter(created_date=today).delete()
        logger.info(f"Deleted existing questions for {today}")

        # Try generating questions with Cohere
        questions_data = generate_questions_with_cohere()

        # Use fallback if generation failed
        if not questions_data:
            logger.info("Using fallback questions due to generation failure")
            questions_data = get_fallback_questions()

        # Save questions to database
        created_questions = []
        for i, q_data in enumerate(questions_data, 1):
            # Clean all text fields before saving
            cleaned_data = {
                'question_text': clean_text(q_data['question']),
                'option_a': clean_text(q_data['a']),
                'option_b': clean_text(q_data['b']),
                'option_c': clean_text(q_data['c']),
                'option_d': clean_text(q_data['d']),
                'correct_answer': q_data['answer'],
                'created_date': today
            }
            
            # Validate question data
            if not all(cleaned_data.values()):
                logger.error(f"Question {i} has empty fields after cleaning")
                continue

            if cleaned_data['correct_answer'] not in ['A', 'B', 'C', 'D']:
                logger.error(f"Question {i} has invalid answer: {cleaned_data['correct_answer']}")
                continue

            question = EnglishQuestion(**cleaned_data)
            created_questions.append(question)

        # Bulk create all questions
        if created_questions:
            EnglishQuestion.objects.bulk_create(created_questions)
            logger.info(f"Successfully created {len(created_questions)} questions for {today}")
            return len(created_questions)
        else:
            logger.error("No valid questions were created")
        return 0

    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        return 0 