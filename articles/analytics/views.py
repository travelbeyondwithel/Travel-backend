from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Article, ArticleVisit

class ArticleVisitStartView(APIView):
    """
    Start tracking a visitor reading an article.
    
    A visit_token is supplied by the frontend so that duplicate
    request from React StrictMode do not create duplicate visits.
    """

    def post(self, request, slug):
        
        try:
            article = Article.objects.get(slug=slug)
            
        except Article.DoesNotExist:
            return Response(
                {"detail": "Article not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        visit_token = request.data.get(
            'visit_token'
        )

        # Make sure the Django session has a session key.
        
        if not visit_token:
            
            return Response(
                {
                    'detail': 'visit_token is required.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not request.session.session_key:
            
            request.session.create()
            
        session_key = request.session.session_key

        visit, created = ArticleVisit.objects.get_or_create(
            visit_token=visit_token,
            defaults={
                'article': article,
                'session_key': session_key,
            }
        )

        return Response(
            {
                "visit_id": visit.id,
                'visit_token': str(
                    visit.visit_token
                ),
                "article_id": article.id,
                "started_at": visit.started_at,
                'created': created,
            },
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            )
        )

class ArticleVisitEndView(APIView):
    """
    End an article visit and calculate time spent.
    """

    def post(self, request, visit_id):
        visit_token = request.data.get("visit_token")

        if not visit_token:
            return Response(
                {"detail": "Visit token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            visit = ArticleVisit.objects.get(
                id=visit_id,
                visit_token=visit_token,
            )

        except ArticleVisit.DoesNotExist:
            return Response(
                {"detail": "Visit not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Don't allow a visit to be ended twice.
        if visit.ended_at is not None:
            return Response(
                {
                    "visit_id": visit.id,
                    "duration": visit.duration,
                },
                status=status.HTTP_200_OK,
            )

        ended_at = timezone.now()

        duration = int(
            (ended_at - visit.started_at).total_seconds()
        )

        # Prevent negative duration.
        duration = max(duration, 0)

        visit.ended_at = ended_at
        visit.duration = duration

        visit.save(
            update_fields=[
                "ended_at",
                "duration",
            ]
        )

        return Response(
            {
                "visit_id": visit.id,
                "duration": visit.duration,
                "ended_at": visit.ended_at,
            },
            status=status.HTTP_200_OK,
        )