import datetime
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from bangazonapi.models import Store


class StoreSerializer(serializers.ModelSerializer):
    """JSON serializer for stores"""

    class Meta:
        model = Store
        fields = ("id", "name", "description", "customer_id")
        depth = 1


class Stores(ViewSet):
    """ "Request handlers for Stores in Bangazon Platform"""

    permission_classes = IsAuthenticatedOrReadOnly

    def create(self, request):
        pass
