from datetime import timedelta

from datetime import datetime
from typing import Any

from django.contrib import admin, messages
from django.db.models import Count, Q, Sum
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils import timezone

from .analytics.services import (
    get_article_analytics,
    format_duration,
)

from .models import (
    Category,
    Article,
    Subcategory,
    GalleryImage,
    QuickTip,
    FAQ,
    Comment,
    ArticleLike,
    Author,
    Destination,
    DestinationContinent,
    TravelGuide,
    Event,
    Profile,
    About,
    Contact,
    ArticleVisit,
    Hero,
    TravelResource,
    PartnerPackage,
    TravelPartner,
    PartnerSubmission,
    WebsitePage,
)

# ============================================================
# ArticleVisit
# ============================================================

@admin.register(ArticleVisit)
class ArticleVisitAdmin(admin.ModelAdmin):
    list_display = (
        'article',
        'started_at',
        'ended_at',
        'duration',
        'session_key',
    )
    
    list_filter = (
        'started_at',
    )
    
    search_fields = (
        'article__title',
        'session_key',
    )
    
    readonly_fields = (
        'started_at',
    )
    
    ordering = (
        '-started_at',
    )
    
    date_hierarchy = 'started_at'






# ============================================================
# DESTINATION
# ============================================================

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'continent',
        'country',
        'city',
        'author',
        'category',
        'status',
        'is_featured',
        'published_at',
    )

    list_filter = (
        'continent',
        'status',
        'is_featured',
        'country',
        'category',
        'published_at',
    )

    search_fields = (
        'title',
        'country',
        'city',
        'introduction',
        'content',
    )

    prepopulated_fields = {
        'slug': ('title',)
    }

    list_editable = (
        'status',
        'is_featured',
    )

    ordering = (
        '-published_at',
        '-created_at',
    )

# ============================================================
# DESTINATION CONTINENT
# ============================================================

@admin.register(DestinationContinent)
class DestinationContinentAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'slug',
        'ordering',
    )

    search_fields = (
        'name',
        'slug',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    ordering = (
        'ordering',
        'name',
    )

# ============================================================
# TRAVEL GUIDE
# ============================================================

@admin.register(TravelGuide)
class TravelGuideAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'destination',
        'author',
        'category',
        'status',
        'is_featured',
        'published_at',
    )

    list_filter = (
        'status',
        'is_featured',
        'category',
        'destination',
        'published_at',
    )

    search_fields = (
        'title',
        'introduction',
        'content',
        'destination__title',
    )

    prepopulated_fields = {
        'slug': ('title',)
    }

    readonly_fields = (
        'reading_time',
        'created_at',
        'updated_at',
    )

    list_editable = (
        'status',
        'is_featured',
    )

    ordering = (
        '-published_at',
        '-created_at',
    )

# ============================================================
# EVENT
# ============================================================

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'event_date',
        'start_time',
        'end_date',
        'end_time',
        'venue',
        'location',
        'organizer',
        'status',
        'is_featured',
    )

    list_filter = (
        'status',
        'is_featured',
        'event_date',
        'end_date',
        'category',
    )

    search_fields = (
        'title',
        'introduction',
        'content',
        'venue',
        'location',
        'organizer',
    )

    prepopulated_fields = {
        'slug': ('title',)
    }

    list_editable = (
        'status',
        'is_featured',
    )

    ordering = (
        'event_date',
        'start_time',
        'end_date',
        'end_time',
    )

# ============================================================
# PAST EVENTS
# ============================================================
#
# This is a PROXY model.
# It does NOT create another database table.
# It simply gives Django Admin another way of viewing Event.
# ============================================================

class PastEvent(Event):

    class Meta:
        proxy = True
        verbose_name = 'Past event'
        verbose_name_plural = 'Past events'

@admin.register(PastEvent)
class PastEventAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'event_date',
        'start_time',
        'end_date',
        'end_time',
        'venue',
        'location',
        'organizer',
        'status',
    )

    list_filter = (
        'status',
        'event_date',
        'end_date',
        'category',
    )

    search_fields = (
        'title',
        'venue',
        'location',
        'organizer',
    )

    ordering = (
        '-end_date',
        '-end_time',
    )

    # --------------------------------------------------------
    # Only show events that have completely finished
    # --------------------------------------------------------

    def get_queryset(self, request):

        queryset = super().get_queryset(request)

        now = timezone.localtime()

        past_event_ids = []

        for event in queryset:

            # An event without an end date cannot be
            # determined to be completely finished.
            if not event.end_date:
                continue

            # An event without an end time cannot be
            # determined to be completely finished.
            if not event.end_time:
                continue

            event_datetime = timezone.make_aware(
                datetime.combine(
                    event.end_date,
                    event.end_time,
                )
            )

            if event_datetime < now:
                past_event_ids.append(event.pk)

        return queryset.filter(
            pk__in=past_event_ids
        )

    # --------------------------------------------------------
    # Delete all past events
    # --------------------------------------------------------

    @admin.action(
        description='Delete ALL past events'
    )
    def delete_all_past_events(self, request, queryset):

        # Get ALL events that are currently displayed
        # in the Past Events section.
        past_events = self.get_queryset(request)

        count = past_events.count()

        if count == 0:

            self.message_user(
                request,
                'There are no past events to delete.',
                level='info',
            )

            return

        past_events.delete()

        self.message_user(
            request,
            f'{count} past event(s) deleted successfully.',
            level='success',
        )

    actions = [
        'delete_all_past_events',
    ]

# ============================================================
# AUTHOR
# ============================================================

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'role',
    )

    search_fields = (
        'name',
    )

# ============================================================
# INLINE MODELS
# ============================================================

class GalleryImageInline(admin.TabularInline):

    model = GalleryImage
    extra = 1

class QuickTipInline(admin.TabularInline):

    model = QuickTip
    extra = 1

class FAQInline(admin.TabularInline):

    model = FAQ
    extra = 1

# ============================================================
# CATEGORY
# ============================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'slug',
    )

    search_fields = (
        'name',
        'slug',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    ordering = (
        'name',
    )

# ============================================================
# SUBCATEGORY
# ============================================================

@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'category',
        'slug',
    )

    list_filter = (
        'category',
    )

    search_fields = (
        'name',
        'slug',
        'category__name',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    ordering = (
        'category__name',
        'name',
    )

# ============================================================
# ARTICLE
# ============================================================

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'author',
        'category',
        'subcategory',
        'destination',
        'status',
        'reading_time',
        'published_at',
        'created_at',
        'content',
        'analytics',
    )

    list_filter = (
        'author',
        'status',
        'category',
        'subcategory',
        'published_at',
    )

    search_fields = (
        'title',
        'subtitle',
        'introduction',
        'destination',
    )

    prepopulated_fields = {
        'slug': ('title',)
    }

    readonly_fields = (
        'reading_time',
        'views',
        'created_at',
        'updated_at',
    )

    filter_horizontal = ()

    inlines = [
        GalleryImageInline,
        QuickTipInline,
        FAQInline,
    ]

    fieldsets = (
        (
            'Basic Information',
            {
                'fields': (
                    'title',
                    'slug',
                    'subtitle',
                    'author',
                    'category',
                    'subcategory',
                    'destination',
                    'introduction',
                )
            },
        ),

        (
            'Hero Image',
            {
                'fields': (
                    'hero_image',
                    'hero_image_alt',
                    'hero_image_caption',
                )
            },
        ),

        (
            'SEO',
            {
                'fields': (
                    'seo_title',
                    'meta_description',
                    'focus_keyword',
                    'tags',
                )
            },
        ),

        (
            'Publishing',
            {
                'fields': (
                    'status',
                    'published_at',
                    'scheduled_publish',
                    'is_featured',
                    'featured_order',
                )
            },
        ),

        (
            'Statistics',
            {
                'fields': (
                    'views',
                    'reading_time',
                    'created_at',
                    'updated_at',
                )
            },
        ),

        (
            'Article Content',
            {
                'fields': (
                    'content',
                )
            },
        ),
    )
    
    @admin.display(description='Analytics')
    def analytics(self, obj):
        data = get_article_analytics(obj)
        
        return (
            f"Today: "
            f"{data['today']['visits']} visits . "
            f"{format_duration(data['today']['time_spent'])} |"
            
            f"7 Days: "
            f"{data['last_7_days']['visits']} visits . "
            f"{format_duration(data['last_7_days']['time_spent'])} |"

            f"30 Days: "
            f"{data['last_30_days']['visits']} visits . "
            f"{format_duration(data['last_30_days']['time_spent'])} |"
            
            f"12 Months: "
            f"{data['last_12_months']['visits']} visits . "
            f"{format_duration(data['last_12_months']['time_spent'])}"
        )
        
    analytics.short_description = 'Analytics'
    
    
    # def analytics_7_days(self, obj):
    #     return get_article_analytics(obj)['last_7_days']['visits']
    
    # analytics_7_days.short_description = '7 Todays'
    
    # def analytics_30_days(self, obj):
    #     return get_article_analytics(obj)['last_30_days']['visits']
    
    # analytics_30_days.short_description = '30 Todays'
    
    # def analytics_12_months(self, obj):
    #     return get_article_analytics(obj)['last_12_months']['visits']
    

# ============================================================
# COMMENTS
# ============================================================

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'article',
        'approved',
        'created_at',
    )

    list_filter = (
        'approved',
        'created_at',
    )

    search_fields = (
        'name',
        'body',
        'article__title',
    )

    actions = [
        'approve_comments',
    ]

    @admin.action(description='Approve selected comments')
    def approve_comments(self, request, queryset):

        queryset.update(
            approved=True
        )

# ============================================================
# ARTICLE LIKES
# ============================================================

@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):

    list_display = (
        'article',
        'browser_id',
        'created_at',
    )

    search_fields = (
        'article__title',
        'browser_id',
    )

    readonly_fields = (
        'browser_id',
        'created_at',
    )

    ordering = (
        '-created_at',
    )

# ============================================================
# PROFILE
# ============================================================

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'tagline',
        'updated_at',
    )

    readonly_fields = (
        'updated_at',
    )

    def has_add_permission(self, request):

        return not Profile.objects.exists()

# ============================================================
# ABOUT
# ============================================================

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'updated_at',
    )

    readonly_fields = (
        'updated_at',
    )

    def has_add_permission(self, request):

        return not About.objects.exists()

# ============================================================
# CONTACT
# ============================================================

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'email',
        'phone',
        'updated_at',
    )

    readonly_fields = (
        'updated_at',
    )

    def has_add_permission(self, request):

        return not Contact.objects.exists()




@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    
    list_display = (
        'article',
        'updated_at',
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
    )




@admin.register(TravelResource)
class TravelResourceAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'partner',
        'is_featured',
        'is_active',
        'created_at',
    )
    
    list_filter = (
        'category',
        'is_featured',
        'is_active'
    )
    
    search_fields = (
        'title',
        'description',
        'partner__business_name'
    )
    
    prepopulated_fields = {
        'slug': ('title',)
    }
    
    ordering = (
        '-created_at',
    )




@admin.register(PartnerPackage)
class PartnerPackageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    list_filter = (
        "name",
        "is_active",
    )

    search_fields = (
        "description",
    )




@admin.register(TravelPartner)
class TravelPartnerAdmin(admin.ModelAdmin):
    list_display = (
        "business_name",
        "business_type",
        "location",
        "package",
        "status",
        "is_featured",
        "created_at",
    )

    list_filter = (
        "status",
        "package",
        "is_featured",
        "business_type",
    )

    search_fields = (
        "business_name",
        "location",
        "country",
        "email",
    )

    prepopulated_fields = {
        "slug": ("business_name",)
    }

    ordering = (
        "-created_at",
    )




@admin.register(PartnerSubmission)
class PartnerSubmissionAdmin(admin.ModelAdmin):

    list_display = (
        "business_name",
        "contact_name",
        "email",
        "requested_package",
        "status",
        "consent_to_publish",
        "accepted_terms",
        "created_at",
    )

    list_filter = (
        "status",
        "requested_package",
        "business_type",
        "consent_to_publish",
        "accepted_terms",
    )

    search_fields = (
        "business_name",
        "contact_name",
        "email",
        "location",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    actions = [
        "approve_and_create_partner",
    ]

    @admin.action(
        description="Approve & create Travel Partner + Resource"
    )
    def approve_and_create_partner(self, request, queryset):

        created_count = 0
        skipped_count = 0

        for submission in queryset:

            # ---------------------------------------------
            # ALREADY APPROVED
            # ---------------------------------------------

            if submission.status == "approved":
                skipped_count += 1

                self.message_user(
                    request,
                    f"{submission.business_name} is already approved.",
                    messages.WARNING,
                )

                continue

            # ---------------------------------------------
            # PUBLISHING CONSENT
            # ---------------------------------------------

            if not submission.consent_to_publish:
                skipped_count += 1

                self.message_user(
                    request,
                    f"{submission.business_name} cannot be approved "
                    "because publishing consent was not provided.",
                    messages.WARNING,
                )

                continue

            # ---------------------------------------------
            # TERMS
            # ---------------------------------------------

            if not submission.accepted_terms:
                skipped_count += 1

                self.message_user(
                    request,
                    f"{submission.business_name} cannot be approved "
                    "because the terms were not accepted.",
                    messages.WARNING,
                )

                continue

            # ---------------------------------------------
            # PACKAGE
            # ---------------------------------------------

            package, _ = PartnerPackage.objects.get_or_create(
                name=submission.requested_package,
                defaults={
                    "description": (
                        f"{submission.get_requested_package_display()} "
                        "for Travel Beyond with El partners."
                    ),
                    "is_active": True,
                },
            )

            # ---------------------------------------------
            # TRAVEL PARTNER
            # ---------------------------------------------

            partner = TravelPartner.objects.create(
                business_name=submission.business_name,
                business_type=submission.business_type,
                description=submission.description,

                logo=submission.logo,
                main_image=submission.main_image,

                location=submission.location,
                country=submission.country,

                phone=submission.phone,
                email=submission.email,

                website_url=submission.website_url,
                booking_url=submission.booking_url,

                instagram_url=submission.instagram_url,
                facebook_url=submission.facebook_url,

                package=package,

                status="active",

                is_featured=(
                    submission.requested_package == "featured"
                ),
            )

            # ---------------------------------------------
            # RESOURCE CATEGORY
            # ---------------------------------------------

            business_type = (
                submission.business_type or ""
            ).strip().lower()

            accommodation_types = {
                "hotel",
                "guesthouse",
                "lodge",
                "resort",
            }

            if business_type in accommodation_types:
                resource_category = "accommodation"
            else:
                resource_category = "things_to_do"

            # ---------------------------------------------
            # TRAVEL RESOURCE
            # ---------------------------------------------

            TravelResource.objects.create(
                title=submission.business_name,

                category=resource_category,

                partner=partner,

                description=submission.description,

                image=submission.main_image,

                external_url=(
                    submission.booking_url
                    or submission.website_url
                ),

                is_featured=(
                    submission.requested_package == "featured"
                ),

                is_active=True,
            )

            # ---------------------------------------------
            # MARK SUBMISSION APPROVED
            # ---------------------------------------------

            submission.status = "approved"

            submission.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            created_count += 1

        # ---------------------------------------------
        # SUCCESS MESSAGE
        # ---------------------------------------------

        if created_count:
            self.message_user(
                request,
                f"{created_count} partner(s) successfully "
                "approved and created.",
                messages.SUCCESS,
            )

        # ---------------------------------------------
        # WARNING MESSAGE
        # ---------------------------------------------

        if skipped_count:
            self.message_user(
                request,
                f"{skipped_count} submission(s) were skipped.",
                messages.WARNING,
            )




@admin.register(WebsitePage)
class WebsitePageAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "page_type",
        "is_published",
        "updated_at",
    )

    list_filter = (
        "page_type",
        "is_published",
    )

    search_fields = (
        "title",
        "introduction",
        "content",
    )

    list_editable = ("is_published",)

    readonly_fields = ("updated_at",)

    fieldsets = (
        ("Page Settings", {
            "fields": (
                "page_type",
                "title",
                "introduction",
                "is_published",
            )
        }),
        ("Page Content", {
            "fields": ("content",)
        }),
        ("Record Information", {
            "fields": ("updated_at",)
        }),
    )