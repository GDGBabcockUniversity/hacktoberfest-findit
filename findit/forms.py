from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import UserProfile, LostItem, FoundItem

class AuthForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'', 'placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'', 'placeholder':'Password'}))





class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':'input', 'placeholder':'Email'}))
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'input', 'placeholder':'username'}))
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'input', 'placeholder':'Password'}))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'input', 'placeholder':'Confirm Password'}))
    phone_number = forms.CharField(required=True, max_length=255, widget=forms.TextInput(attrs={'class':'input', 'placeholder':'Phone Number'}))
    first_name = forms.CharField(required=True, max_length=30, widget=forms.TextInput(attrs={'class':'input', 'placeholder':'First Name'}))
    last_name = forms.CharField(required=True, max_length=30, widget=forms.TextInput(attrs={'class':'input', 'placeholder':'Last Name'}))
    
    class Meta:
        model = UserProfile
        fields = [ 'first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'phone_number',]


    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class updateProfileForm(forms.ModelForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class':'input', 'placeholder':'Email'}))
    username = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'input', 'placeholder':'username'}))
    phone_number = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'class':'input', 'placeholder':'Phone Number'}))
    first_name = forms.CharField(required=False, max_length=30, widget=forms.TextInput(attrs={'class':'input', 'placeholder':'First Name'}))
    last_name = forms.CharField(required=False, max_length=30, widget=forms.TextInput(attrs={'class':'input', 'placeholder':'Last Name'}))
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = [ 'first_name', 'last_name', 'username', 'email', 'phone_number','profile_image']


    # def save(self, commit=True):
    #     user = super(RegistrationForm, self).save(commit=False)
    #     user.email = self.cleaned_data['email']
    #     if commit:
    #         user.save()
    #     return user

class LostItemForm(forms.ModelForm):
    class Meta:
        model = LostItem
        fields = ['description', 'color', 'brand', 'distinctive_features', 'image', 'last_known_location']
        # Changes how the fields are displayed on the form
        labels = {
            'description': 'Name of Item',
            'color': 'Color',
            'brand': 'Brand',
            'distinctive_features': 'Description of Item',
            'last_known_location': 'Last Known Location',
            'image': 'Image',
        }
        widget = {
            
        }

class FoundItemForm(forms.ModelForm):
    class Meta:
        model = FoundItem
        fields = ['description', 'color', 'brand', 'distinctive_features', 'image', 'last_known_location']
        labels = {
            'description': 'Name of Item',
            'color': 'Color',
            'brand': 'Brand',
            'distinctive_features': 'Description of Item',
            'last_known_location': 'Last Known Location',
            'image': 'Image',
        }
        widget = {
            'description': forms.TextInput(attrs={'class': 'input', 'placeholder': 'e.g Airpods MAX'}),
            'color': forms.TextInput(attrs={'class': 'input', 'placeholder': 'e.g Grey'}),
            'brand': forms.TextInput(attrs={'class': 'input', 'placeholder': 'e.g Apple'}),
            'distinctive_features': forms.Textarea(attrs={'class': 'input', 'placeholder': 'e.g Has a scratch on the left side'}),
            'last_known_location': forms.TextInput(attrs={'class': 'input', 'placeholder': 'e.g Library'}),
            'image': forms.ClearableFileInput(attrs={'class': ''}),
        }
