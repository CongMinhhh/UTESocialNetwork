from django.core.management.base import BaseCommand
from django.utils import timezone
from core.quiz_views import generate_daily_quiz
from core.quiz_models import Quiz

class Command(BaseCommand):
    help = 'Generates a new daily quiz'

    def handle(self, *args, **options):
        # Check if a quiz already exists for today
        today = timezone.now().date()
        if Quiz.objects.filter(date=today).exists():
            self.stdout.write(self.style.WARNING('A quiz already exists for today'))
            return

        # Generate new quiz
        quiz = generate_daily_quiz()
        if quiz:
            self.stdout.write(self.style.SUCCESS(f'Successfully generated quiz for {today}'))
        else:
            self.stdout.write(self.style.ERROR('Failed to generate quiz')) 