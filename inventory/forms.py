from django import forms
from .models import Variant, Location


class TransferForm(forms.Form):
    variant = forms.ModelChoiceField(queryset=Variant.objects.all())
    source = forms.ModelChoiceField(queryset=Location.objects.all())
    destination = forms.ModelChoiceField(queryset=Location.objects.all())
    quantity = forms.IntegerField(min_value=1)
    unit = forms.ChoiceField(choices=[("pieces","Pieces"),("cartons","Cartons")])
