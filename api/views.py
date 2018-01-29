from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Session, Campaign

def create_campaign(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    if request.user is None:
        return HttpResponse(status=403)
    players = [User.objects.get(id=x) for x in request.POST['players']]
    new_session = Campaign(dm=request.user)
    new_session.save()  # Must have an id before many to many relationships can be saved
    for player in players:
        new_session.players.add(player)
    new_session.save()
    return HttpResponse(bytes(str(new_session.id), 'utf8'))

def get_campaign(request, campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)
    if campaign is None:
        return HttpResponse(status=404)
    if campaign.private:
        user = request.user
        if user != campaign.dm and user not in campaign.players.all():
            return HttpResponse(status=403)
    return HttpResponse({
        'name': campaign.name,
        'dm': campaign.dm.username,
        'players': [p.username for p in campaign.players.all()]
    })
