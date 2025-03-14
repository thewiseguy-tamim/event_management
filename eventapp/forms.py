# forms.py
from django import forms
from .models import Event, Category, RSVP
from django.contrib.auth.models import User

class StyledFormMixin:
    """Mixin to apply style to form fields"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()

    default_classes = "border-2 border-gray-300 w-full p-3 rounded-lg shadow-sm focus:outline-none focus:border-rose-500 focus:ring-rose-500"

    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():
            if isinstance(self.fields[field_name].widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateInput, forms.EmailInput)):
                self.fields[field_name].widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': f"Enter {field_name.replace('_', ' ').capitalize()}"
                })


class EventCreationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'location', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'border-2 border-gray-300 w-full p-3 rounded-lg shadow-sm focus:outline-none focus:border-rose-500 focus:ring-rose-500'
            })


class RSVPForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = RSVP
        fields = ['event', 'response']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event'].queryset = Event.objects.all() 

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'border-2 border-gray-300 w-full p-3 rounded-lg shadow-sm focus:outline-none focus:border-rose-500 focus:ring-rose-500'
            })

from django import forms
from .models import RSVP

class RSVPForm(forms.ModelForm):
    class Meta:
        model = RSVP
        fields = ['response']
        widgets = {
            'response': forms.RadioSelect(choices=((True, 'Yes'), (False, 'No')))
        }