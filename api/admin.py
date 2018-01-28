from django.contrib import admin

from .models import Session, PlayerCharacter, Campaign, Post

admin.site.register((Session, PlayerCharacter, Campaign, Post))
