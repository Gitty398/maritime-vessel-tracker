from rest_framework import serializers


class MarinesiaVesselInputSerializer(serializers.Serializer):
    mmsi = serializers.IntegerField(min_value=1)

    name = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=200)
    imo = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)

    lat = serializers.FloatField(required=False, allow_null=True)
    lng = serializers.FloatField(required=False, allow_null=True)
    sog = serializers.FloatField(required=False, allow_null=True)
    cog = serializers.FloatField(required=False, allow_null=True)
    status = serializers.IntegerField(required=False, allow_null=True)
    dest = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    eta = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    draught = serializers.FloatField(required=False, allow_null=True)
    ts = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, attrs):
        lat = attrs.get("lat")
        lng = attrs.get("lng")
        if (lat is None) ^ (lng is None):
            raise serializers.ValidationError("If lat is provided, lng must also be provided (and vice versa).")
        return attrs


class SaveVesselsRequestSerializer(serializers.Serializer):
    vessels = MarinesiaVesselInputSerializer(many=True)

    def validate_vessels(self, vessels):
        if not vessels:
            raise serializers.ValidationError("Provide at least one vessel.")
        return vessels