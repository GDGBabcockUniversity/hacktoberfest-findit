"""
FindIt Forms Module - Refactored to Follow DRY Principles

This module contains form classes for the FindIt lost and found system.
Refactored to eliminate code duplication between LostItemForm and FoundItemForm
by introducing a base ItemForm class.

Author: Refactored for Issue #8
Date: October 2024
"""

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import LostItem, FoundItem


# ============================================================================
# Base Form Class (DRY Principle)
# ============================================================================

class BaseItemForm(forms.ModelForm):
    """
    Base form class for item reporting forms.
    
    This class contains all common fields and validation logic shared between
    LostItemForm and FoundItemForm, following the DRY (Don't Repeat Yourself) principle.
    
    Common Fields:
    - item_name: Name/description of the item
    - color: Color of the item
    - item_type: Category/type of item
    - brand: Brand name (optional)
    - description: Detailed description
    - location: Last known location or found location
    - contact_name: Reporter's name
    - contact_email: Reporter's email
    - contact_phone: Reporter's phone number
    """
    
    # Phone number validator
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    # Common form fields
    item_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter item name',
            'autocomplete': 'off'
        }),
        help_text='Brief name or description of the item'
    )
    
    color = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter color',
            'autocomplete': 'off'
        }),
        help_text='Primary color of the item'
    )
    
    item_type = forms.ChoiceField(
        required=True,
        choices=[
            ('', 'Select item type'),
            ('electronics', 'Electronics'),
            ('clothing', 'Clothing'),
            ('accessories', 'Accessories'),
            ('documents', 'Documents'),
            ('bags', 'Bags & Luggage'),
            ('jewelry', 'Jewelry'),
            ('keys', 'Keys'),
            ('wallet', 'Wallet/Purse'),
            ('phone', 'Mobile Phone'),
            ('laptop', 'Laptop/Tablet'),
            ('books', 'Books/Notebooks'),
            ('sports', 'Sports Equipment'),
            ('pet', 'Pet'),
            ('other', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Category of the item'
    )
    
    brand = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter brand (if applicable)',
            'autocomplete': 'off'
        }),
        help_text='Brand name (optional)'
    )
    
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Provide detailed description...',
            'rows': 4
        }),
        help_text='Detailed description including distinctive features'
    )
    
    location = forms.CharField(
        max_length=300,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter location',
            'autocomplete': 'off'
        })
    )
    
    contact_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name',
            'autocomplete': 'name'
        }),
        help_text='Your name for contact purposes'
    )
    
    contact_email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
            'autocomplete': 'email'
        }),
        help_text='Valid email address for notifications'
    )
    
    contact_phone = forms.CharField(
        max_length=15,
        required=True,
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1234567890',
            'autocomplete': 'tel'
        }),
        help_text='Phone number with country code'
    )
    
    # Image field (optional)
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text='Upload an image of the item (optional, max 5MB)'
    )
    
    class Meta:
        abstract = True
        
    def clean_item_name(self):
        """Validate and clean item name."""
        item_name = self.cleaned_data.get('item_name')
        if item_name:
            item_name = item_name.strip()
            if len(item_name) < 3:
                raise ValidationError('Item name must be at least 3 characters long.')
        return item_name
    
    def clean_description(self):
        """Validate and clean description."""
        description = self.cleaned_data.get('description')
        if description:
            description = description.strip()
            if len(description) < 10:
                raise ValidationError('Description must be at least 10 characters long.')
            if len(description) > 1000:
                raise ValidationError('Description cannot exceed 1000 characters.')
        return description
    
    def clean_contact_email(self):
        """Validate and normalize email."""
        email = self.cleaned_data.get('contact_email')
        if email:
            email = email.lower().strip()
        return email
    
    def clean_contact_phone(self):
        """Validate and clean phone number."""
        phone = self.cleaned_data.get('contact_phone')
        if phone:
            # Remove spaces and dashes
            phone = phone.replace(' ', '').replace('-', '')
        return phone
    
    def clean_location(self):
        """Validate and clean location."""
        location = self.cleaned_data.get('location')
        if location:
            location = location.strip()
            if len(location) < 3:
                raise ValidationError('Location must be at least 3 characters long.')
        return location
    
    def clean_image(self):
        """Validate uploaded image."""
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Image file size cannot exceed 5MB.')
            
            # Check file type
            valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if hasattr(image, 'content_type') and image.content_type not in valid_types:
                raise ValidationError('Only JPEG, PNG, and GIF images are allowed.')
        
        return image
    
    def clean(self):
        """
        Additional form-level validation.
        Override this method in child classes for specific validation.
        """
        cleaned_data = super().clean()
        
        # Example: Ensure at least one contact method is provided
        email = cleaned_data.get('contact_email')
        phone = cleaned_data.get('contact_phone')
        
        if not email and not phone:
            raise ValidationError('At least one contact method (email or phone) is required.')
        
        return cleaned_data


# ============================================================================
# Lost Item Form
# ============================================================================

class LostItemForm(BaseItemForm):
    """
    Form for reporting lost items.
    
    Inherits all common fields and validation from BaseItemForm.
    Customizes the location field label and help text for lost items context.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize location field for lost items
        self.fields['location'].label = 'Last Seen Location'
        self.fields['location'].help_text = 'Where did you last see the item?'
        self.fields['location'].widget.attrs['placeholder'] = 'Enter last seen location'
    
    class Meta:
        model = LostItem
        fields = [
            'item_name',
            'color',
            'item_type',
            'brand',
            'description',
            'location',
            'contact_name',
            'contact_email',
            'contact_phone',
            'image'
        ]
    
    def clean(self):
        """Additional validation specific to lost items."""
        cleaned_data = super().clean()
        
        # Add any lost item specific validation here
        # For example: Check if similar lost item already exists
        item_name = cleaned_data.get('item_name')
        location = cleaned_data.get('location')
        
        if item_name and location:
            # Check for potential duplicates
            from datetime import timedelta
            from django.utils import timezone
            
            recent_date = timezone.now() - timedelta(days=7)
            similar_items = LostItem.objects.filter(
                item_name__icontains=item_name,
                location__icontains=location,
                date_reported__gte=recent_date
            ).exists()
            
            if similar_items:
                # Just a warning, don't prevent submission
                self.add_error(None, ValidationError(
                    'A similar item has been reported recently. '
                    'Please check existing reports before submitting.',
                    code='duplicate_warning'
                ))
        
        return cleaned_data


# ============================================================================
# Found Item Form
# ============================================================================

class FoundItemForm(BaseItemForm):
    """
    Form for reporting found items.
    
    Inherits all common fields and validation from BaseItemForm.
    Customizes the location field label and help text for found items context.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize location field for found items
        self.fields['location'].label = 'Found Location'
        self.fields['location'].help_text = 'Where did you find the item?'
        self.fields['location'].widget.attrs['placeholder'] = 'Enter found location'
    
    class Meta:
        model = FoundItem
        fields = [
            'item_name',
            'color',
            'item_type',
            'brand',
            'description',
            'location',
            'contact_name',
            'contact_email',
            'contact_phone',
            'image'
        ]
    
    def clean(self):
        """Additional validation specific to found items."""
        cleaned_data = super().clean()
        
        # Add any found item specific validation here
        # For example: Suggest potential matches with lost items
        item_name = cleaned_data.get('item_name')
        color = cleaned_data.get('color')
        
        if item_name and color:
            # Check for potential matches with lost items
            potential_matches = LostItem.objects.filter(
                item_name__icontains=item_name,
                color__iexact=color,
                status='active'
            ).count()
            
            if potential_matches > 0:
                # Informational message, not an error
                from django.contrib import messages
                # Note: messages framework needs request context
                # This is just for demonstration
                pass
        
        return cleaned_data


# ============================================================================
# Additional Helper Forms
# ============================================================================

class ItemSearchForm(forms.Form):
    """Form for searching items."""
    
    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by item name, color, or description...',
            'autocomplete': 'off'
        })
    )
    
    location = forms.CharField(
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by location...',
            'autocomplete': 'off'
        })
    )
    
    item_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + BaseItemForm.item_type.field.choices[1:],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class ClaimItemForm(forms.Form):
    """Form for claiming an item."""
    
    proof_description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Describe the item in detail to prove ownership...',
            'rows': 4
        }),
        help_text='Provide specific details that only the owner would know'
    )
    
    contact_email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
    )
    
    def clean_proof_description(self):
        """Validate proof description."""
        proof = self.cleaned_data.get('proof_description')
        if proof and len(proof) < 20:
            raise ValidationError('Please provide more detailed proof of ownership (at least 20 characters).')
        return proof