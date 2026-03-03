from django.conf import settings
from django.db import models
from django.db.models import Max

class SavedVessel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mmsi = models.BigIntegerField()
    name = models.CharField(max_length=200, blank=True)
    imo = models.CharField(max_length=20, blank=True)
    raw = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "mmsi")

    def __str__(self):
        return f"{self.mmsi} - {self.name}"
    
    def ingest_location_if_newer(self, *, lat, lng, ts, sog=None, cog=None, raw=None):
        latest_ts = self.locations.aggregate(m=Max("ts"))["m"]

        if latest_ts is None or ts > latest_ts:
            VesselLocation.objects.get_or_create(
                vessel=self,
                ts=ts,
                defaults={
                    "lat": lat,
                    "lng": lng,
                    "sog": sog,
                    "cog": cog,
                    "raw": raw or {},
                },
            )

    @property
    def latest_position(self):
        return self.locations.first()


class VesselLocation(models.Model):
    vessel = models.ForeignKey(SavedVessel, on_delete=models.CASCADE, related_name="locations")

    lat = models.FloatField()
    lng = models.FloatField()

    sog = models.FloatField(null=True, blank=True)
    cog = models.FloatField(null=True, blank=True)

    ts = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    raw = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-ts"]
        constraints = [
            models.UniqueConstraint(fields=["vessel", "ts"], name="uniq_location_per_ts"),
        ]

    def __str__(self):
        return f"{self.vessel.mmsi} @ {self.lat}, {self.lng}"