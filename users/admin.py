from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from users.models import User


@admin.register(User)
class UserAdmin(UserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    fieldsets = (
        (
            UserAdmin.fieldsets[0][0],
            {
                "fields": UserAdmin.fieldsets[0][1]["fields"]
                + ("phone_number", "birthday", "profile_picture"),
            },
        ),
    ) + UserAdmin.fieldsets[1:]
