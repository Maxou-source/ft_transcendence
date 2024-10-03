# your_app/management/commands/clear_friends.py

from django.core.management.base import BaseCommand
from app.models import User42, FriendList, FriendRequest

class Command(BaseCommand):
    help = 'Clear all friend data'

    def handle(self, *args, **kwargs):
        FriendRequest.objects.all().delete()
        FriendList.objects.all().delete()
        
        # Clear userFriends for all User42 instances
        for user in User42.objects.all():
            user.userFriends.clear()

        self.stdout.write(self.style.SUCCESS('Successfully cleared all friend data'))
