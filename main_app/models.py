from django.conf import settings
from django.db import models


class SavedVessel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_vessels",
    )
    mmsi = models.BigIntegerField()
    name = models.CharField(max_length=200, blank=True)
    imo = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "mmsi")

    def __str__(self) -> str:
        return f"{self.mmsi} ({self.user})"

    @property
    def latest_position(self):
        return self.positions.order_by("-ts", "-id").first()


class VesselPosition(models.Model):
    vessel = models.ForeignKey(
        SavedVessel,
        on_delete=models.CASCADE,
        related_name="positions",
    )

    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    sog = models.FloatField(null=True, blank=True)
    cog = models.FloatField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)

    dest = models.CharField(max_length=255, blank=True, null=True)
    eta = models.CharField(max_length=50, blank=True, null=True)
    draught = models.FloatField(null=True, blank=True)

    ts = models.DateTimeField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    raw = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["vessel", "-ts"]),
        ]

    def __str__(self) -> str:
        return f"Pos {self.vessel.mmsi} @ {self.ts or self.created_at}"