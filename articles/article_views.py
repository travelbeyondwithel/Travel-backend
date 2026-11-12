import hashlib

# from datetime import timedelta

from django.conf import settings
# from django.db import transaction
# from django.utils import timezone
from django.db.models import Q, F

from .models import Article, ArticleView

# VIEW_WINDOW = timedelta(hours=24)

def get_client_ip(request):
    
    # In production, use the proxy/CDN configuration
    # rather than blindly trusting X-Forwarded-For.
    
    # if getattr(
    #     settings,
    #     'TRUST_PROXY_IP',
    #     False
    # ):
        
    forwarded_for = request.META.get(
        'HTTP_X_FORWARDED_FOR'
    )
        
    if forwarded_for:
        return forwarded_for.split('', '')[0].strip()
        
    return request.META.get(
        'REMOTE_ADDR',
        ''
    )


def hash_ip(ip_address):
    
    if not ip_address:
        return ''
    
    return hashlib.sha256(
        ip_address.encode('utf-8')
    ).hexdigest()


def record_article_view(article, request):
    
    """
    One lifetime view per visitor per article.
    
    A visitor is identified primary by browser_id,
    with IP hash as a fallback.
    
    If either an existing browser_id OR an existing IP hash
    has already viewed this article, we do Not create another view.
    
    """
    
    browser_id = request.headers.get(
        "X-Browser_ID",
        ""
    ).strip()
    
    ip_address = get_client_ip(request)
    ip_hash = hash_ip(ip_address)


    # --------------
    # Check whether this visitor has already viewed
    # this article using EITHER identifier.
    # --------------


    existing_view = ArticleView.objects.filter(
        article=article
    ).filter(
        Q(browser_id=browser_id, browser_id__gt='')
        | Q(ip_hash=ip_hash, ip_hash__gt='')
    ).first()

    if existing_view:
        return False

    # --------
    # No existing record - create ONE
    # --------

    ArticleView.objects.create(
        article=article,
        browser_id=browser_id,
        ip_hash=ip_hash,
    )

    # --------
    # Increase total article views once
    # --------

    Article.objects.filter(
        pk=article.pk
    ).update(
        views=F('views') + 1
    )

    return True
        

