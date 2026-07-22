from django_q.tasks import schedule
from django.utils import timezone
from apps.tournaments.models import Tournament
from apps.schedules.models import MatchReminder
from apps.newsletter.models import NewsletterCampaign
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def update_tournament_status():
    """Update tournament statuses"""
    now = timezone.now()
    
    # Registration ending soon - set to LIVE
    tournaments = Tournament.objects.filter(
        status='REGISTRATION',
        registration_end__lt=now
    )
    for tournament in tournaments:
        tournament.status = 'LIVE'
        tournament.save()
        logger.info(f'Updated tournament: {tournament.name} to LIVE')
    
    # Completed tournaments
    completed = Tournament.objects.filter(
        status='LIVE',
        end_date__lt=now
    )
    for tournament in completed:
        tournament.status = 'COMPLETED'
        tournament.save()
        logger.info(f'Updated tournament: {tournament.name} to COMPLETED')
    
    return f'Updated {tournaments.count()} tournaments to LIVE, {completed.count()} to COMPLETED'


def send_match_reminders():
    """Send reminders for upcoming matches"""
    from apps.notifications.models import Notification
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    now = timezone.now()
    reminder_time = now + timedelta(hours=2)
    
    # Find matches starting in 2 hours
    from apps.schedules.models import MatchSchedule
    matches = MatchSchedule.objects.filter(
        scheduled_start__lte=reminder_time,
        scheduled_start__gte=now,
        status='SCHEDULED'
    )
    
    sent_count = 0
    for match in matches:
        for user in [match.match.player1, match.match.player2]:
            if user:
                Notification.objects.create(
                    user=user,
                    type='MATCH',
                    title='Match Starting Soon',
                    message=f'Your match in {match.tournament.name} starts in 2 hours!',
                    channel='IN_APP'
                )
                sent_count += 1
    
    return f'Sent {sent_count} match reminders'


def send_newsletter_digest():
    """Send daily newsletter digest"""
    from apps.newsletter.models import NewsletterCampaign, NewsletterSubscription
    from django.core.mail import send_mail
    from django.conf import settings
    
    # Get active subscribers
    subscribers = NewsletterSubscription.objects.filter(status='ACTIVE')
    
    # Get campaigns scheduled for today
    today = timezone.now().date()
    campaigns = NewsletterCampaign.objects.filter(
        scheduled_for__date=today,
        status='SCHEDULED'
    )
    
    sent_count = 0
    for campaign in campaigns:
        for subscriber in subscribers:
            try:
                send_mail(
                    campaign.subject,
                    campaign.content,
                    settings.DEFAULT_FROM_EMAIL,
                    [subscriber.email],
                    fail_silently=True
                )
                sent_count += 1
            except:
                pass
        campaign.status = 'SENT'
        campaign.save()
    
    return f'Sent {sent_count} newsletter emails'


def cleanup_expired_data():
    """Clean up expired data"""
    from apps.payments.models import PaystackTransaction
    from apps.legal.models import UserConsent
    
    # Clean up expired transactions
    expired_time = timezone.now() - timedelta(days=30)
    expired_transactions = PaystackTransaction.objects.filter(
        status='PENDING',
        created_at__lt=expired_time
    )
    expired_transactions.update(status='CANCELLED')
    
    # Clean up expired consents
    expired_consents = UserConsent.objects.filter(
        is_active=True,
        expires_at__lt=timezone.now()
    )
    expired_consents.update(is_active=False)
    
    return f'Cleaned up {expired_transactions.count()} transactions, {expired_consents.count()} consents'


def run_all_scheduled_tasks():
    """Run all scheduled tasks"""
    results = []
    results.append(update_tournament_status())
    results.append(send_match_reminders())
    results.append(send_newsletter_digest())
    results.append(cleanup_expired_data())
    return '\n'.join(results)


# Schedule tasks
def schedule_tasks():
    """Schedule all recurring tasks"""
    from django_q.models import Schedule
    
    schedules = [
        ('Update tournament status', 'apps.tasks.scheduled_tasks.update_tournament_status', '0 0 * * *'),
        ('Send match reminders', 'apps.tasks.scheduled_tasks.send_match_reminders', '*/30 * * * *'),
        ('Send newsletter digest', 'apps.tasks.scheduled_tasks.send_newsletter_digest', '0 9 * * *'),
        ('Cleanup expired data', 'apps.tasks.scheduled_tasks.cleanup_expired_data', '0 2 * * *'),
        ('Run all tasks', 'apps.tasks.scheduled_tasks.run_all_scheduled_tasks', '0 1 * * *'),
    ]
    
    for name, func, cron in schedules:
        Schedule.objects.get_or_create(
            name=name,
            defaults={
                'func': func,
                'schedule_type': Schedule.CRON,
                'cron': cron,
                'repeats': -1,
                'enabled': True,
            }
        )
    
    return f'Scheduled {len(schedules)} tasks'
