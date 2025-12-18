from django.contrib import admin

from .models import GuestIdentity, PrayerAssignment, PrayerRequest


@admin.register(GuestIdentity)
class GuestIdentityAdmin(admin.ModelAdmin):
    list_display = ("public_id", "linked_user", "created_at")
    search_fields = ("public_id",)
    list_select_related = ("linked_user",)


@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "user",
        "guest_identity",
        "category_user_selected",
        "category_ml_suggested",
        "status",
    )
    list_filter = ("status", "category_user_selected", "category_ml_suggested", "created_at")
    search_fields = ("request_text",)
    list_select_related = ("user", "guest_identity")


@admin.register(PrayerAssignment)
class PrayerAssignmentAdmin(admin.ModelAdmin):
    list_display = ("prayer_request", "assigned_to", "assigned_at")
    list_select_related = ("prayer_request", "assigned_to")
