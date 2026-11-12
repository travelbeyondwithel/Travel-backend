from datetime import timedelta

from django.db import models
from django.db.models import Count, Sum
from django.utils import timezone

from ..models import ArticleVisit


def get_article_analytics(article):
    """
    Calculate visit count and total time spent for an article.
    
    Periods:
    - today
    - last 7 days
    - last 30 days
    - last 12 months
    
    Return seconds for time spent
    """
    
    now = timezone.now()
    
    today_start = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )
    
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)
    twelve_months_ago = now - timedelta(days=365)
    
    visits = ArticleVisit.objects.filter(article=article)
    
    analytics = visits.aggregate(
        # -------------------------------------------
        # Today
        # -------------------------------------------
        today_visits=Count(
            'id',
            filter=models.Q(started_at__gte=today_start),
        ),
        today_time=Sum(
            'duration',
            filter=models.Q(started_at__gte=today_start),
        ),
        
        # -------------------------------------------
        # Last 7 Days
        # -------------------------------------------
        last_7_days_visits=Count(
            'id',
            filter=models.Q(started_at__gte=seven_days_ago),
        ),
        last_7_days_time=Sum(
            'duration',
            filter=models.Q(started_at__gte=seven_days_ago),
        ),
        
        # -------------------------------------------
        # Last 30 Days
        # -------------------------------------------
        last_30_days_visits=Count(
            'id',
            filter=models.Q(started_at__gte=thirty_days_ago),
        ),
        last_30_days_time=Sum(
            'duration',
            filter=models.Q(started_at__gte=thirty_days_ago),
        ),
        
        # -------------------------------------------
        # Last 12 Months
        # -------------------------------------------
        last_12_months_visits=Count(
            'id',
            filter=models.Q(started_at__gte=twelve_months_ago),
        ),
        last_12_months_time=Sum(
            'duration',
            filter=models.Q(started_at__gte=twelve_months_ago),
        ),
    )
    
    return {
        'today': {
            'visits': analytics['today_visits'] or 0,
            'time_spent': analytics['today_time'] or 0,
        },
        
        'last_7_days': {
            'visits': analytics['last_7_days_visits'] or 0,
            'time_spent': analytics['last_7_days_time'] or 0,
        },
        
        'last_30_days': {
            'visits': analytics['last_30_days_visits'] or 0,
            'time_spent': analytics['last_30_days_time'] or 0,
        },
        
        'last_12_months': {
            'visits': analytics['last_12_months_visits'] or 0,
            'time_spent': analytics['last_12_months_time'] or 0,
        },
        
    }
    
def format_duration(seconds):
    """
    Covert seconds into a readable duration.
    
    Examples:
    45      _> 45s
    120      _> 2m
    3660      _> 1h 1m
    90000      _> 1d 1h
    """
    
    seconds = int(seconds or 0)
    
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 30)
    
    parts = []
    
    if days:
        parts.append(f'{days}d')
    
    if hours:
        parts.append(f'{hours}h')
    
    if minutes:
        parts.append(f'{minutes}m')
    
    if seconds and len(parts) < 2:
        parts.append(f'{seconds}s')
        
    return " ".join(parts) if parts else "0s"