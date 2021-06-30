""" Webapp views """

from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views.generic import DetailView, ListView
from rest_framework import generics, status
from rest_framework.response import Response

from .models import DummyChannel, Message
from .receiver import MESSAGE_CREATED, MESSAGE_DELETED, MESSAGE_EDITED, WebAppReceiver
from .serializers import DummyChannelSerializer, MessageSerializer

LIVE_RECEIVER = WebAppReceiver()


class DummyChannelListView(ListView):
    """List all channels"""

    model = DummyChannel
    context_object_name = "dummy_channels"


class DummyChannelDetailView(DetailView):
    """Channel details view"""

    model = DummyChannel
    context_object_name = "dummy_channel"
    slug_field = "channel_name"
    slug_url_kwarg = "channel_name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["channel"] = self.object.channel_name
        return context


class DummyChannelListAPIView(generics.GenericAPIView):
    def get(self, request):
        """API endpoint: list all channels"""

        channels = DummyChannel.objects.all()
        serializer = DummyChannelSerializer(channels, many=True)
        return Response(serializer.data)

    def post(self, request):
        """API endpoint: create a new channel"""

        serializer = DummyChannelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DummyChannelDetailAPIView(generics.GenericAPIView):
    model = DummyChannel
    slug_field = "channel_name"
    slug_url_kwarg = "channel_name"

    def get(self, request, channel_name):
        """API endpoint: retrieve a channel by its name"""

        channel = get_object_or_404(DummyChannel, channel_name=channel_name)
        serializer = DummyChannelSerializer(channel)
        return Response(serializer.data)

    def delete(self, request, channel_name):
        """API endpoint: delete a channel by its name"""

        channel = get_object_or_404(DummyChannel, channel_name=channel_name)
        channel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MessageListAPIView(generics.GenericAPIView):
    def get(self, request):
        """API endpoint: list all messages"""

        messages = Message.objects.all().order_by("-created")
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request):
        """API endpoint: create a new message"""

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            update = serializer.data
            update["update_type"] = MESSAGE_CREATED
            LIVE_RECEIVER.dispatch_event(event=update)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageDetailAPIView(generics.GenericAPIView):
    """
    Retrieve, update or delete a Message instance.
    """

    def get(self, request, pk):
        """API endpoint: retrieve a message by its ID"""

        message = get_object_or_404(Message, pk=pk)
        serializer = MessageSerializer(message)
        return Response(serializer.data)

    def put(self, request, pk):
        """API endpoint: update a message by its ID"""

        message = get_object_or_404(Message, pk=pk)
        serializer = MessageSerializer(message, data=request.data)
        if serializer.is_valid():
            serializer.validated_data["modified"] = now()
            serializer.save()
            update = serializer.data
            update["update_type"] = MESSAGE_EDITED
            LIVE_RECEIVER.dispatch_event(event=update)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """API endpoint: delete a message by its ID"""

        message = get_object_or_404(Message, pk=pk)
        update = {
            "channel": message.channel.channel_name,
            "id": pk,
            "update_type": MESSAGE_DELETED,
        }
        message.delete()
        LIVE_RECEIVER.dispatch_event(event=update)
        return Response(status=status.HTTP_204_NO_CONTENT)
