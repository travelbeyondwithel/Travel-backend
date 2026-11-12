from django import forms 
from .models import(
    Article, 
    # ArticleSection, 
    QuickTip, 
    FAQ,
    GalleryImage)

    # Article Form

class ArticleForm(forms.ModelForm):
    
    class Meta:
        model =Article 
        
        fields = [ 
            'title',
            'subtitle', 
            'slug',
            'category', 
            'hero_image',
            'hero_image_alt', 
            'hero_image_caption', 
            'introduction', 
            'seo_title', 
            'meta_description',
            'focus_keyword', 
            'status', 
            'published_at'
        ]
        widgets = { 
            
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Article title...'
            }),
            
            'subtitle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subtitle...'
            }),
            
            'slug': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            
            'hero_image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            
            'hero_image_alt': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the image for accessibility'
            }),
            
            'hero_image_caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Image caption'
            }),
            
            'introduction': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Write your introduction...'
            }),
            
            'seo_title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            
            'focus_keyword': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            
            'published_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }

    # Article Section Form

# class ArticleSectionForm(forms.ModelForm):
    
#     class Meta:
        
#         model = ArticleSection
        
#         fields = [
#             'heading',
#             'image',
#             'image_caption',
#             'body',
#             'order',
#         ]
        
#         widgets = {
            
#             'heading': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Section Heading'
#             }),
            
#             'image': forms.ClearableFileInput(attrs={
#                 'class': 'form-control'
#             }),
            
#             'image_caption': forms.TextInput(attrs={
#                 'class': 'form-control'
#             }),
            
#             'body': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 12
#             }),
            
#             'order': forms.NumberInput(attrs={
#                 'class': 'form-control'
#             }),
            
#         }

    # QuickTip Form

class QuickTipForm(forms.ModelForm):
    
    class Meta:
        
        model = QuickTip
        
        fields = ['tip']
        
        widgets = {
            
            'tip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: Bring hiking shoes'
            })
            
        }

    # FAQ Form

class FAQForm(forms.ModelForm):
    
    class Meta:
        
        model = FAQ
        
        fields = [
            'question',
            'answer'
        ]
        
        widgets = {
            
            'question': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            
            'answer': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            })
            
        }
        
        # Gallery Form 
        
class GalleryImageForm(forms.ModelForm):
    
    class Meta:
        
        model = GalleryImage
        
        fields = [
            'image',
            'caption',
            'order'
        ]
        
        widgets = {
            
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            
            'caption': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            
            'order': forms.NumberInput(attrs={
                'class': 'form-control'
            })
            
        }
        