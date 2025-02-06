from django import forms
from .models import Event, Participant, Category

class StyledFormMixin:
    """Mixin to apply style to form fields"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()

    default_classes = "border-2 border-gray-300 w-full p-3 rounded-lg shadow-sm focus:outline-none focus:border-blue-500 focus:ring-blue-500"

    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():
            if isinstance(self.fields[field_name].widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateInput, forms.EmailInput)):
                self.fields[field_name].widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': f"Enter {field_name.replace('_', ' ').capitalize()}"
                })

class EventForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

class ParticipantForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['name', 'email']
        
class CategoryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
