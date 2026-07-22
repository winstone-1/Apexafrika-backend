from django.core.management.base import BaseCommand
from django_q.models import Schedule

class Command(BaseCommand):
    help = 'Schedule Django-Q tasks'

    def handle(self, *args, **options):
        tasks = [
            {
                'name': 'Update tournament status',
                'func': 'apps.tasks.scheduled_tasks.update_tournament_status',
                'cron': '0 0 * * *'
            },
            {
                'name': 'Send match reminders',
                'func': 'apps.tasks.scheduled_tasks.send_match_reminders',
                'cron': '*/30 * * * *'
            },
            {
                'name': 'Send newsletter digest',
                'func': 'apps.tasks.scheduled_tasks.send_newsletter_digest',
                'cron': '0 9 * * *'
            },
            {
                'name': 'Cleanup expired data',
                'func': 'apps.tasks.scheduled_tasks.cleanup_expired_data',
                'cron': '0 2 * * *'
            },
            {
                'name': 'Run all scheduled tasks',
                'func': 'apps.tasks.scheduled_tasks.run_all_scheduled_tasks',
                'cron': '0 1 * * *'
            },
        ]

        created_count = 0
        for task in tasks:
            schedule, created = Schedule.objects.get_or_create(
                name=task['name'],
                defaults={
                    'func': task['func'],
                    'schedule_type': Schedule.CRON,
                    'cron': task['cron'],
                    'repeats': -1,
                    'enabled': True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"✅ Scheduled: {task['name']}")
            else:
                self.stdout.write(f"⏭️ Already exists: {task['name']}")

        self.stdout.write(self.style.SUCCESS(f"\n✅ Scheduled {created_count} tasks"))
