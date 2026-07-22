from django.core.management.base import BaseCommand
from apps.tasks.scheduled_tasks import schedule_tasks

class Command(BaseCommand):
    help = 'Schedule Django-Q tasks'

    def handle(self, *args, **options):
        result = schedule_tasks()
        self.stdout.write(self.style.SUCCESS(result))
