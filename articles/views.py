from django.conf import settings
from django.shortcuts import render
# from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import generics, status, serializers
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .article_views import record_article_view
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from . models import (
    Article,
    Category,
    Comment,
    ArticleLike,
    Destination,
    TravelGuide,
    Event,
    Subcategory,
    DestinationContinent,
    Profile,
    About,
    Contact,
    Hero,
    TravelResource,
    PartnerSubmission,
    WebsitePage,
)

from .serializers import (
    ArticleListSerializer,
    ArticleLikeSerializer,
    ArticleCreateSerializer,
    ArticleDetailSerializer,
    CategorySerializer,
    CommentSerializer,
    HomeArticleSerializer,
    DestinationSerializer,
    DestinationDirectorySerializer,
    TravelGuideSerializer,
    EventSerializer,
    ProfileSerializer,
    AboutSerializer,
    ContactSerializer,
    HeroSerializer,
    TravelResourceSerializer,
    PartnerSubmissionSerializer,
    WebsitePageSerializer,
)

# Create your views here.


class HomeAPIView(APIView):
    
    def get(self, request):
        
        featured = (
            Article.objects
            .filter(
                is_featured=True,
                status='published'
            )
            .exclude(hero_image='')
            .order_by('-published_at')[:3]
        )
        
        # featured_articles = (
        #     Article.objects
        #     .filter(is_featured=True, status='published')
        #     .exclude(id=featured.id if featured else None)
        #     .order_by('-published_at')[:3]
        #     .first()
        # )
        
        latest = (
        Article.objects
        .filter(status='published')
        .exclude(id=featured.first().id if featured.exists() else None)
        .order_by('-published_at')[:6]
        )
        
        popular = (
        Article.objects
        .filter(status='published')
        .order_by('-views')[:6]
        )
        
        data = {
            'featured': HomeArticleSerializer(featured, many=True).data,
            'latest': HomeArticleSerializer(latest, many=True).data,
            'popular': HomeArticleSerializer(popular, many=True).data,
        }
        
        categories = Category.objects.all()
        
        return Response(data)
            
            # 'featured':
            #     HomeArticleSerializer(featured).data
            #     if featured else None,
                
            # 'latest':
            #     HomeArticleSerializer(
            #         latest,
            #         many=True
            #     ).data,
            
            # 'latest': [
            #     {
            #         'id': article.id,
            #         'title': article.title,
            #         'subtitle': article.subtitle,
            #         'slug': article.slug,
            #     }
            #     for article in latest
            # ]
                
            # 'popular':
            #     HomeArticleSerializer(
            #         popular,
            #         many=True
            #     ).data,
                
            # 'categories': [
            #     {
            #         'id': c.id,
            #         'name': c.name,
            #         'slug': c.slug,
            #     }
            #     for c in categories
            # ]
                # CategorySerializer(
                #     categories,
                #     many=True
                # ).data
        # })

class SubcategoryArticlesView(ListAPIView):
    
    serializer_class = ArticleListSerializer
    
    def get_queryset(self):
        
        slug = self.kwargs.get('slug')
        
        return Article.objects.filter(
            status='published',
            subcategory__slug=slug
        ).select_related(
            'author',
            'category', 
            'subcategory', 
            'destination'
        )




class ArticleSlugResolverView(APIView):

    def get(self, request, slug):

        # ==========================
        # Check Article first
        # ==========================

        article = Article.objects.filter(
            slug=slug,
            status='published'
        ).first()

        if article:

            return Response({
                'type': 'article',
                'slug': article.slug,
            })

        # ==========================
        # Check Subcategory
        # ==========================

        subcategory = Subcategory.objects.filter(
            slug=slug
        ).select_related(
            'category'
        ).first()

        if subcategory:

            return Response({
                'type': 'subcategory',

                'slug': subcategory.slug,

                'subcategory': {
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'slug': subcategory.slug,
                    
                    'category': {
                        'id': subcategory.category.id,
                        'name': subcategory.category.name,
                        'slug': subcategory.category.slug,
                    }
                }
            })

        # ==========================
        # Nothing found
        # ==========================

        return Response(
            {
                'detail': 'Not found.'
            },
            status=status.HTTP_404_NOT_FOUND
        )




class ArticleListView(generics.ListAPIView):
    
    serializer_class = ArticleListSerializer
    permission_classes = [AllowAny]
    
    queryset = (
        Article.objects
        .filter(status='published')
        .select_related(
            'category',
            'destination',
            'author',
            'travel_guide',
        )
        .prefetch_related(
            'gallery',
            'quick_tips',
            'faqs',
            'comments',
            'likes',
            'tags',
        )
    )



class ArticleDetailView(generics.RetrieveAPIView):
    
    serializer_class = ArticleDetailSerializer
    
    permission_classes = [AllowAny]
    
    lookup_field = 'slug'
    
    queryset = (
        Article.objects.filter(status='published')
        .select_related('category', 'author')
        .prefetch_related(
            'sections',
            'gallery',
            'quick_tips',
            'faqs',
            'comments',
            'likes',
            'tags',
        )
    )
    
    def retrieve(self, request, slug):
        
        try:
            
            article = Article.objects.get(
                slug=slug,
                status='published',
            )
            
        except Article.DoesNotExist:
            
            return Response(
                {
                    'detail': 'Article not found.'
                },
                status=404,
            )
            
        # browser_id = request.headers.get(
        #     'X-Browser-ID',
        #     ''
        # )
        
        # Record the visitor
        
        record_article_view(article, request)
        
        serializer = ArticleDetailSerializer(article)
        
        return Response(
            serializer.data
        )



class CategoryListView(generics.ListAPIView):
    
    serializer_class = CategorySerializer
    
    permission_classes = [AllowAny]
    
    queryset = Category.objects.all()
    


class LikeArticleView(APIView):
    
    def post(self, request):
    
        article = request.data.get('article')
        browser_id = request.data.get('browser_id')
        
        already_liked = Article.objects.filter(
            article=article,
            browser_id=browser_id
        ).exists()
        
        if already_liked:
            return Response(
                {
                'message': 'Already liked.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        ArticleLike.objects.create(
            article=article,
            browser_id=browser_id
        )
        
        return Response(
            {
                'message': 'Liked!'
            },
            status = status.HTTP_201_CREATED
        )

class CommentListView(generics.ListAPIView):
    
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]
    

    def get_queryset(self):
        
        slug = self.kwargs['slug']
        
        article = Article.objects.get(slug=slug)
        
        return Comment.objects.filter(
            article=article,
            approved=True
        ).order_by('-created_at')



class CommentCreateView(generics.CreateAPIView):
    
    serializer_class = CommentSerializer
    
    permission_classes = [AllowAny]
    
    queryset = Comment.objects.all()
    
    def perform_create(self, serializer):
        article_slug = self.request.data.get('article_slug')
        
        if not article_slug:
            raise serializers.ValidationError({
                'article': 'Article slug is required'
            })
            
        try:
            
            article = Article.objects.get(
                slug=article_slug
            )
            
        except Article.DoesNotExist:
            raise serializers.ValidationError({
                'article': 'Article not found.'
            })
        
        serializer.save(
            article=article,
            approved=True
        )




class ArticleLikeView(generics.GenericAPIView):
    
    permission_classes = [AllowAny]
    
    def post(self, request, slug):
        
        browser_id = request.headers.get(
            'X-Browser_ID'
        )
        
        if not browser_id:
            
            return Response(
                {
                    'detail': 'Browser ID is Required.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        try:
            
            article = Article.objects.get(
                slug=slug,
                status='published',
            )
            
        except Article.DoesNotExist:
            
            return Response(
                {
                    'detail':
                        'Article not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        like, created = ArticleLike.objects.get_or_create(
            article=article,
            browser_id=browser_id,
        )
        
        if not created:
            # Already liked - unlike
            like.delete()
            
            liked = False
            
        else:
            # Didn't like it - like
            liked = True
            
        likes_count = (
            ArticleLike.objects
            .filter(article=article)
            .count()
        )
            
        return Response(
            {
                'liked': liked,
                'likes': likes_count,
            }
        )



class ArticleLikeStatusView(APIView):
    
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        browser_id = request.headers.get('X-Browser-ID')
        
        if not browser_id:
            return Response(
                {'detail': 'Browser ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            article = Article.objects.get(
                slug=slug,
                status='published'
            )
        
        except Article.DoesNotExist:
            return Response(
                {'detail': 'Article not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        liked = ArticleLike.objects.filter(
            article=article,
            browser_id=browser_id
        ).exists()
        
        likes_count = ArticleLike.objects.filter(
            article=article
        ).count()
        
        return Response({
            'liked': liked,
            'likes': likes_count,
        })



class SearchArticleView(generics.ListAPIView):
    
    serializer_class = ArticleListSerializer
    
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        
        query = self.request.GET.get('q')
        
        return Article.objects.filter(
            status='published',
            title__icontains=query,
        )




class CategoryArticleView(generics.ListAPIView):
    
    serializer_class = ArticleListSerializer
    
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        
        slug = self.kwargs['slug']
        
        return Article.objects.filter(
            status='published',
            category__slug=slug,
        )

class ArticleCreateView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleCreateSerializer
    permission_classes = [AllowAny]



class DestinationListView(ListAPIView):
    queryset = Destination.objects.filter(
        status='published'
    ).select_related(
        'author',
        'category'
    )
    
    serializer_class = DestinationSerializer



class DestinationDetailView(RetrieveAPIView):
    queryset = Destination.objects.filter(
        status='published'
    ).select_related(
        'author',
        'category'
    )
    
    serializer_class = DestinationSerializer
    lookup_field = 'slug'


class DestinationDirectoryView(ListAPIView):
    
    queryset = DestinationContinent.objects.prefetch_related(
        'destinations'
    ).all()
    
    serializer_class = DestinationDirectorySerializer
    
    # queryset = Destination.objects.filter(
    #     status='published'
    # ).select_related(
    #     'author',
    #     'category'
    # )
    
    # serializer_class = DestinationSerializer
    



class TravelGuideListView(ListAPIView):
    queryset = TravelGuide.objects.filter(
        status='published'
    ).select_related(
        'author',
        'category',
        'destination',
    )
    
    serializer_class = TravelGuideSerializer

class TravelGuideDetailView(RetrieveAPIView):
    queryset = TravelGuide.objects.filter(
        status='published'
    ).select_related(
        'author',
        'category',
        'destination',
    )
    
    serializer_class = TravelGuideSerializer
    lookup_field = 'slug'



class EventListView(ListAPIView):
        queryset = Event.objects.filter(
            status='published'
        ).filter(
            Q(end_date__gt=timezone.localdate()) |
            Q(
                end_date=timezone.localdate(),
                end_time__gt=timezone.localtime().time()
            )
        ).select_related(
            'author',
            'category',
        )
        serializer_class = EventSerializer



class EventDetailView(RetrieveAPIView):
    queryset = Event.objects.filter(
        status='published'
    ).filter(
        Q(end_date__gt=timezone.localdate()) |
        Q(
            end_date=timezone.localdate(),
            end_time__gt=timezone.localtime().time()
        )
    ).select_related(
        'author',
        'category',
    )
    
    serializer_class = EventSerializer
    lookup_field = 'slug'


class UpcomingEventListView(ListAPIView):
    serializer_class = EventSerializer
    
    def get_queryset(self):
        today = timezone.localdate()
        now = timezone.localtime()
        current_time = now.time()
        fourteen_days_from_now = today + timedelta(days=14)
        
        return Event.objects.filter(
            status='published',
            event_date__gte=today,
            event_date__lte=fourteen_days_from_now,
        ).filter(
            Q(
                # Multi-day event that continues beyond today
                event_date__gt=today
            )
            |
            Q(
                # Event ends today but has no end time
                event_date=today,
                end_time__isnull=True
            )
            |
            Q(
                # Event ends today and hasn't reaches its end time
                end_date=today,
                end_time__gt=current_time
            ) 
            |
            Q(
                # No end date: event date is after today
                end_date__isnull=True,
                event_date__gt=today
            )
            |
            Q(
                # No end date: event is today and has no end time
                end_date__isnull=True,
                event_date=today,
                end_time__isnull=True
            )
            |
            Q(
                # No end date: event is today and hasn't finished
                end_date__isnull=True,
                event_date=today,
                end_time__gt=current_time
            )
        ).select_related(
        'author',
        'category',
        ).order_by(
        'event_date',
        'start_time',
        )
        
        # return queryset
    
    
# def get(self, request):
        # now = timezone.localtime()
        
        # events = Event.objects.filter(
        #     published=True
        # ).filter(
        #     Q(end_date__gt=now.date()) |
        #     Q(
        #         end_date=now.date(),
        #         end_time__gt=now.time()
        #     )
        # )
        
        # serializer = EventSerializer(
        #     events,
        #     many=True
        # )
        
        # return Response(serializer.data)




class ProfileView(RetrieveAPIView):
    serializer_class = ProfileSerializer
    
    def get_object(self):
        return Profile.objects.first()




class AboutView(RetrieveAPIView):
    serializer_class = AboutSerializer
    
    def get_object(self):
        return About.objects.first()




class ContactView(RetrieveAPIView):
    serializer_class = ContactSerializer
    
    def get_object(self):
        return Contact.objects.first()




class HeroView(RetrieveAPIView):
    
    serializer_class = HeroSerializer
    
    def get_object(self):
        return Hero.objects.select_related(
            'article',
            'article__author',
            'article__category',
            'article__subcategory',
            'article__destination',
        ).first()
        
        
    # def get_object(self):
    #     return Hero.objects.select_related(
    #         'article',
    #     ).first()
        
    #     if not hero:
    #         raise Http404('No hero has been configured.')
        
    #     return hero



class TravelResourceListView(generics.ListAPIView):
    serializer_class = TravelResourceSerializer

    def get_queryset(self):
        return (
            TravelResource.objects
            .filter(is_active=True)
            .select_related(
                "partner",
                "partner__package",
            )
            .order_by("-created_at")
        )



class TravelResourceDetailView(generics.RetrieveAPIView):
    serializer_class = TravelResourceSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return (
            TravelResource.objects
            .filter(is_active=True)
            .select_related(
                "partner",
                "partner__package",
            )
        )



class PartnerSubmissionCreateView(generics.CreateAPIView):
    serializer_class = PartnerSubmissionSerializer


    def get_queryset(self):
        return PartnerSubmission.objects.all()




class TravelSupportView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request):
        return Response(
            getattr(
                settings,
                'TRAVEL_SUPPORT',
                {
                    'enabled': False,
                    'title': 'Support Travel Beyond with El',
                    'description': '',
                    'amounts': 'USD',
                    'url': '',
                },
            )
        )





from rest_framework import generics
from rest_framework.permissions import AllowAny

class WebsitePageDetailView(generics.RetrieveAPIView):
    serializer_class = WebsitePageSerializer
    permission_classes = [AllowAny]
    lookup_field = "page_type"

    def get_queryset(self):
        return WebsitePage.objects.filter(
            is_published=True
        )
