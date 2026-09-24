from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]
        input_class = (
            "w-full rounded-lg bg-aether-bg border border-white/10 px-3 py-2 "
            "text-slate-200 focus:outline-none focus:border-aether-accent"
        )
        widgets = {
            "name": forms.TextInput(attrs={"class": input_class}),
            "email": forms.EmailInput(attrs={"class": input_class}),
            "message": forms.Textarea(attrs={"class": input_class, "rows": 5}),
        }
