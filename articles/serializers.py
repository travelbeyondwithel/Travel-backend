from rest_framework import serializers
from django.conf import settings
# from taggit.serializers import (
#     TagListSerializerField,
#     TaggitSerializer,
# )
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
    Hero,
    TravelResource,
    PartnerSubmission,
    TravelPartner,
    WebsitePage,
)

class AuthorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Author
        fields = (
            'id',
            'name',
            'role',
            'photo',
            'bio',
            'facebook',
            'instagram',
            'linkedin',
        )

class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model =Category
        fields = [ 
            'id',
            'name', 
            'slug',
            'description',
        ]



# class ArticleSectionSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model =ArticleSection 
#         fields = [ 
#             'id',
#             'heading',
#             'content', 
#         ]



class GalleryImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =GalleryImage
        fields = [ 
            'id',
            'image',
            'caption', 
            'order', 
        ]




class QuickTipSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =QuickTip 
        fields = [ 
            'id',
            'title',
            'value', 
        ]




class FAQSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =FAQ
        fields = [ 
            'id',
            'question', 
            'answer', 
        ]


class ArticleLikeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ArticleLike
        fields = (
            'article',
            'browser_id',
        )


class CommentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comment
        fields = [ 
            'id',
            'article',
            'name', 
            'email',
            'content', 
            'created_at', 
        ]
        
        read_only_fields = [
            'id',
            'article',
            'created_at',
        ]



class DestinationMiniSerializer(serializers.ModelSerializer): 
    
    class Meta:
        model = Destination
        fields = [
            'id',
            'title',
            'slug',
        ]
        


class DestinationContinentMiniSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DestinationContinent
        fields = [
            'id',
            'name',
            'slug',
        ]



class CategoryMiniSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
        ]
        


class SubcategorySerializer(serializers.ModelSerializer):
    
    category_name = serializers.CharField(
        source='category.name', 
        read_only=True
    )
    
    class Meta:
        model = Subcategory
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'category',
            'category_name',
        ]


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    category = CategoryMiniSerializer(read_only=True)
    subcategory = SubcategorySerializer(read_only=True)
    destination = DestinationMiniSerializer(read_only=True)
    
    reading_time = serializers.SerializerMethodField()
    published_at = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'subtitle',
            'slug',
            'author',
            'category',
            'subcategory',
            'destination',
            'introduction',
            'reading_time',
            'tags',
            'hero_image',
            'hero_image_alt',
            'hero_image_caption',
            'published_at',
            'views',
            'likes',
            'is_featured',
        ]
        
    def get_author(self, obj):
        if obj.author:
            return obj.author.name
        
        return 'El'
    
    def get_reading_time(self, obj):
        if obj.travel_guide:
            return obj.travel_guide.reading_time
        
        return obj.reading_time
    
    def get_published_at(self, obj):
        if obj.travel_guide:
            return obj.travel_guide.published_at
        
        return obj.published_at
    
    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]
    # def get_category(self, obj):
    #     if obj.category:
    #         return obj.category.name
        
        # return 'Travel'



class ArticleListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    subcategory = SubcategorySerializer(read_only=True)
    destination = DestinationMiniSerializer(read_only=True)
    
    reading_time = serializers.SerializerMethodField()
    published_at = serializers.SerializerMethodField()
    
    
    tags = serializers.SerializerMethodField()
    
    likes = serializers.SerializerMethodField()
    
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model =Article
        
        fields = [
            'id',
            'title',
            'subtitle',
            'slug',
            'author',
            'category',
            'subcategory',
            'destination',
            'introduction',
            'reading_time',
            'hero_image',
            'hero_image_alt',
            'hero_image_caption',
            'tags',
            'status',
            'published_at',
            'likes',
            'comments',
        ]
    
    def get_author(self, obj):
        if obj.author:
            return obj.author.name
        
        return 'El'
    
    def get_category(self, obj):
        if obj.category:
            return obj.category.name
        
        return 'Travel'
    
    def get_reading_time(self, obj):
        
        travel_guide = TravelGuide.objects.filter(
            slug=obj.slug,
            status='published'
        ).first()
        
        if travel_guide:
            return travel_guide.reading_time
        
        return obj.reading_time
    
    def get_published_at(self, obj):
        
        travel_guide = TravelGuide.objects.filter(
            slug=obj.slug,
            status='published'
        ).first()
        
        if travel_guide:
            return travel_guide.published_at
        
        return obj.published_at
    
    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]
    
    def get_likes(self, obj):
        return obj.likes.count()
    
    def get_comments(self, obj):
        return obj.comments.filter(
            approved=True
        ).count()



class ArticleDetailSerializer(serializers.ModelSerializer):
    
    category = CategorySerializer(read_only=True)
    
    subcategory = SubcategorySerializer(read_only=True)
    
    destination = DestinationMiniSerializer(read_only=True)
    
    author = AuthorSerializer(read_only=True)
    
    tags = serializers.SerializerMethodField()
    
    # sections = ArticleSectionSerializer(
    #     many=True,
    #     read_only=True
    # )
    
    gallery = GalleryImageSerializer(
        many=True,
        read_only=True
    )
    
    quick_tips = QuickTipSerializer(
        many=True,
        read_only=True
    )
    
    faqs = FAQSerializer(
        many=True,
        read_only=True
    )
    
    comments = CommentSerializer(
        many=True,
        read_only=True
    )
    
    likes = serializers.SerializerMethodField()
    views = serializers.IntegerField(read_only=True)
    
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model =Article
        
        fields = [
            'id',
            'title',
            'subtitle',
            'slug',
            'author',
            'category',
            'subcategory',
            'destination',
            'introduction',
            'hero_image',
            'hero_image_alt',
            'hero_image_caption',
            'content',
            
            'external_link',
            'external_link_text',
            
            'reading_time',
            'tags',
            'seo_title',
            'meta_description',
            'focus_keyword', 
            'published_at',
            
            # 'sections',
            'gallery',
            'quick_tips',
            'faqs',
            'likes',
            'comments',
            'views',
            'comment_count',
        ]
    
    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]
    
    def get_likes(self, obj):
        return obj.likes.count()
    
    def get_comment_count(self, obj):
        return obj.comments.filter(
            approved=True
        ).count()
        


class HomeArticleSerializer(serializers.ModelSerializer):
    
    author = serializers.SerializerMethodField(
        # source='author.name',
        # read_only=True
    )
    
    category = serializers.SerializerMethodField(
        # source='category.name',
        # read_only=True
    )
    
    subcategory = SubcategorySerializer(read_only=True)
    
    likes_count = serializers.SerializerMethodField()
    
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        
        model = Article
        
        fields = [
            'id',
            'title',
            'slug',
            'author',
            'category',
            'subcategory',
            'introduction',
            'hero_image',
            'reading_time',
            'published_at',
            'likes_count',
            'comments_count',
        ]
    
    def get_author(self, obj):
        if obj.author:
            return obj.author.name
        
        return 'El'
    
    def get_category(self, obj):
        if obj.category:
            return obj.category.name
        
        return 'Travel'
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_comments_count(self, obj):
        
        return obj.comments.filter(
            approved=True
        ).count()
        
        
class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'



class DestinationSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    
    category = serializers.SerializerMethodField()
    
    continent = DestinationContinentMiniSerializer(
        read_only=True
    )
    
    class Meta:
        
        model = Destination
        
        fields = [
            'id',
            'title',
            'slug',
            'introduction',
            'content',
            'city',
            
            'continent',
            
            'hero_image',
            'hero_image_alt',
            'hero_image_caption',
            'author',
            'category',
            'reading_time',
            'is_featured',
            'status',
            'published_at',
            'created_at',
        ]
    
    def get_author(self, obj):
        if obj.author:
            return obj.author.name
        
        return None
    
    def get_category(self, obj):
        if obj.category:
            return obj.category.name
        
        return None


class DestinationDirectoryItemSerializer(serializers.ModelSerializer):
    
    image = serializers.ImageField(
        source='hero_image',
        read_only=True
    )
    
    class Meta:
        model = Destination
        fields = [
            'id',
            'title',
            'slug',
            'image',
            'city',
        ]


class DestinationDirectorySerializer(
    serializers.ModelSerializer
):
    
    countries = serializers.SerializerMethodField()
    
    class Meta:
        model = DestinationContinent
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'countries',
        ]
        
    def get_countries(self, obj):
        
        destinations = obj.destinations.filter(
            status='published'
        )
        
        return DestinationDirectoryItemSerializer(
            destinations,
            many=True,
            context=self.context
        ).data




class TravelGuideSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()
    
    class Meta:
        
        model = TravelGuide
        
        fields = [
            'id',
            'title',
            'slug',
            'introduction',
            'content',
            'hero_image',
            'hero_image_alt',
            'hero_image_caption',
            'author',
            'category',
            'destination',
            'reading_time',
            'is_featured',
            'status',
            'published_at',
            'created_at',
        ]
    
    def get_author(self, obj):
        if obj.author:
            return obj.author.name
        
        return None
    
    def get_category(self, obj):
        if obj.category:
            return obj.category.name
        
        return None
    
    def get_destination(self, obj):
        if obj.destination:
            return {
                'id': obj.destination.id,
                'title': obj.destination.title,
                'slug': obj.destination.slug,
            }
        return None




class EventSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    
    class Meta:
        
        model = Event
        
        fields = [
            'id',
            'title',
            'slug',
            'introduction',
            'content',
            'event_date',
            'start_time',
            'end_date',
            'end_time',
            'venue',
            'location',
            'organizer',
            'ticket_url',
            'ticket_price',
            'hero_image',
            'hero_image_alt',
            'hero_image_caption',
            'author',
            'category',
            'is_featured',
            'status',
            'published_at',
            'created_at',
        ]
    
    def get_author(self, obj):
        if obj.author:
            return obj.author.name
        
        return None
    
    def get_category(self, obj):
        if obj.category:
            return obj.category.name
        
        return None




class ProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profile
        fields = [
            'id',
            'name',
            'role',
            'tagline',
            'bio',
            'photo',
            'facebook',
            'instagram',
            'youtube',
            'tiktok',
            'pinterest',
            'linkedin',
        ]





class AboutSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = About
        fields = [
            'id',
            'title',
            'content',
            # 'hero_image',
            # 'hero_image_alt',
            # 'hero_image_caption',
            'updated_at',
        ]





class ContactSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Contact
        fields = [
            'id',
            'title',
            'introduction',
            'email',
            'phone',
            'address',
            'facebook',
            'instagram',
            'whatsapp',
            'youtube',
            'linkedin',
            'updated_at',
        ]





class HeroSerializer(serializers.ModelSerializer):
    
    article = ArticleSerializer(read_only=True)
    
    class Meta:
        model = Hero
        fields = [
            'id',
            'article',
            'created_at',
            'updated_at',
        ]



class TravelPartnerSerializer(serializers.ModelSerializer):
    
    package_display = serializers.CharField(
        source="package.get_name_display",
        read_only=True
    )
    
    class Meta:
        model = TravelPartner
        fields = [
            "id",
            "business_name",
            "slug",
            "business_type",
            "description",
            "logo",
            "main_image",
            "location",
            "country",

            "phone",
            "email",
            "website_url",
            "booking_url",
            "instagram_url",
            "facebook_url",

            "package",
            "package_display",

            "status",
            "is_featured",
        ]



class TravelResourceSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(
        source="get_category_display",
        read_only=True,
    )

    partner = TravelPartnerSerializer(
        read_only=True,
    )

    class Meta:
        model = TravelResource

        fields = [
            "id",
            "title",
            "slug",

            "category",
            "category_display",

            "partner",

            "description",
            "image",
            "external_url",

            "is_featured",
            "is_active",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "slug",
            "created_at",
            "updated_at",
        ]

    def get_partner_package_display(self, obj):
        if not obj.partner or not obj.partner.package:
            return None
        
        return obj.partner.package.get_name_display()
    
    def get_is_featured_partner(self, obj):
        if not obj.partner or not obj.partner.package:
            return False
        
        return obj.partner.package.name == 'featured'
    
    def get_is_sponsored(self, obj):
        if not obj.partner or not obj.partner.package:
            return False
        
        return obj.partner.package.name == 'sponsored'


class PartnerSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerSubmission

        fields = [
            "id",
            "business_name",
            "contact_name",
            "email",
            "phone",
            "business_type",
            "location",
            "country",
            "website_url",
            "booking_url",
            "description",
            "logo",
            "main_image",
            "instagram_url",
            "facebook_url",
            "requested_package",
            "consent_to_publish",
            "accepted_terms",
            "status",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "created_at",
        ]

    def validate_consent_to_publish(self, value):
        if not value:
            raise serializers.ValidationError(
                "You must give permission for Travel Beyond with El "
                "to publish the submitted information and images."
            )

        return value

    def validate_accepted_terms(self, value):
        if not value:
            raise serializers.ValidationError(
                "You must accept the partner terms."
            )

        return value




class TravelSupportSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()
    title = serializers.CharField()
    description = serializers.CharField()
    amounts = serializers.ListField(
        child=serializers.IntegerField()
    )
    currency = serializers.CharField()
    url = serializers.URLField()




class WebsitePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsitePage
        fields = [
            "id",
            "page_type",
            "title",
            "introduction",
            "content",
            "updated_at",
        ]
        read_only_fields = fields