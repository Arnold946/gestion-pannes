import secrets
import string
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm
from accounts.models import Role, User
from organisation.models import Unite



def generate_temporary_password(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

class UserCreationFormCustom(forms.ModelForm):

    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=True,
        empty_label="veuillez selectionner un role"
    )
    profile_picture = forms.ImageField(
        label='Photo de profil',
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': False})
    )
    unite = forms.ModelChoiceField(
        queryset=Unite.objects.all(),
        required=True,
        empty_label="veuillez selectionner une unite"
    )
    phone_number = forms.CharField(
        label='Numéro de téléphone',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Numéro de téléphone'})
    )
    password = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        initial=generate_temporary_password,
        help_text="Un mot de passe temporaire sera généré automatiquement et envoyé par e-mail."
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'phone_number', 'profile_picture', 'password', 'unite')


class ModifierUtilisateurForm(forms.ModelForm):

    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=True,
        empty_label="veuillez selectionner un role"
    )
    profile_picture = forms.ImageField(
        label='Photo de profil',
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': False})
    )
    unite = forms.ModelChoiceField(
        queryset=Unite.objects.all(),
        required=True,
        empty_label="veuillez selectionner une unite"
    )
    phone_number = forms.CharField(
        label='Numéro de téléphone',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Numéro de téléphone'})
    )
    password = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        initial=generate_temporary_password,
        help_text="Un mot de passe temporaire sera généré automatiquement et envoyé par e-mail."
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'phone_number', 'profile_picture', 'password', 'unite')

class EmailLoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254)
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if not email or not password:
            raise forms.ValidationError("Veuillez entrer votre email et mot de passe.")
        
        return cleaned_data
    
class PasswordChangeFormCustom(SetPasswordForm):

    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']