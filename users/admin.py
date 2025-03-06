from django.contrib import admin
from users.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = [
        "username",
        "gender"
    ]

    def username(self, obj):
        return obj.user.username
