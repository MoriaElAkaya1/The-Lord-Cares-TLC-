from __future__ import annotations

from django.conf import settings
from django.db import models
from prayers.models import GuestIdentity


class TestimonialStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class Testimonial(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="testimonials",
    )

    guest_identity = models.ForeignKey(
        GuestIdentity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="testimonials",
    )

    display_name = models.CharField(
        max_length=80,
        blank=True,
        default="",
        help_text="Optional. If empty, we show Anonymous (or the user's name if signed in).",
    )

    title = models.CharField(max_length=120, blank=True, default="")
    content = models.TextField()

    status = models.CharField(
        max_length=16,
        choices=TestimonialStatus.choices,
        default=TestimonialStatus.PENDING,
    )

    def clean(self) -> None:
        from django.core.exceptions import ValidationError

        if self.user_id and self.guest_identity_id:
            raise ValidationError("Testimonial cannot have both user and guest_identity.")
        if not self.user_id and not self.guest_identity_id:
            raise ValidationError("Testimonial must have either user or guest_identity.")

    def public_author_name(self) -> str:
        if self.display_name.strip():
            return self.display_name.strip()
        if self.user_id:
            return getattr(self.user, "get_full_name", lambda: "")() or getattr(
                self.user, "username", "User"
            )
        return "Anonymous"

    def __str__(self) -> str:
        return f"Testimonial({self.status}) {self.created_at:%Y-%m-%d}"
