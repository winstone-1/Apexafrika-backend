from django_q.tasks import schedule
from django.utils import timezone
from apps.tournaments.models import Tournament
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
    count = 0
    for tournament in tournaments:
        tournament.status = 'LIVE'
        tournament.save()
        count += 1
        logger.info(f'Updated tournament: {tournament.name} to LIVE')
    
    return f'Updated {count} tournaments to LIVE'


def send_match_reminders():
    """Send reminders for upcoming matches"""
    from apps.notifications.models import Notification
    from apps.schedules.models import MatchSchedule
    
    now = timezone.now()
    reminder_time = now + timedelta(hours=2)
    
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
    
    subscribers = NewsletterSubscription.objects.filter(status='ACTIVE')
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
    
    expired_time = timezone.now() - timedelta(days=30)
    expired_transactions = PaystackTransaction.objects.filter(
        status='PENDING',
        created_at__lt=expired_time
    )
    count1 = expired_transactions.update(status='CANCELLED')
    
    expired_consents = UserConsent.objects.filter(
        is_active=True,
        expires_at__lt=timezone.now()
    )
    count2 = expired_consents.update(is_active=False)
    
    return f'Cleaned up {count1} transactions, {count2} consents'


def run_all_scheduled_tasks():
    """Run all scheduled tasks"""
    results = []
    results.append(update_tournament_status())
    results.append(send_match_reminders())
    results.append(send_newsletter_digest())
    results.append(cleanup_expired_data())
    return '\n'.join(results)
