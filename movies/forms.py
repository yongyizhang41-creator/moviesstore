from django import forms
from .models import Rating

class RatingForm(forms.ModelForm):
    score = forms.TypedChoiceField(
        choices = [(value, f'{value} / 5') for value in range(1,6)],
        coerce = int,
        widget = forms.RadioSelect,
        label = 'Your rating',
    )

    class Meta: 
        model = Rating
        fields = ['score']