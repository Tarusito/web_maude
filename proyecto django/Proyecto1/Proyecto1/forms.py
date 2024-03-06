# forms.py
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.core.exceptions import ValidationError
import re



class RegistrationForm(forms.Form):
    nombre = forms.CharField(label='Nombre', max_length=100)
    correo_ucm = forms.EmailField(label='Correo UCM')
    contraseña = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    confirmar_contraseña = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    def clean_correo_ucm(self):
        correo = self.cleaned_data['correo_ucm']
        if not correo.endswith('@ucm.es'):
            raise ValidationError('El correo debe ser una dirección @ucm.es')
        return correo

    def clean(self):
        cleaned_data = super().clean()
        contraseña = cleaned_data.get('contraseña')
        confirmar_contraseña = cleaned_data.get('confirmar_contraseña')

        # Validar la contraseña
        if contraseña and not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$', contraseña):
            self.add_error('contraseña', 'La contraseña debe tener más de 8 caracteres, incluyendo un número, una letra minúscula y una mayúscula.')

        # Comprobar que las contraseñas coincidan
        if contraseña and confirmar_contraseña and contraseña != confirmar_contraseña:
            self.add_error('confirmar_contraseña', 'Las contraseñas no coinciden.')

        return cleaned_data
    
class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'validate', 'placeholder': 'Correo UCM', 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        # Cambia el label del campo 'username' a 'Correo electrónico'
        self.fields['username'].label = "Correo electrónico"
