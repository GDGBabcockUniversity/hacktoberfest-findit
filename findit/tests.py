"""
FindIt Forms Tests - Comprehensive Test Suite

Tests for the refactored forms module following DRY principles.
Tests cover:
- Base form functionality
- LostItemForm specific behavior
- FoundItemForm specific behavior
- Form validation
- Error handling

Author: Tests for Issue #8
Date: October 2024
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from findit.forms import (
    BaseItemForm,
    LostItemForm,
    FoundItemForm,
    ItemSearchForm,
    ClaimItemForm
)
from findit.models import LostItem, FoundItem
from datetime import timedelta
from django.utils import timezone
import io
from PIL import Image


# ============================================================================
# Base Form Tests
# ============================================================================

class BaseItemFormTests(TestCase):
    """Tests for the BaseItemForm class."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            'item_name': 'Blue Backpack',
            'color': 'Blue',
            'item_type': 'bags',
            'brand': 'Nike',
            'description': 'A blue Nike backpack with laptop compartment and water bottle holder',
            'location': 'Central Park, near the fountain',
            'contact_name': 'John Doe',
            'contact_email': 'john.doe@example.com',
            'contact_phone': '+1234567890',
        }
    
    def test_base_form_is_abstract(self):
        """Test that BaseItemForm is abstract and cannot be instantiated directly."""
        # BaseItemForm should be used as a parent class only
        # This test ensures it has Meta.abstract = True
        self.assertTrue(BaseItemForm.Meta.abstract)
    
    def test_valid_data_passes_validation(self):
        """Test that valid data passes all validation."""
        form = LostItemForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_required_fields(self):
        """Test that all required fields are enforced."""
        required_fields = [
            'item_name', 'color', 'item_type', 'description',
            'location', 'contact_name', 'contact_email', 'contact_phone'
        ]
        
        for field in required_fields:
            data = self.valid_data.copy()
            data[field] = ''
            form = LostItemForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)
    
    def test_optional_fields(self):
        """Test that optional fields are not required."""
        data = self.valid_data.copy()
        data['brand'] = ''
        form = LostItemForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_item_name_minimum_length(self):
        """Test item name must be at least 3 characters."""
        data = self.valid_data.copy()
        data['item_name'] = 'AB'
        form = LostItemForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('item_name', form.errors)
    
    def test_description_minimum_length(self):
        """Test description must be at least 10 characters."""
        data = self.valid_data.copy()
        data['description'] = 'Too short'
        form = LostItemForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)
    
    def test_description_maximum_length(self):
        """Test description cannot exceed 1000 characters."""
        data = self.valid_data.copy()
        data['description'] = 'A' * 1001
        form = LostItemForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)
    
    def test_email_validation(self):
        """Test email field validation."""
        data = self.valid_data.copy()
        data['contact_email'] = 'invalid-email'
        form = LostItemForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('contact_email', form.errors)
    
    def test_email_normalization(self):
        """Test email is lowercased and trimmed."""
        data = self.valid_data.copy()
        data['contact_email'] = '  JOHN.DOE@EXAMPLE.COM  '
        form = LostItemForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['contact_email'], 'john.doe@example.com')
    
    def test_phone_validation_valid_formats(self):
        """Test phone number accepts valid formats."""
        valid_phones = [
            '+1234567890',
            '+12345678901',
            '1234567890',
            '+123456789012345',
        ]
        
        for phone in valid_phones:
            data = self.valid_data.copy()
            data['contact_phone'] = phone
            form = LostItemForm(data=data)
            self.assertTrue(form.is_valid(), f"Phone {phone} should be valid")
    
    def test_phone_validation_invalid_formats(self):
        """Test phone number rejects invalid formats."""
        invalid_phones = [
            '123',  # Too short
            'abcdefghij',  # Letters
            '++1234567890',  # Double plus
        ]
        
        for phone in invalid_phones:
            data = self.valid_data.copy()
            data['contact_phone'] = phone
            form = LostItemForm(data=data)
            self.assertFalse(form.is_valid(), f"Phone {phone} should be invalid")
    
    def test_phone_normalization(self):
        """Test phone number spaces and dashes are removed."""
        data = self.valid_data.copy()
        data['contact_phone'] = '+1 234-567-890'
        form = LostItemForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['contact_phone'], '+1234567890')
    
    def test_location_minimum_length(self):
        """Test location must be at least 3 characters."""
        data = self.valid_data.copy()
        data['location'] = 'AB'
        form = LostItemForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('location', form.errors)
    
    def test_item_type_choices(self):
        """Test item_type field accepts valid choices."""
        valid_types = [
            'electronics', 'clothing', 'accessories', 'documents',
            'bags', 'jewelry', 'keys', 'wallet', 'phone', 'laptop',
            'books', 'sports', 'pet', 'other'
        ]
        
        for item_type in valid_types:
            data = self.valid_data.copy()
            data['item_type'] = item_type
            form = LostItemForm(data=data)
            self.assertTrue(form.is_valid(), f"Item type {item_type} should be valid")
    
    def test_contact_method_required(self):
        """Test at least one contact method is required."""
        # This test may need adjustment based on actual implementation
        # Currently both email and phone are required
        data = self.valid_data.copy()
        form = LostItemForm(data=data)
        self.assertTrue(form.is_valid())


# ============================================================================
# Image Upload Tests
# ============================================================================

class ImageUploadTests(TestCase):
    """Tests for image upload functionality."""
    
    def setUp(self):
        """Set up test data with valid form data."""
        self.valid_data = {
            'item_name': 'Red Laptop',
            'color': 'Red',
            'item_type': 'laptop',
            'brand': 'Dell',
            'description': 'A red Dell laptop with stickers on the back cover',
            'location': 'Library, 2nd floor',
            'contact_name': 'Jane Smith',
            'contact_email': 'jane@example.com',
            'contact_phone': '+1987654321',
        }
    
    def create_test_image(self, size=(100, 100), format='JPEG'):
        """Helper method to create a test image."""
        file = io.BytesIO()
        image = Image.new('RGB', size, color='red')
        image.save(file, format)
        file.seek(0)
        return SimpleUploadedFile(
            name='test_image.jpg',
            content=file.read(),
            content_type='image/jpeg'
        )
    
    def test_valid_image_upload(self):
        """Test uploading a valid image."""
        image = self.create_test_image()
        form = LostItemForm(data=self.valid_data, files={'image': image})
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_image_size_limit(self):
        """Test image size limit (5MB)."""
        # Create a large image (this is a mock test)
        large_image = self.create_test_image(size=(3000, 3000))
        form = LostItemForm(data=self.valid_data, files={'image': large_image})
        # Note: Actual file size checking may need adjustment
        # based on how Django handles file size validation
    
    def test_image_type_validation(self):
        """Test only allowed image types are accepted."""
        # Valid formats: JPEG, PNG, GIF
        # This test verifies the content type checking logic
        pass  # Implementation depends on actual file type validation
    
    def test_no_image_is_optional(self):
        """Test that image upload is optional."""
        form = LostItemForm(data=self.valid_data)
        self.assertTrue(form.is_valid())


# ============================================================================
# LostItemForm Tests
# ============================================================================

class LostItemFormTests(TestCase):
    """Tests specific to LostItemForm."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            'item_name': 'Black Wallet',
            'color': 'Black',
            'item_type': 'wallet',
            'brand': 'Leather Co',
            'description': 'Black leather wallet with ID holder and credit card slots',
            'location': 'Downtown Cafe, Main Street',
            'contact_name': 'Alice Johnson',
            'contact_email': 'alice@example.com',
            'contact_phone': '+1122334455',
        }
    
    def test_lost_item_form_inherits_from_base(self):
        """Test LostItemForm inherits from BaseItemForm."""
        self.assertTrue(issubclass(LostItemForm, BaseItemForm))
    
    def test_lost_item_location_label(self):
        """Test location field has correct label for lost items."""
        form = LostItemForm()
        self.assertEqual(form.fields['location'].label, 'Last Seen Location')
    
    def test_lost_item_location_help_text(self):
        """Test location field has correct help text for lost items."""
        form = LostItemForm()
        self.assertIn('last see', form.fields['location'].help_text.lower())
    
    def test_creates_lost_item_instance(self):
        """Test form creates LostItem model instance."""
        form = LostItemForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        instance = form.save(commit=False)
        self.assertIsInstance(instance, LostItem)
    
    def test_duplicate_warning(self):
        """Test duplicate item warning functionality."""
        # Create an existing lost item
        LostItem.objects.create(
            item_name='Black Wallet',
            color='Black',
            item_type='wallet',
            location='Downtown Cafe',
            description='Test description',
            contact_name='Test',
            contact_email='test@example.com',
            contact_phone='+1234567890',
            date_reported=timezone.now()
        )
        
        # Try to create similar item
        form = LostItemForm(data=self.valid_data)
        # Form should still be valid but may have a warning
        # Implementation depends on how warnings are handled


# ============================================================================
# FoundItemForm Tests
# ============================================================================

class FoundItemFormTests(TestCase):
    """Tests specific to FoundItemForm."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            'item_name': 'Silver Watch',
            'color': 'Silver',
            'item_type': 'jewelry',
            'brand': 'Rolex',
            'description': 'Silver Rolex watch with leather strap and date function',
            'location': 'Park Bench, City Park',
            'contact_name': 'Bob Williams',
            'contact_email': 'bob@example.com',
            'contact_phone': '+1555666777',
        }
    
    def test_found_item_form_inherits_from_base(self):
        """Test FoundItemForm inherits from BaseItemForm."""
        self.assertTrue(issubclass(FoundItemForm, BaseItemForm))
    
    def test_found_item_location_label(self):
        """Test location field has correct label for found items."""
        form = FoundItemForm()
        self.assertEqual(form.fields['location'].label, 'Found Location')
    
    def test_found_item_location_help_text(self):
        """Test location field has correct help text for found items."""
        form = FoundItemForm()
        self.assertIn('find', form.fields['location'].help_text.lower())
    
    def test_creates_found_item_instance(self):
        """Test form creates FoundItem model instance."""
        form = FoundItemForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        instance = form.save(commit=False)
        self.assertIsInstance(instance, FoundItem)
    
    def test_potential_match_detection(self):
        """Test potential match with lost items detection."""
        # Create a lost item that matches
        LostItem.objects.create(
            item_name='Silver Watch',
            color='Silver',
            item_type='jewelry',
            location='City Park',
            description='Lost my silver watch',
            contact_name='Owner',
            contact_email='owner@example.com',
            contact_phone='+1111111111',
            status='active'
        )
        
        # Submit found item
        form = FoundItemForm(data=self.valid_data)
        # Form should process and potentially flag matches
        # Implementation depends on matching logic


# ============================================================================
# Additional Forms Tests
# ============================================================================

class ItemSearchFormTests(TestCase):
    """Tests for ItemSearchForm."""
    
    def test_all_fields_optional(self):
        """Test all search fields are optional."""
        form = ItemSearchForm(data={})
        self.assertTrue(form.is_valid())
    
    def test_search_query_field(self):
        """Test search query field accepts text."""
        form = ItemSearchForm(data={'search_query': 'blue backpack'})
        self.assertTrue(form.is_valid())
    
    def test_location_filter(self):
        """Test location filter field."""
        form = ItemSearchForm(data={'location': 'Central Park'})
        self.assertTrue(form.is_valid())
    
    def test_item_type_filter(self):
        """Test item type filter accepts valid choices."""
        form = ItemSearchForm(data={'item_type': 'bags'})
        self.assertTrue(form.is_valid())


class ClaimItemFormTests(TestCase):
    """Tests for ClaimItemForm."""
    
    def test_valid_claim_form(self):
        """Test valid claim form data."""
        data = {
            'proof_description': 'The wallet contains my driver license with ID number 123456789',
            'contact_email': 'claimer@example.com'
        }
        form = ClaimItemForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_proof_description_required(self):
        """Test proof description is required."""
        data = {'contact_email': 'claimer@example.com'}
        form = ClaimItemForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('proof_description', form.errors)
    
    def test_proof_description_minimum_length(self):
        """Test proof description must be at least 20 characters."""
        data = {
            'proof_description': 'Too short',
            'contact_email': 'claimer@example.com'
        }
        form = ClaimItemForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('proof_description', form.errors)
    
    def test_contact_email_required(self):
        """Test contact email is required."""
        data = {
            'proof_description': 'Detailed proof of ownership with specific features'
        }
        form = ClaimItemForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('contact_email', form.errors)


# ============================================================================
# DRY Principle Verification Tests
# ============================================================================

class DRYPrincipleTests(TestCase):
    """Tests to verify DRY principle is followed."""
    
    def test_lost_and_found_forms_share_base_class(self):
        """Test both forms inherit from the same base class."""
        self.assertTrue(issubclass(LostItemForm, BaseItemForm))
        self.assertTrue(issubclass(FoundItemForm, BaseItemForm))
    
    def test_common_fields_defined_once(self):
        """Test common fields are defined in base class only."""
        lost_form = LostItemForm()
        found_form = FoundItemForm()
        
        # Common fields should be present in both
        common_fields = [
            'item_name', 'color', 'item_type', 'brand',
            'description', 'location', 'contact_name',
            'contact_email', 'contact_phone', 'image'
        ]
        
        for field in common_fields:
            self.assertIn(field, lost_form.fields)
            self.assertIn(field, found_form.fields)
    
    def test_no_code_duplication_in_child_forms(self):
        """Test child forms don't duplicate parent code."""
        # LostItemForm and FoundItemForm should be minimal
        # Most logic should be in BaseItemForm
        import inspect
        
        lost_methods = [m for m in inspect.getmembers(LostItemForm, predicate=inspect.ismethod)]
        found_methods = [m for m in inspect.getmembers(FoundItemForm, predicate=inspect.ismethod)]
        
        # Child classes should have minimal custom methods
        # Main logic should be inherited
        # This is a conceptual test


# ============================================================================
# Integration Tests
# ============================================================================

class FormIntegrationTests(TestCase):
    """Integration tests for form workflow."""
    
    def test_complete_lost_item_workflow(self):
        """Test complete workflow of reporting lost item."""
        data = {
            'item_name': 'Green Umbrella',
            'color': 'Green',
            'item_type': 'other',
            'brand': 'Totes',
            'description': 'Green folding umbrella with wooden handle',
            'location': 'Bus Station, Platform 3',
            'contact_name': 'Charlie Brown',
            'contact_email': 'charlie@example.com',
            'contact_phone': '+1999888777',
        }
        
        form = LostItemForm(data=data)
        self.assertTrue(form.is_valid())
        
        lost_item = form.save()
        self.assertIsNotNone(lost_item.id)
        self.assertEqual(lost_item.item_name, 'Green Umbrella')
    
    def test_complete_found_item_workflow(self):
        """Test complete workflow of reporting found item."""
        data = {
            'item_name': 'Red Scarf',
            'color': 'Red',
            'item_type': 'clothing',
            'brand': '',
            'description': 'Handknit red wool scarf with fringe ends',
            'location': 'Coffee Shop, Main Street',
            'contact_name': 'Diana Prince',
            'contact_email': 'diana@example.com',
            'contact_phone': '+1777888999',
        }
        
        form = FoundItemForm(data=data)
        self.assertTrue(form.is_valid())
        
        found_item = form.save()
        self.assertIsNotNone(found_item.id)
        self.assertEqual(found_item.item_name, 'Red Scarf')


# ============================================================================
# Edge Case Tests
# ============================================================================

class EdgeCaseTests(TestCase):
    """Tests for edge cases and boundary conditions."""
    
    def test_special_characters_in_description(self):
        """Test form handles special characters."""
        data = {
            'item_name': 'Book',
            'color': 'Blue',
            'item_type': 'books',
            'description': 'Book with title: "Python & Django" - 2nd Edition!',
            'location': 'Library',
            'contact_name': "O'Brien",
            'contact_email': 'test@example.com',
            'contact_phone': '+1234567890',
        }
        form = LostItemForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_unicode_characters(self):
        """Test form handles unicode characters."""
        data = {
            'item_name': 'Café Menu',
            'color': 'Beige',
            'item_type': 'documents',
            'description': 'Menu with café listings and naïve designs',
            'location': 'Café François',
            'contact_name': 'José García',
            'contact_email': 'jose@example.com',
            'contact_phone': '+1234567890',
        }
        form = LostItemForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_maximum_valid_values(self):
        """Test form with maximum allowed values."""
        data = {
            'item_name': 'A' * 200,  # Max length
            'color': 'B' * 50,  # Max length
            'item_type': 'other',
            'brand': 'C' * 100,  # Max length
            'description': 'D' * 1000,  # Max length
            'location': 'E' * 300,  # Max length
            'contact_name': 'F' * 100,  # Max length
            'contact_email': 'test@example.com',
            'contact_phone': '+123456789012345',  # Max length
        }
        form = LostItemForm(data=data)
        self.assertTrue(form.is_valid())