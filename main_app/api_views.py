
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

class NearbyVesselsSearchAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return Response({"ok": True, "message": "nearby search placeholder"}, status=200)

class SaveVesselsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return Response({"ok": True, "message": "save vessels placeholder"}, status=201)

class MyVesselsListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response([], status=200)

class RefreshMyVesselsLocationsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return Response({"ok": True, "message": "refresh placeholder"}, status=200)