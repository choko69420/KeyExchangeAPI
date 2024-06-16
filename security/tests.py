from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from .models import Channel

class SecretExchangeTests(TestCase):
		def setUp(self):
				# Create a test user
				self.user1 = User.objects.create_user(username='testuser', password='password123')
				self.user2 = User.objects.create_user(username='testuser2', password='password123')
				# Authenticate the test user
				self.client1 = APIClient()
				self.client2 = APIClient()
				self.client1.force_authenticate(user=self.user1)
				self.client2.force_authenticate(user=self.user2)

				# URL for the channel creation endpoint
				self.create_url = reverse('channels-list')

		def test_channel_creation(self):
				# Data for creating a new channel
				data = {
						# Include any other required fields here
						'recipient_user_id': self.user2.id,
				}
				# Make a POST request to create the channel
				response = self.client1.post(self.create_url, data)
				# Check if the channel was created successfully
				self.assertEqual(response.status_code, status.HTTP_201_CREATED)

				# Check if the channel exists in the database
				self.assertTrue(Channel.objects.filter(name=response.data['name']).exists())

		def test_unauthenticated_user(self):
				# Create a new client without authentication
				unauthenticated_client = APIClient()

				# Data for creating a new channel
				data = {
						# Include any other required fields here
						'recipient_user_id': self.user2.id,
				}

				# Make a POST request to create the channel without authentication
				response = unauthenticated_client.post(self.create_url, data)

				# Check if the response status code is 401 Unauthorized
				self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

		def test_channel_acceptance(self):
			# Data for creating a new channel
				data = {
						# Include any other required fields here
						'recipient_user_id': self.user2.id,
				}
				# Make a POST request to create the channel
				response = self.client1.post(self.create_url, data)
				# Check if the channel was created successfully
				self.assertEqual(response.status_code, status.HTTP_201_CREATED)

				# send a request as the recipient to accept the channel
				response = self.client2.post(reverse('channels-accept', args=[response.data['id']]), data={'accepted': True})

				# Check if the channel was accepted successfully
				self.assertEqual(response.status_code, status.HTTP_200_OK)

		def test_set_secret(self):
			# Data for creating a new channel
				data = {
						# Include any other required fields here
						'recipient_user_id': self.user2.id,
				}
				# Make a POST request to create the channel
				response = self.client1.post(self.create_url, data)
				# Check if the channel was created successfully
				self.assertEqual(response.status_code, status.HTTP_201_CREATED)

				# send a request as the recipient to accept the channel
				response2 = self.client2.post(reverse('channels-accept', args=[response.data['id']]), data={'accepted': True})

				# Check if the channel was accepted successfully
				self.assertEqual(response2.status_code, status.HTTP_200_OK)

				# send a request as the sender to set the secret
				response3 = self.client1.post(reverse('setsecret'), data={'channel_id': response.data['id']})
				# Check if the secret was set successfully
				self.assertEqual(response3.status_code, status.HTTP_200_OK)
				print('secret_key' in response3.data)
				self.assertTrue('secret_key' in response3.data)
				self.user1_secret_key = response3.data['secret_key']
				# send a request as the recipient to retrieve the secret_key
				response4 = self.client2.post(reverse('setsecret'), data={'channel_id': response.data['id']})
				# Check if the secret was retrieved successfully
				self.assertEqual(response4.status_code, status.HTTP_200_OK)
				self.assertTrue('secret_key' in response4.data)
				self.user2_secret_key = response4.data['secret_key']

				# check if the secret_key is the same

				response5 = self.client1.post(reverse('generatekey'), data={'channel_id': response.data['id'],'secret_key': self.user1_secret_key})
				response6 = self.client2.post(reverse('generatekey'), data={'channel_id': response.data['id'],'secret_key': self.user2_secret_key})
				self.assertEqual(response5.status_code, status.HTTP_200_OK)
				self.assertEqual(response6.status_code, status.HTTP_200_OK)
				self.assertTrue('key' in response5.data)
				self.assertTrue('key' in response6.data)
				self.assertTrue(response5.data['key'] == response6.data['key'])