import requests
from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from .models import User42

OAUTH_USERINFO_URL = "https://api.intra.42.fr/v2/me"

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope['query_string'].decode())
        token = query_string.get('token')
        
        print (token)
        if token:
            user = await self.get_user_from_token(token[0])
            scope['user'] = user
        else:
            scope['user'] = AnonymousUser()
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            response = requests.get(OAUTH_USERINFO_URL, headers={"Authorization": f"Bearer {token}"})
            if response.status_code == 200:
                user_info = response.json()
                user = User42.objects.get(id42=user_info['id'])
                return user
            else:
                return AnonymousUser()
        except User42.DoesNotExist:
            return AnonymousUser()
