from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class QuizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quiz'

    def ready(self):
        if not settings.DEBUG:  # Only run scheduler in production
            scheduler = BackgroundScheduler()
            
            # Import the task function here to avoid circular imports
            from .tasks import generate_daily_questions
            
            # Add the job to run at 00:05 every day
            scheduler.add_job(
                generate_daily_questions,
                trigger=CronTrigger(hour=0, minute=5),
                id='generate_daily_questions',
                name='Generate daily English questions',
                replace_existing=True
            )
            
            try:
                logger.info("Starting APScheduler...")
                scheduler.start()
            except Exception as e:
                logger.error(f"Error starting APScheduler: {e}")
