from rest_framework import serializers

from security.models import Channel

class ChannelSerializer(serializers.ModelSerializer):
    recipient_user = serializers.ReadOnlyField(source = "recipient_user.id")
    class Meta:
        model = Channel
        fields = ('id','sender_user', 'name', 'recipient_user', 'accepted')

class AcceptChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ('accepted',)
