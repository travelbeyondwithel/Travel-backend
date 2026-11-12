from django.db import models
from django.core.exceptions import ValidationError
import math
import re
import uuid

# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver

from django.conf import settings
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone
from datetime import datetime

from taggit.managers import TaggableManager

# Create your models here.



class Author(models.Model):
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120, blank=True)
    
    photo = models.ImageField(
        upload_to='authors',
        blank=True,
        null=True
    )
    
    bio = models.TextField(blank=True)
    
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    
    def __str__(self):
        return self.name




class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    
    
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name



class Subcategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    
    name =models.CharField(
        max_length=100
    )
    
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True
    )
    
    description = models.TextField(
        blank=True
    )
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Subcategories'
        unique_together = ('category', 'name')
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
            super().save(*args, **kwargs)
            
    def __str__(self):
        return self.name




class Article(models.Model):
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    
    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
    )
    
    title = models.CharField(max_length=255)
    
    subtitle = models.CharField(
        max_length=350,
        blank=True
    )
    
    slug = models.SlugField(
        unique=True,
        blank=True
    )
    
    # keep your existing category, tags, hero image, etc.
    
    introduction = models.TextField(blank=True)
    
    content = CKEditor5Field(
        config_name='extends',
        blank=True,
        default=''
    )
    
    # Optional prominent/direct link
    external_link = models.URLField(
        blank=True,
        null=True
    )
    
    external_link_text = models.CharField(
        max_length=150,
        blank=True,
    )
    
    reading_time = models.PositiveIntegerField(
        default=1
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
    )
    
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
    )
    
    destination = models.ForeignKey(
        'Destination',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
    )
    
    travel_guide = models.OneToOneField(
        'TravelGuide',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
    )
    
    views = models.PositiveIntegerField(
        default=0
    )
    
    is_featured = models.BooleanField(
        default=False,
        help_text='Display this article in homepage hero'
    )
    
    featured_order = models.PositiveIntegerField(
        default=0
    )
    
    
    # tags = models.ManyToManyField(
    #     "Tag",
    #     blank=True,
    #     related_name='articles',
    # )
    
    tags = TaggableManager(blank=True)
    
    hero_image = models.ImageField(
        max_length=255,
        blank=True
    )
    
    hero_image_alt = models.CharField(max_length=255, blank=True)
    
    hero_image_caption = models.CharField(max_length=255, blank=True)
    
    
    seo_title = models.CharField(
        max_length=255,
        blank=True
    )
    
    meta_description = models.TextField(blank=True)
    
    focus_keyword = models.CharField(
        max_length=100,
        blank=True
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    published_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    scheduled_publish = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Optional: Schedule this article to be published automatically.'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        
    # def __str__(self):
    #     return self.titles
    
    def calculate_reading_time(self):
        
        #------------------------
        # Calculate reading time
        #------------------------
        
        text_parts = [
            self.title or '',
            self.subtitle or '',
            self.introduction or '',
            self.content or '',
        ]
        
        # # Add all sections content
        # for section in self.sections.all():
        #     text_parts.append(section.heading or '')
        #     text_parts.append(section.content or '')
            
        # Combine everything
        full_text = " ".join(text_parts)
        
        # Remove HTML tags if There are any
        full_text = re.sub(r"<[^>]+>", " ", full_text)
        
        # Count words
        words = re.findall(r"\b[\w'-]+\b", full_text)
        
        word_count = len(words)
        
        # 200 words per minute
        reading_time = max(1, math.ceil(word_count / 200))
    
        return reading_time
    
    def save(self, *args, **kwargs):
        
        # Save first so the Article has an ID
        super().save(*args, **kwargs)
        
        # Calculate reading time
        reading_time = self.calculate_reading_time()
        
        #Update only the reading_time field
        if self.reading_time != reading_time:
            Article.objects.filter(pk=self.pk).update(
                reading_time=reading_time
            )
            
            self.reading_time = reading_time



class ArticleVisit(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='visits'
    )
    
    visit_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True
    )
    
    session_key = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        db_index=True
    )
    
    started_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    
    ended_at = models.DateTimeField(
        blank=True,
        null=True
    )
    
    duration = models.PositiveIntegerField(
        default=0,
        help_text='Time spent on the article in seconds.'
    )
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['article', '-started_at']),
            models.Index(fields=['-started_at']),
        ]
        
    def __str__(self):
        return f"{self.article.title} - {self.started_at:%Y-%m-%d %H:%M}"



class ArticleView(models.Model):
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='view_records',
    )
    
    browser_id = models.CharField(
        max_length=64,
        blank=True,
        default='',
        db_index=True,
    )
    
    ip_hash = models.CharField(
        max_length=64,
        blank=True,
        default='',
        db_index=True,
    )
    
    viewed_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    
    class Meta:
        indexes = [
            models.Index(
                fields=['article', 'browser_id', 'viewed_at']
            ),
            models.Index(
                fields=['article', 'ip_hash', 'viewed_at']
            ),
        ]
        
        constraints = [
            
            models.UniqueConstraint(
                fields=['article', 'browser_id'],
                condition=models.Q(browser_id=''),
                name='unique_article_browser_view',
            ),
            
            models.UniqueConstraint(
                fields=['article', 'ip_hash'],
                condition=models.Q(browser_id=''),
                name='unique_article_ip_view',
            )
        ]
        
    def __str__(self):
        return (
            f"{self.article.title} - "
            f"{self.viewed_at}"
        )




# class ArticleSection(models.Model):
    
#     article = models.ForeignKey(
#         "Article",
#         on_delete=models.CASCADE,
#         related_name="sections"
#     )
    
#     heading = models.CharField(max_length=255)
    
#     content = models.TextField(
#         blank=True
#     )
    
#     def __str__(self):
#         return self.heading
    
# @receiver(post_save, sender=ArticleSection)
# def updated_article_reading_time(sender, instance, **kwargs):
        
#     if instance.article_id:
#         article = instance.article
        
#         reading_time = article.calculate_reading_time()
        
#         if article.reading_time != reading_time:
#             Article.objects.filter(pk=article.pk).update(
#                 reading_time=reading_time
#             )
    
# @receiver(post_delete, sender=ArticleSection)
# def updated_article_reading_time_after_delete(sender, instance, **kwargs):
        
#     if instance.article_id:
#         try:
#             article = Article.objects.get(pk=instance.article_id)
#         except Article.DoesNotExist:
#             return
        
#         reading_time = article.calculate_reading_time()
        
#         Article.objects.filter(pk=article.pk).update(
#             reading_time=reading_time
#         )


class DestinationContinent(models.Model):
    
    name = models.CharField(
        max_length=100,
        unique=True
    )
    
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True
    )
    
    description = models.TextField(
        blank=True
    )
    
    ordering = models.PositiveIntegerField(
        default=0
    )
    
    class Meta:
        ordering = ['ordering', 'name']
        verbose_name = 'Destination Continent'
        verbose_name_plural = 'Destination Continents'
        
    def save(self, *args, **kwargs):
        
        if not self.slug:
            self.slug = slugify(self.name)
            
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name




class Destination(models.Model):
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    
    continent = models.ForeignKey(
        DestinationContinent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True, 
        related_name='destinations',
    )
    
    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='destinations',
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='destinations',
    )
    
    title = models.CharField(max_length=255)
    
    slug = models.SlugField(
        unique=True,
        blank=True,
    )
    
    introduction = models.TextField(
        blank=True
    )
    
    content = CKEditor5Field(
        config_name='extends',
        blank=True,
        default=''
    )
    
    country = models.CharField(
        max_length=120,
        blank=True
    )
    
    city = models.CharField(
        max_length=120,
        blank=True
    )
    
    hero_image = models.ImageField(
        upload_to='destinations/',
        blank=True,
        null=True
    )

    hero_image_alt = models.CharField(
        max_length=255,
        blank=True
    )

    hero_image_caption = models.CharField(
        max_length=255,
        blank=True
    )

    reading_time = models.PositiveIntegerField(
        default=1
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    is_featured = models.BooleanField(
        default=False
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True
    )

    seo_title = models.CharField(
        max_length=255,
        blank=True
    )

    meta_description = models.TextField(
        blank=True
    )

    focus_keyword = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

        # Calculate reading time
        text = f"{self.title} {self.introduction} {self.content}"

        text = re.sub(
            r"<[^>]+>",
            " ",
            text
        )

        words = re.findall(
            r"\b[\w'-]+\b",
            text
        )

        reading_time = max(
            1,
            math.ceil(len(words) / 200)
        )

        if self.reading_time != reading_time:
            Destination.objects.filter(
                pk=self.pk
            ).update(
                reading_time=reading_time
            )

            self.reading_time = reading_time





class TravelGuide(models.Model):

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='travel_guides',
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='travel_guides',
    )

    # Optional connection to a destination
    destination = models.ForeignKey(
        Destination,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='travel_guides',
    )

    title = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    introduction = models.TextField(
        blank=True
    )

    content = CKEditor5Field(
        config_name='extends',
        blank=True,
        default=''
    )

    hero_image = models.ImageField(
        upload_to='travel_guides/',
        blank=True,
        null=True
    )

    hero_image_alt = models.CharField(
        max_length=255,
        blank=True
    )

    hero_image_caption = models.CharField(
        max_length=255,
        blank=True
    )

    reading_time = models.PositiveIntegerField(
        default=1
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    is_featured = models.BooleanField(
        default=False
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True
    )

    seo_title = models.CharField(
        max_length=255,
        blank=True
    )

    meta_description = models.TextField(
        blank=True
    )

    focus_keyword = models.CharField(
        max_length=100,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.title)



        text = f"{self.title} {self.introduction} {self.content}"

        text = re.sub(
            r"<[^>]+>",
            " ",
            text
        )

        words = re.findall(
            r"\b[\w'-]+\b",
            text
        )

        reading_time = max(
            1,
            math.ceil(len(words) / 200)
        )

        if self.reading_time != reading_time:
            TravelGuide.objects.filter(
                pk=self.pk
            ).update(
                reading_time=reading_time
            )

            self.reading_time = reading_time
        
        if self.status == 'published' and self.published_at is None:
            self.published_at = timezone.now()
            
        super().save(*args, **kwargs)




class Event(models.Model):

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
    )

    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
    )

    title = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    introduction = models.TextField(
        blank=True
    )

    content = CKEditor5Field(
        config_name='extends',
        blank=True,
        default=''
    )

    # -----------------------------
    # Event date & time
    # -----------------------------

    event_date = models.DateField()

    start_time = models.TimeField(
        null=True,
        blank=True
    )
    
    end_date = models.DateField(
        null=True,
        blank=True
    )

    end_time = models.TimeField(
        null=True,
        blank=True
    )

    # -----------------------------
    # Location
    # -----------------------------

    venue = models.CharField(
        max_length=255,
        blank=True
    )

    location = models.CharField(
        max_length=255,
        blank=True
    )

    # -----------------------------
    # Organizer
    # -----------------------------

    organizer = models.CharField(
        max_length=255,
        blank=True
    )

    # -----------------------------
    # Tickets
    # -----------------------------

    ticket_url = models.URLField(
        blank=True
    )

    ticket_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # -----------------------------
    # Image
    # -----------------------------

    hero_image = models.ImageField(
        upload_to='events/',
        blank=True,
        null=True
    )

    hero_image_alt = models.CharField(
        max_length=255,
        blank=True
    )

    hero_image_caption = models.CharField(
        max_length=255,
        blank=True
    )

    # -----------------------------
    # Status
    # -----------------------------

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    is_featured = models.BooleanField(
        default=False
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # -----------------------------
    # SEO
    # -----------------------------

    seo_title = models.CharField(
        max_length=255,
        blank=True
    )

    meta_description = models.TextField(
        blank=True
    )

    focus_keyword = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['event_date', 'start_time']
    
    @property
    def is_active(self):
        
        now = timezone.localtime()
        
        if self.end_time:
            end_datetime = timezone.make_aware(
                datetime.combine(
                    self.end_date,
                    self.end_time
                )
            )
        else:
            end_datetime = timezone.make_aware(
                datetime.combine(
                    self.end_date,
                    datetime.max.time()
                )
            )
        return now <= end_datetime

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)




class GalleryImage(models.Model):
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='gallery'
    )
    
    image = models.ImageField(
        upload_to='gallery'
    )
    
    caption= models.CharField(max_length=255, blank=True)
    
    order = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return f"{self.article.title} Gallery"



class Tag(models.Model):
    
    name = models.CharField(max_length=100, unique=True)
    
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name
    

        
        
class QuickTip(models.Model):
    
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='quick_tips'
    )
    
    
    title = models.CharField(max_length=255)
    
    value = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return self.title



class FAQ(models.Model):
    
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='faqs'
    )
    
    
    question = models.CharField(max_length=255)
    
    answer = models.TextField(max_length=255, blank=True)
    
    def __str__(self):
        return self.question



class Comment(models.Model):
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    name = models.CharField(max_length=100)
    
    email = models.EmailField()
    
    content = models.TextField()
    
    approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} - {self.article.title}"
        


class ArticleLike(models.Model):
    
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    
    browser_id = models.CharField(blank=True, 
        max_length=64, 
        db_index=True
    )
    
    # user = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE
    # )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields= [
                    'article',
                    'browser_id',
                ],
                name='unique_article_browser_like',
            )
            ]
        
    def __str__(self):
        return (
            f"{self.article.title} - "
            f"{self.browser_id}"
        )


class ArticleFeedback(models.Model):
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="feedback"
    )
    
    browser_id = models.CharField(blank=True, max_length=255)
    
    helpful = models.BooleanField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('article', 'browser_id')




class Profile(models.Model):
    name = models.CharField(
        max_length=100,
        default="El"
    )
    
    role = models.CharField(
        max_length=100,
        blank=True, 
        default=''
    )

    photo = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True
    )

    tagline = models.CharField(
        max_length=255,
        blank=True
    )

    bio = models.TextField(
        blank=True
    )

    instagram = models.URLField(
        blank=True
    )

    facebook = models.URLField(
        blank=True
    )

    youtube = models.URLField(
        blank=True
    )

    tiktok = models.URLField(
        blank=True
    )

    pinterest = models.URLField(
        blank=True
    )
    
    linkedin = models.URLField(
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profile"

    def save(self, *args, **kwargs):
        if not self.pk and Profile.objects.exists():
            raise ValidationError('Only one Profile instance is allowed.')
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name




class About(models.Model):
    title = models.CharField(
        max_length=200,
        default="About Me"
    )

    content = CKEditor5Field(
        config_name="extends"
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "About"
        verbose_name_plural = "About"

    def save(self, *args, **kwargs):
        if not self.pk and About.objects.exists():
            raise ValidationError('Only one About instance is allowed.')
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title




class Contact(models.Model):
    title = models.CharField(
        max_length=200,
        default="Get in Touch"
    )

    introduction = CKEditor5Field(
        config_name="extends",
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    phone = models.CharField(
        max_length=50,
        blank=True
    )

    whatsapp = models.CharField(
        max_length=50,
        blank=True
    )

    address = models.CharField(
        max_length=255,
        blank=True
    )

    instagram = models.URLField(
        blank=True
    )

    linkedin = models.URLField(
        blank=True
    )
    
    facebook = models.URLField(
        blank=True
    )

    youtube = models.URLField(
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contact"

    def save(self, *args, **kwargs):
        if not self.pk and Contact.objects.exists():
            raise ValidationError('Only one Contact instance is allowed.')
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



class Hero(models.Model):
    
    article = models.OneToOneField(
        Article,
        on_delete=models.CASCADE,
        related_name='hero',
        help_text='Select the article to display as the homepage hero.'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Homepage Hero: {self.article.title}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            Hero.objects.all().delete()
            
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'Homepage Hero'
        verbose_name_plural = 'Homepage Hero'



class TravelResource(models.Model):
    CATEGORY_CHOICES = [
        ('planning', 'Travel Planning'),
        ('essentials', 'Travel Essentials'),
        ('accommodation', 'Accommodation'),
        ('transportation', 'Getting Around'),
        ('things_to_do', 'Things To Do'),
        ('opportunities', 'Travel Opportunities'),
    ]
    
    title = models.CharField(max_length=200)
    
    slug = models.SlugField(max_length=220, unique=True, blank=True,)
    
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES,)
    
    partner = models.ForeignKey(
        'TravelPartner',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='resources',
    )
    
    description = models.TextField()
    
    image = models.ImageField(
        upload_to='travel_resources/', 
        blank=True, 
        null=True,
    )
    
    external_url = models.URLField(blank=True, null=True)
    
    is_featured = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Travel Resources'
        verbose_name_plural ='Travel Resources'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            
        super().save(*args, **kwargs)



class PartnerPackage(models.Model):
    PACKAGE_CHOICES = [
        ("standard", "Standard Listing"),
        ("featured", "Featured Partner"),
        ("sponsored", "Sponsored Feature"),
    ]

    name = models.CharField(
        max_length=30,
        choices=PACKAGE_CHOICES,
        unique=True
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Partner Package"
        verbose_name_plural = "Partner Packages"
        ordering = ["name"]

    def __str__(self):
        return self.get_name_display()




class TravelPartner(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("active", "Active"),
        ("paused", "Paused"),
        ("expired", "Expired"),
        ("rejected", "Rejected"),
    ]

    business_name = models.CharField(max_length=200)

    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True
    )

    business_type = models.CharField(
        max_length=100,
        blank=True
    )

    description = models.TextField(blank=True)

    logo = models.ImageField(
        upload_to="travel_partners/logos/",
        blank=True,
        null=True
    )
    
    main_image = models.ImageField(
        upload_to='travel_partners/images',
        blank=True,
        null=True,
    )

    location = models.CharField(
        max_length=255,
        blank=True
    )

    country = models.CharField(
        max_length=100,
        blank=True
    )

    phone = models.CharField(
        max_length=50,
        blank=True
    )

    email = models.EmailField(blank=True)

    website_url = models.URLField(
        blank=True,
        null=True
    )

    booking_url = models.URLField(
        blank=True,
        null=True
    )

    instagram_url = models.URLField(
        blank=True,
        null=True
    )

    facebook_url = models.URLField(
        blank=True,
        null=True
    )

    package = models.ForeignKey(
        PartnerPackage,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="partners"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.business_name)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Travel Partner"
        verbose_name_plural = "Travel Partners"
        ordering = ["-created_at"]




class PartnerSubmission(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    business_name = models.CharField(
        max_length=200
    )

    contact_name = models.CharField(
        max_length=150
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=50,
        blank=True
    )

    business_type = models.CharField(
        max_length=100,
        blank=True
    )

    location = models.CharField(
        max_length=255,
        blank=True
    )

    country = models.CharField(
        max_length=100,
        blank=True
    )

    website_url = models.URLField(
        blank=True,
        null=True
    )

    booking_url = models.URLField(
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True
    )
    
    logo = models.ImageField(
        upload_to='partner_submissions/logos',
        blank=True,
        null=True,
    )
    
    main_image = models.ImageField(
        upload_to='partner_submissions/images',
        blank=True,
        null=True,
    )
    
    consent_to_publish = models.BooleanField(
        default=False,
    )
    
    accepted_terms = models.BooleanField(
        default=False,
    )

    instagram_url = models.URLField(
        blank=True,
        null=True
    )

    facebook_url = models.URLField(
        blank=True,
        null=True
    )

    requested_package = models.CharField(
        max_length=30,
        choices=PartnerPackage.PACKAGE_CHOICES,
        default="standard"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    admin_notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Partner Submission"
        verbose_name_plural = "Partner Submissions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.business_name} — {self.get_status_display()}"




class WebsitePage(models.Model):
    PAGE_CHOICES = [
        ("partner-with-us", "Partner with Us"),
        ("privacy-policy", "Privacy Policy"),
        ("terms-and-disclaimers", "Terms and Disclaimers"),
    ]

    page_type = models.SlugField(
        max_length=60,
        choices=PAGE_CHOICES,
        unique=True,
    )

    title = models.CharField(max_length=200)

    introduction = models.TextField(
        blank=True,
        help_text="Optional introduction displayed below the page title.",
    )

    content = CKEditor5Field(
        config_name="extends",
        blank=True,
        default="",
        help_text="Write and format the main page content here.",
    )

    is_published = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Website Page"
        verbose_name_plural = "Website Pages"
        ordering = ["title"]

    def __str__(self):
        return self.title