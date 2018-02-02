import json

from django.test import TestCase
from django.contrib.auth.models import User

from .models import Campaign

class CampaignTests(TestCase):

    def setUp(self):
        self.dm = User.objects.create_user('dm')
        self.dm.set_password('dm_password')
        self.dm.save()
        self.user1 = User.objects.create_user('user1')
        self.user1.set_password('user1_password')
        self.user1.save()
        self.user2 = User.objects.create_user('user2')
        self.user2.set_password('user2_password')
        self.user2.save()
        self.campaign_private = Campaign.objects.create(name='Test Campaign', dm=self.dm, private=True)
        self.campaign_private.save()
        self.campaign_private.players.add(self.user1)
        self.campaign_private.save()
        self.campaign_public = Campaign.objects.create(name='Test Campaign 2', dm=self.dm, private=False)
        self.campaign_public.save()
        self.campaign_public.players.add(self.user1)
        self.campaign_public.save()

    def test_can_login(self):
        logged_in = self.client.login(username=self.dm.username, password='dm_password')
        self.assertTrue(logged_in)

    def test_can_create(self):
        self.client.login(username=self.dm.username, password='dm_password')
        res = self.client.post('/api/campaign/create', {
            'players': [self.user1.id],
        })
        self.assertEqual(res.status_code, 201)
        int(res.content)

    def test_create_without_users(self):
        self.client.login(username=self.dm.username, password='dm_password')
        res = self.client.post('/api/campaign/create', {})
        self.assertEqual(res.status_code, 201)
        int(res.content)    
    
    def test_cannot_create_when_not_logged_in(self):
        res = self.client.post('/api/campaign/create', {
            'players': [],
        })
        self.assertEqual(res.status_code, 403)
    
    def test_cannot_get_private_while_not_logged_in(self):
        res = self.client.get(f'/api/campaign/{self.campaign_private.id}')
        self.assertEqual(res.status_code, 403)
    
    def test_cannot_get_private_while_logged_in(self):
        self.client.login(username=self.user2.username, password='user2_password')
        res = self.client.get(f'/api/campaign/{self.campaign_private.id}')
        self.assertEqual(res.status_code, 403)
    
    def test_can_get_private_when_logged_in(self):
        self.client.login(username=self.user1.username, password='user1_password')
        res = self.client.get(f'/api/campaign/{self.campaign_private.id}')
        self.assertEqual(res.status_code, 200)
    
    def test_can_get_public_while_not_logged_in(self):
        res = self.client.get(f'/api/campaign/{self.campaign_public.id}')
        self.assertEqual(res.status_code, 200)

    def test_can_get_public_while_logged_in(self):
        self.client.login(username=self.user2.username, password='user2_password')
        res = self.client.get(f'/api/campaign/{self.campaign_public.id}')
        self.assertEqual(res.status_code, 200)
    
    def test_can_delete(self):
        self.client.login(username=self.dm.username, password='dm_password')
        res = self.client.post('/api/campaign/create', {
            'players': [self.user1.id],
        })
        self.assertEqual(res.status_code, 201)
        newid = int(res.content)
        res2 = self.client.delete(f'/api/campaign/{newid}')
        self.assertEqual(res2.status_code, 204)
        res3 = self.client.get(f'/api/campaign/{newid}')
        self.assertEqual(res3.status_code, 404)

    def test_unauth_cant_delete(self):
        self.client.login(username=self.user1.username, password='user1_password')
        res2 = self.client.delete(f'/api/campaign/{self.campaign_public.id}')
        self.assertEqual(res2.status_code, 403)
    
    def test_patch_dm(self):
        self.client.login(username=self.dm.username, password='dm_password')
        res = self.client.post('/api/campaign/create', {
            'players': [self.user1.id],
        })
        self.assertEqual(res.status_code, 201)
        newid = int(res.content)
        res2 = self.client.patch(f'/api/campaign/{newid}', json.dumps({
            'dm': self.user1.id
        }))
        self.assertEqual(res2.status_code, 204)
        self.client.logout()
        self.client.login(username=self.user1.username, password='user1_password')
        res3 = self.client.get(f'/api/campaign/{newid}')
        content = json.loads(res3.content)
        self.assertEqual(self.user1.username, content['dm'])
