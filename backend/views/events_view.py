# views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import Event
from ..serializers import EventSerializer

class EventListView(generics.ListCreateAPIView):
    """
    API view for listing and creating events.
    Requires authentication for access.
    Endpoint: GET /api/events/ (List all events)
              POST /api/events/ (Create a new event)
    """

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        Get a list of all events.
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Create a new event.
        """
        return super().create(request, *args, **kwargs)

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting an event.
    Requires authentication for access.
    Endpoint: GET /api/events/<int:pk>/ (Retrieve an event)
              PUT /api/events/<int:pk>/ (Update an event)
              DELETE /api/events/<int:pk>/ (Delete an event)
    """

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve an event.
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Update an event.
        """
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete an event.
        """
        return super().destroy(request, *args, **kwargs)
