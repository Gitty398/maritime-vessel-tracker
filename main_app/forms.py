from django import forms
from .models import SavedVessel

class SavedVesselForm(forms.ModelForm):
    class Meta:
        model = SavedVessel
        fields = ["mmsi", "name", "imo"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Optional"}),
            "imo": forms.TextInput(attrs={"placeholder": "Optional"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["mmsi"].disabled = True