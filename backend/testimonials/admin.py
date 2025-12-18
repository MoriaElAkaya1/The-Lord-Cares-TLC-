from django.contrib import admin

from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "status", "user", "guest_identity", "title")
    list_filter = ("status", "created_at")
    search_fields = ("title", "content", "display_name")
    list_select_related = ("user", "guest_identity")
