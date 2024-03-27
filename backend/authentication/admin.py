from django.contrib import admin
from .models import User  # Adjust the import according to your app structure


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ("email", "first_name", "last_name")
    pass  # You can customize the admin model as needed
