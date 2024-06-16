import math
import os
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .permissions import IsRecipient
from .models import Channel
from .serializers import AcceptChannelSerializer, ChannelSerializer
from rest_framework.response import Response
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User
class ChannelViewSet(viewsets.ModelViewSet):

		def get_serializer_class(self):
			if self.action == 'create' or self.action == 'list':
				return ChannelSerializer
			elif self.action =='accept':
				return AcceptChannelSerializer
			return ChannelSerializer

		def get_permissions_for_action(self, action):
				if action == 'create':
						return [IsAuthenticated]
				elif action == 'list':
						return [IsAuthenticated]
				elif action =='retrieve':
						return [IsAuthenticated]
				return []
		
		def get_permissions(self):
				permission_classes = self.get_permissions_for_action(self.action)
				return [permission() for permission in permission_classes]

		def get_queryset(self):
				channels = Channel.objects.filter(Q(sender_user=self.request.user) | Q(recipient_user=self.request.user))
				return channels
		
		def retrieve(self, request, pk=None):
			channel = Channel.objects.get(id=pk)
			serializer = ChannelSerializer(channel)
			return Response(serializer.data)
		
		def create(self, request):
				if 'recipient_user_id' not in request.data:
						return Response(data={'error': 'Recipient user id not provided'}, status=400)
				
				recipient_user = User.objects.get(id=request.data['recipient_user_id'])
				channel = Channel.objects.create(sender_user=request.user,recipient_user=recipient_user)
				data = ChannelSerializer(channel).data
				return Response(data, status=201)

		@action(methods=['post'], detail=True, permission_classes=[IsRecipient])
		def accept(self, request, pk=None):
				channel = Channel.objects.get(id=pk)
				serializer = AcceptChannelSerializer(channel, data=request.data)
				if serializer.is_valid():
					channel.accepted = serializer.validated_data['accepted']
					channel.save()
					return Response(data={'accepted': channel.accepted}, status=200)
				else:
					return Response(data={'error': 'Invalid data'}, status=400)
				
class SecretExchangeView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, format=None):
		if not 'channel_id' in request.data:
			return Response(data={'error': 'Missing channel_id'}, status=400)
		channel = Channel.objects.get(id=request.data['channel_id'])
		if not channel.accepted:
			return Response(data={'error': 'Channel not accepted'}, status=400)
		
		if channel.sender_user == request.user:
			# set the initial_sender_secret
			secret_key = os.urandom(32)
			random_int = int.from_bytes(secret_key, byteorder='big')
			channel.initial_sender_secret = pow(settings.BASE,random_int, settings.MODULUS)
			channel.save()
			return Response(data={'secret_key': random_int}, status=200)
		elif channel.recipient_user == request.user:
			# set the initial_sender_secret
			secret_key = os.urandom(32)
			random_int = int.from_bytes(secret_key, byteorder='big')
			channel.initial_recipient_secret = pow(settings.BASE,random_int,settings.MODULUS)
			channel.save()

			return Response(data={'secret_key': random_int}, status=200)
		else:
			return Response(data={'error': 'User can\'t access channel'}, status=400)

class KeyGenerationView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, format=None):
		if not 'channel_id' in request.data:
			return Response(data={'error': 'Missing channel_id'}, status=400)
		if not'secret_key' in request.data:
			return Response(data={'error': 'Missing secret_key'}, status=400)
		
		channel = Channel.objects.get(id=request.data['channel_id'])

		if not channel.accepted:
			return Response(data={'error': 'Channel not accepted'}, status=400)
		if not channel.initial_recipient_secret:
			return Response(data={'error': 'Initial secret not set'}, status=400)
		if not channel.initial_sender_secret:
			return Response(data={'error': 'Initial secret not set'}, status=400)
		
		if channel.sender_user == request.user:
			key = pow(int(channel.initial_recipient_secret), int(request.data['secret_key']), settings.MODULUS)
			return Response(data={'key': key}, status=200)
		if channel.recipient_user == request.user:
			key = pow(int(channel.initial_sender_secret),  int(request.data['secret_key']), settings.MODULUS)
			return Response(data={'key': key}, status=200)
		else:
			return Response(data={'error': 'User can\'t access channel'}, status=400)

