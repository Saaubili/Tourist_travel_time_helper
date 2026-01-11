from django import forms
from data_receiver.models import City


class CitySelectForm(forms.Form):
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=forms.HiddenInput()
    )