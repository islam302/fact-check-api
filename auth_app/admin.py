from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import CustomUser


class CustomUserAdminForm(forms.ModelForm):
    sender_emails_input = forms.CharField(
        label='Sender Emails',
        help_text='Enter email addresses separated by commas (e.g., email1@example.com, email2@example.com)',
        required=False,
        widget=forms.TextInput(attrs={'style': 'width: 100%;', 'placeholder': 'email1@example.com, email2@example.com'})
    )

    class Meta:
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.sender_emails:
            # Convert JSON list to comma-separated string
            self.fields['sender_emails_input'].initial = ', '.join(self.instance.sender_emails)

    def save(self, commit=True):
        instance = super().save(commit=False)
        emails_str = self.cleaned_data.get('sender_emails_input', '')
        if emails_str:
            # Split by comma and clean up whitespace
            emails_list = [email.strip() for email in emails_str.split(',') if email.strip()]
            instance.sender_emails = emails_list
        else:
            instance.sender_emails = []
        if commit:
            instance.save()
        return instance


class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm
    list_display = ('id', 'username', 'email', 'role', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'sender_name', 'sender_emails_input')}),
        ('Permissions', {'fields': ('role', 'is_staff', 'groups', 'user_permissions')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)