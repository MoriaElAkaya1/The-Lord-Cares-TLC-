from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class PrayerCategory(models.TextChoices):
    FAMILY = "family", "Family"
    FAITH = "faith", "Faith"
    HEALTH = "health", "Health"
    SPOUSE = "spouse", "Spouse"
    CHILDREN = "children", "Children"
    PARENTING = "parenting", "Parenting"
    FINANCES = "finances", "Finances"
    GUIDANCE = "guidance", "Guidance"
    OTHER = "other", "Other"


class GuestIdentity(models.Model):
    """
    Represents an anonymous visitor. The browser keeps a cookie with this UUID so
    repeat visits map to the same GuestIdentity.
    """

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    linked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_guest_identities",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Guest {self.public_id}"


class PrayerRequestStatus(models.TextChoices):
    NEW = "new", "New"
    PRAYING = "praying", "Praying"
    PRAYED = "prayed", "Prayed"
    CLOSED = "closed", "Closed"


class PrayerRequest(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prayer_requests",
    )

    guest_identity = models.ForeignKey(
        GuestIdentity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prayer_requests",
    )

    request_text = models.TextField()

    category_user_selected = models.CharField(
        max_length=32,
        choices=PrayerCategory.choices,
        default=PrayerCategory.OTHER,
    )

    # ML-suggested category (later). Keep nullable until ML exists.
    category_ml_suggested = models.CharField(
        max_length=32,
        choices=PrayerCategory.choices,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=16,
        choices=PrayerRequestStatus.choices,
        default=PrayerRequestStatus.NEW,
    )

    @property
    def is_guest(self) -> bool:
        return self.user_id is None and self.guest_identity_id is not None

    def clean(self) -> None:
        """
        Basic integrity rule:
        A request must belong to exactly one identity: user OR guest_identity.
        """
        from django.core.exceptions import ValidationError

        if self.user_id and self.guest_identity_id:
            raise ValidationError("PrayerRequest cannot have both user and guest_identity.")
        if not self.user_id and not self.guest_identity_id:
            raise ValidationError("PrayerRequest must have either user or guest_identity.")

    def __str__(self) -> str:
        owner = self.user_id or self.guest_identity_id
        return f"PrayerRequest({owner}) @ {self.created_at:%Y-%m-%d}"


class PrayerAssignment(models.Model):
    """
    Which admin/prayer-team member is assigned to pray for this request.
    """

    prayer_request = models.ForeignKey(
        PrayerRequest, on_delete=models.CASCADE, related_name="assignments"
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prayer_assignments",
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    note = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return f"{self.prayer_request_id} -> {self.assigned_to_id}"
