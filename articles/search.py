from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import (
    Article,
    TravelGuide,
    Event,
    Destination,
)

class SearchView(APIView):

    def get(self, request):

        query = request.GET.get("q", "").strip()

        # ==========================================
        # EMPTY SEARCH
        # ==========================================

        if not query:

            return Response({
                "query": "",
                "results": []
            })

        # ==========================================
        # MINIMUM SEARCH LENGTH
        # ==========================================

        if len(query) < 2:

            return Response({
                "query": query,
                "results": []
            })

        results = []

        # ==========================================
        # ARTICLES
        # ==========================================

        articles = Article.objects.filter(
            status="published"
        ).filter(

            Q(title__icontains=query) |
            Q(subtitle__icontains=query) |
            Q(introduction__icontains=query) |
            Q(content__icontains=query) |
            Q(seo_title__icontains=query) |
            Q(meta_description__icontains=query) |
            Q(focus_keyword__icontains=query)

        ).distinct()[:10]

        for article in articles:

            results.append({

                "id": article.id,

                "type": "article",

                "title": article.title,

                "slug": article.slug,

                "introduction": article.introduction,

                "hero_image": (
                    article.hero_image.url
                    if article.hero_image
                    else None
                ),

            })

        # ==========================================
        # TRAVEL GUIDES
        # ==========================================

        travel_guides = TravelGuide.objects.filter(
            status="published"
        ).filter(

            Q(title__icontains=query) |
            Q(introduction__icontains=query) |
            Q(content__icontains=query) |
            Q(seo_title__icontains=query) |
            Q(meta_description__icontains=query) |
            Q(focus_keyword__icontains=query)

        ).distinct()[:10]

        for guide in travel_guides:

            results.append({

                "id": guide.id,

                "type": "travel_guide",

                "title": guide.title,

                "slug": guide.slug,

                "introduction": guide.introduction,

                "hero_image": (
                    guide.hero_image.url
                    if guide.hero_image
                    else None
                ),

            })

        # ==========================================
        # EVENTS
        # ==========================================

        events = Event.objects.filter(
            status="published"
        ).filter(

            Q(title__icontains=query) |
            Q(introduction__icontains=query) |
            Q(content__icontains=query) |
            Q(venue__icontains=query) |
            Q(location__icontains=query) |
            Q(organizer__icontains=query) |
            Q(seo_title__icontains=query) |
            Q(meta_description__icontains=query) |
            Q(focus_keyword__icontains=query)

        ).distinct()[:10]

        for event in events:

            results.append({

                "id": event.id,

                "type": "event",

                "title": event.title,

                "slug": event.slug,

                "introduction": event.introduction,

                "hero_image": (
                    event.hero_image.url
                    if event.hero_image
                    else None
                ),

            })

        # ==========================================
        # DESTINATIONS
        # ==========================================

        destinations = Destination.objects.filter(
            status="published"
        ).filter(

            Q(title__icontains=query) |
            Q(introduction__icontains=query) |
            Q(content__icontains=query) |
            Q(country__icontains=query) |
            Q(city__icontains=query) |
            Q(seo_title__icontains=query) |
            Q(meta_description__icontains=query) |
            Q(focus_keyword__icontains=query)

        ).distinct()[:10]

        for destination in destinations:

            results.append({

                "id": destination.id,

                "type": "destination",

                "title": destination.title,

                "slug": destination.slug,

                "introduction": destination.introduction,

                "country": destination.country,

                "city": destination.city,

                "hero_image": (
                    destination.hero_image.url
                    if destination.hero_image
                    else None
                ),

            })

        # ==========================================
        # RESPONSE
        # ==========================================

        return Response({

            "query": query,

            "count": len(results),

            "results": results

        })