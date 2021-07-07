""" Webapp views """

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views.generic import DetailView, ListView
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Channel, Image, Message
from .receiver import MESSAGE_CREATED, MESSAGE_DELETED, MESSAGE_EDITED, WebAppReceiver
from .serializers import ChannelSerializer, MessageSerializer

LIVE_RECEIVER = WebAppReceiver()


def send_update(update_type, data):
    event = {"update_type": update_type}
    event.update(data)
    LIVE_RECEIVER.dispatch_event(event=event)


class ChannelListView(ListView):
    """List all channels"""

    model = Channel
    context_object_name = "channels"


channels_list_view = ChannelListView.as_view()


class ChannelDetailView(DetailView):
    """Channel details view"""

    model = Channel
    context_object_name = "channel"
    slug_field = "channel_name"
    slug_url_kwarg = "channel_name"


channel_detail_view = ChannelDetailView.as_view()


class CreateChannelView(APIView):
    def post(self, request):
        """API endpoint: create a new channel"""

        serializer = ChannelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


create_channel_view = CreateChannelView.as_view()


class DeleteChannelView(APIView):
    slug_field = "channel_name"
    slug_url_kwarg = "channel_name"

    def delete(self, request, channel_name):
        """API endpoint: delete a channel by its name"""

        channel = get_object_or_404(Channel, channel_name=channel_name)
        channel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


delete_channel_view = DeleteChannelView.as_view()


class CreateMessageView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "webapp/message.html"

    def post(self, request):
        """API endpoint: create a new message"""
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            send_update(update_type=MESSAGE_CREATED, data=data)
            return Response({"message": data}, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


create_message_view = CreateMessageView.as_view()


class MessageDetailView(APIView):
    """
    Retrieve, update or delete a Message instance.
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "webapp/message.html"

    def put(self, request, pk):
        """API endpoint: update a message by its ID"""

        message = get_object_or_404(Message, pk=pk)
        serializer = MessageSerializer(message, data=request.data)
        if serializer.is_valid():
            serializer.validated_data["modified"] = now()
            serializer.save()
            data = serializer.data
            send_update(update_type=MESSAGE_EDITED, data=data)
            return Response({"message": data})
        return JsonResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """API endpoint: delete a message by its ID"""

        message = get_object_or_404(Message, pk=pk)
        update = {
            "channel": message.channel.channel_name,
            "id": pk,
        }
        message.delete()
        send_update(update_type=MESSAGE_DELETED, data=update)
        return JsonResponse(data={}, status=status.HTTP_204_NO_CONTENT)


message_detail_view = MessageDetailView.as_view()


class DeleteImageView(APIView):
    def delete(self, request, pk):
        """API endpoint: delete an image by its ID"""

        image = get_object_or_404(Image, pk=pk)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


delete_image_view = DeleteImageView.as_view()
