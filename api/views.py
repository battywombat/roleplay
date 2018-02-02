import json

from django.http import HttpResponse
from django.contrib.auth.models import User, AnonymousUser
from .models import Campaign

def create_campaign(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    if isinstance(request.user, AnonymousUser):
        return HttpResponse(status=403)
    if 'players' in request.POST:
        players = (User.objects.get(id=x) for x in request.POST['players'])
    else:
        players = tuple()
    if 'name' in request.POST:
        name = request.POST['name']
    else:
        name = ''
    new_campaign = Campaign(dm=request.user, name=name)
    new_campaign.save()  # Must have an id before many to many relationships can be saved
    for player in players:
        new_campaign.players.add(player)
    new_campaign.save()
    return HttpResponse(bytes(str(new_campaign.id), 'utf8'), status=201)

def _get_user(user_id):
    query = User.objects.filter(id=user_id)
    if len(query.all()) == 0:
        return None
    return query.all()[0]

def _campaign_patch(campaign, data):
    if 'dm' in data:
        new_dm = _get_user(data['dm'])
        if new_dm is None:
            return HttpResponse(status=400)
        campaign.dm = new_dm
    if 'remove_player' in data:
        player = _get_user(data['remove_player'])
        if player is None or player not in campaign.players.all():
            return HttpResponse(status=400)
        campaign.players.remove(player)
    if 'add_player' in data:
        player = _get_user(data['add_player'])
        if player is None:
            return HttpResponse(status=400)
        campaign.players.add(player)
    if 'private' in data:
        if not isinstance(data['private'], bool):
            return HttpResponse(status=400)
        campaign.private = data['private']
    if 'name' in data:
        if not isinstance(data['private'], str):
            return HttpResponse(status=400)
        campaign.private = data['name']
    campaign.save()
    return HttpResponse(status=204)

def _campaign_get(user, campaign):
    if campaign.private and user != campaign.dm and user not in campaign.players.all():
        return HttpResponse(status=403)
    return HttpResponse(json.dumps({
        'name': campaign.name,
        'dm': campaign.dm.username,
        'players': [p.username for p in campaign.players.all()]
    }), status=200)

def campaign(request, campaign_id):
    query = Campaign.objects.filter(id=campaign_id)
    if not query.exists():
        return HttpResponse(status=404)
    campaign, = query.all()
    if request.method == 'GET':
        return _campaign_get(request.user, campaign)
    elif request.method == 'DELETE':
        if request.user != campaign.dm:
            return HttpResponse(status=403)
        campaign.delete()
        return HttpResponse(status=204)
    elif request.method == 'PATCH':
        if request.user != campaign.dm:
            return HttpResponse(status=403)
        data = json.loads(request.body, encoding='utf8')
        return _campaign_patch(campaign, data)
    return HttpResponse(status=405)
