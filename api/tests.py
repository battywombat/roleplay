from django.test import TestCase
from django.contrib.auth.models import User

from .models import Campaign

class CampaignCreationTests(TestCase):

    def setUp(self):
        self.dm = User.objects.create_user('dm')
        self.dm.set_password('dm_password')
        self.dm.save()
        self.user1 = User.objects.create_user('user1')
        self.user1.set_password('user1_password')
        self.user1.save()

    def test_can_login(self):
        logged_in = self.client.login(username=self.dm.username, password='dm_password')
        self.assertTrue(logged_in)

    def test_can_create(self):
        self.client.login(username=self.dm.username, password='dm_password')
        res = self.client.post('/api/campaign/create', {
            'players': [self.user1.id],
        })
        self.assertEqual(res.status_code, 200)
        int(res.content)
