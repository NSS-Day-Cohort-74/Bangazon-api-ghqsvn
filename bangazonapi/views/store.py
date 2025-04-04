from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from django.contrib.auth.models import User


class StoreSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for Users

    Arguments:
        serializers
    """
    class Meta:
        model = User
        url = serializers.HyperlinkedIdentityField(
            view_name='user',
            lookup_field = 'id'
        )
        fields = ('id', 'url', 'username', 'password', 'first_name', 'last_name', 'email', 'is_active', 'date_joined')


class Stores(ViewSet):
    """Users for Bangazon
    Purpose: Allow a user to communicate with the Bangazon database to GET PUT POST and DELETE Users.
    Methods: GET PUT(id) POST
"""


    def retrieve(self, request, pk=None):
        """Handle GET requests for single customer
        Purpose: Allow a user to communicate with the Bangazon database to retrieve  one user
        Methods:  GET
        Returns:
            Response -- JSON serialized customer instance
        """
        return Response({},status=status.HTTP_200_OK)



    def list(self, request):
        """Handle GET requests to user resource"""
        return Response({},status=status.HTTP_200_OK)
    def create(self, request):
        """Handle GET requests to user resource"""
        return Response({},status=status.HTTP_200_OK)
