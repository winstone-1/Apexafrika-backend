from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from apps.tournaments.models import Tournament, Match
from apps.players.models import PlayerStats
from apps.payments.models import PaystackTransaction

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def platform_analytics(request):
    """Get platform-wide analytics"""
    
    # Date range
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Tournament stats
    total_tournaments = Tournament.objects.count()
    active_tournaments = Tournament.objects.filter(status='LIVE').count()
    completed_tournaments = Tournament.objects.filter(status='COMPLETED').count()
    tournaments_by_game = list(Tournament.objects.values('game').annotate(count=Count('id')).order_by('-count'))
    
    # Player stats
    total_players = PlayerStats.objects.count()
    top_players = list(PlayerStats.objects.select_related('player').order_by('-win_rate')[:10])
    
    # Revenue stats (using Paystack)
    total_revenue = PaystackTransaction.objects.filter(
        status='COMPLETED',
        transaction_type='PAYMENT',
        created_at__gte=start_date
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_prizes = PaystackTransaction.objects.filter(
        status='COMPLETED',
        transaction_type='PRIZE',
        created_at__gte=start_date
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Growth stats
    new_tournaments = Tournament.objects.filter(created_at__gte=start_date).count()
    new_players = PlayerStats.objects.filter(player__date_joined__gte=start_date).count()
    
    return Response({
        'summary': {
            'total_tournaments': total_tournaments,
            'active_tournaments': active_tournaments,
            'completed_tournaments': completed_tournaments,
            'total_players': total_players,
            'total_revenue': float(total_revenue) if total_revenue else 0,
            'total_prizes': float(total_prizes) if total_prizes else 0,
        },
        'growth': {
            'new_tournaments': new_tournaments,
            'new_players': new_players,
            'days': days,
        },
        'tournaments_by_game': tournaments_by_game,
        'top_players': [
            {
                'username': stats.player.username,
                'gamer_tag': stats.player.gamer_tag,
                'win_rate': stats.win_rate,
                'total_wins': stats.total_wins,
                'tournaments_won': stats.tournaments_won,
            }
            for stats in top_players
        ]
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def tournament_analytics(request, tournament_id):
    """Get analytics for a specific tournament"""
    
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return Response({'error': 'Tournament not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Participant stats
    participants = tournament.participants.all()
    total_participants = participants.count()
    checked_in = participants.filter(status='CHECKED_IN').count()
    
    # Match stats
    matches = tournament.matches.all()
    total_matches = matches.count()
    completed_matches = matches.filter(status='COMPLETED').count()
    
    # Top performers
    top_performers = list(
        participants.select_related('player')
        .order_by('-points', '-wins')[:5]
        .values('player__username', 'player__gamer_tag', 'wins', 'points', 'rank')
    )
    
    # Payment stats
    payment_stats = PaystackTransaction.objects.filter(
        tournament=tournament,
        status='COMPLETED'
    ).aggregate(
        total_payments=Sum('amount'),
        count=Count('id')
    )
    
    return Response({
        'tournament': {
            'id': tournament.id,
            'name': tournament.name,
            'game': tournament.game,
            'status': tournament.status,
            'prize_pool': float(tournament.prize_pool) if tournament.prize_pool else 0,
        },
        'stats': {
            'total_participants': total_participants,
            'checked_in': checked_in,
            'total_matches': total_matches,
            'completed_matches': completed_matches,
            'completion_rate': (completed_matches / total_matches * 100) if total_matches > 0 else 0,
        },
        'top_performers': top_performers,
        'payments': {
            'total_payments': float(payment_stats['total_payments'] or 0),
            'payment_count': payment_stats['count'] or 0,
        }
    })
