from django.urls import path
from .analytics.views import (
    ArticleVisitStartView,
    ArticleVisitEndView,
)

from .search import SearchView

from .views import *
# from .views import CommentCreateView


app_name = 'articles'

urlpatterns = [
    path('hero/', HeroView.as_view(), name='hero'),
    
    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path('articles/', ArticleListView.as_view(), name='article_list'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    
    path('articles/subcategory/<slug:slug>/', SubcategoryArticlesView.as_view(), name='subcategory_articles'),
    path('articles/resolve/<slug:slug>/', ArticleSlugResolverView.as_view(), name='resolve_article_slug'),
    
    path('home/', HomeAPIView.as_view(), name='home'),
    
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories<slug:slug>/', CategoryArticleView.as_view(), name='category_articles'),
    
    path('destinations/directory/', DestinationDirectoryView.as_view(), name='destination_directory'),
    path('destinations/', DestinationListView.as_view(), name='destinations'),
    path('destinations/<slug:slug>/', DestinationDetailView.as_view(), name='destination_detail'),
    
    path('travel-guides/', TravelGuideListView.as_view(), name='travel-guides'),
    path('travel-guides/<slug:slug>/', TravelGuideDetailView.as_view(), name='travel-guide_detail'),
    
    path('events/', EventListView.as_view(), name='events'),
    path('events/upcoming/', UpcomingEventListView.as_view(), name='upcoming_events'),
    path('events/<slug:slug>/', EventDetailView.as_view(), name='event_detail'),
    
    path('search/', SearchView.as_view(), name='search'),
    
    path("pages/<slug:page_type>/", WebsitePageDetailView.as_view(), name="website-page-detail",),
    
    path('comments/', CommentCreateView.as_view(), name='comment-create'),
    path('articles/<slug:slug>/comments/', CommentListView.as_view(), name='article_comments'),
    
    path('articles/<slug:slug>/visit/start/', ArticleVisitStartView.as_view(), name='article_visit_start'),
    path('articles/visits/<int:visit_id>/end/', ArticleVisitEndView.as_view(), name='article_visit_end'),
    
    path('articles/<slug:slug>/like/', ArticleLikeView.as_view(), name='article_like'),
    path('articles/<slug:slug>/like-status/', ArticleLikeStatusView.as_view(), name='like-status'),
    
    path('resources/', TravelResourceListView.as_view(), name='travel-resource-list'),
    path('resources/<slug:slug>/', TravelResourceDetailView.as_view(), name='travel-resource-detail'),

    path('partner-submissions/', PartnerSubmissionCreateView.as_view(), name='partner-submission-create'),
    path('support/', TravelSupportView.as_view(), name='travel-support'),
    
    path('profile/', ProfileView.as_view(), name='profile'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
]