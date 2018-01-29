from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, AnonymousUser
from .models import Session, Campaign

def create_campaign(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    if isinstance(request.user, AnonymousUser):
        return HttpResponse(status=403)
    if 'players' in request.POST:
        players = (User.objects.get(id=x) for x in request.POST['players'])
    else:
        players = tuple()
    new_session = Campaign(dm=request.user)
    new_session.save()  # Must have an id before many to many relationships can be saved
    for player in players:
        new_session.players.add(player)
    new_session.save()
    return HttpResponse(bytes(str(new_session.id), 'utf8'))

def campaign(request, campaign_id):
    query = Campaign.objects.filter(id=campaign_id)
    if not query.exists():
        return HttpResponse(status=404)
    campaign, = query.all()
    if request.method == 'GET':
        if campaign.private:
            user = request.user
            if user != campaign.dm and user not in campaign.players.all():
                return HttpResponse(status=403)
        return HttpResponse({
            'name': campaign.name,
            'dm': campaign.dm.username,
            'players': [p.username for p in campaign.players.all()]
        })
    else:
        if request.user != campaign.dm:
            return HttpResponse(status=403)
        command = request.POST['command']
        if command == 'delete':
            campaign.delete()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
