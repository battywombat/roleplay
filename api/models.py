from django.db import models
from django.contrib.auth.models import User

class PlayerCharacter(models.Model):
    name = models.CharField(max_length=30)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField('creation date')

class Campaign(models.Model):
    dm = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default='')
    players = models.ManyToManyField(User, related_name='playing_in')
    private = models.BooleanField(default=True)

class Session(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    start_date = models.DateTimeField('date started')
    end_date = models.DateTimeField('date finished')

class Post(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    date = models.DateTimeField('date added')
    poster = models.ForeignKey(PlayerCharacter, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f'{poster.name}: {text}'
