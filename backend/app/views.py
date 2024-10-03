import json
import requests
from . import views

import uuid
import boto3
import os 
import datetime


from .models import User42
from django.db import models
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from .utils import get_user_info, get_user_info_from_session
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render, redirect
# from django.utils.encoding import force_text
from django.contrib.sessions.backends.db import SessionStore
from django.template.loader import render_to_string
from django.forms.models import model_to_dict

from .models import FriendList, FriendRequest
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from urllib.parse import urlparse, parse_qs
from .forms import *
from django.views.decorators.csrf import csrf_exempt

import random
import string

GRANT_TYPE = 'authorization_code'
OAUTH_TOKEN_URL = 'https://api.intra.42.fr/oauth/token'

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
LINK = os.getenv('URI')
time = datetime.datetime.now()

#def get_favicon(request):
    #if request: HttpResponse()
    #if request: FileResponse(open('/app/static/images/favicon.ico', 'rb'), content_type='image/x-icon')

    #if (request)
        #return HttpResponse(, status=200)

def generate_random_name(length=12):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def refresh_access_token(request):
    refresh_token = request.session.get('refresh_token')

    if not refresh_token:
        return HttpResponse('No refresh token available', status=401)

    old_token = request.session['token']


    data = {
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token,
    }

    response = requests.post(OAUTH_TOKEN_URL, data=data)
    if response.status_code == 200:
        token_data = response.json()
        token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        request.session['token'] = token
        request.session['refresh_token'] = refresh_token
        return JsonResponse({'access_token': token})
    else:
        return HttpResponse('Failed to refresh token', status=response.status_code)
    
@csrf_exempt
def send_friend_request(request):
    if request.method == 'POST':
        try:
            receiver_user_id = request.POST.get('receiver_user_id')
        except User42.DoesNotExist:
            response = {
                'response': "receiver id is wrong."
            }
            return JsonResponse(response, status=400)
        try:
            sender_user_id = request.POST.get('sender_user_id')
        except User42.DoesNotExist:
            response = {
                'response': "sender id is wrong."
            }
            return JsonResponse(response, status=400)
        #url = '/send_friend_request/?receiver_user_id=144667&sender_user_id=129011'
        #parsed_url = urlparse(url)
        #query_params = parse_qs(parsed_url.query)

        #receiver_user_id = query_params.get('receiver_user_id', [None])[0]
        #sender_user_id = query_params.get('sender_user_id', [None])[0]
        try:
            receiver = User42.objects.get(id42=receiver_user_id)
            sender = User42.objects.get(id42=sender_user_id)
            
            created = FriendRequest.objects.get_or_create(
                sender=sender,
                receiver=receiver
            )

            if created:
                sender.userFriends.add(receiver)
                receiver.userFriends.add(sender)
                response = {
                    'response': "Friend request sent."
                }
            else:
                response = {
                    'response': "Friend request already exists."
                }

            updated_friend_list = list(sender.userFriends.all().values(
                'id42', 'profil_url', 'login', 'pseudo', 'email', 'wallet', 'pool_year', 'image', 'last_name', 'first_name', 'connected', 
            ))

            response['friends'] = updated_friend_list

            response['receiver'] = [{
                'id42': receiver.id42, 
                'profil_url': receiver.profil_url,
                'login': receiver.login,
                'pseudo': receiver.pseudo,
                'email': receiver.email,
                'wallet': receiver.wallet,
                'pool_year': receiver.pool_year,
                'image': receiver.image,
                'last_name': receiver.last_name,
                'first_name': receiver.first_name,
                'connected': receiver.connected,
            }]
            return JsonResponse(response)
        
        except User42.DoesNotExist:
            response = {
                'response': "User does not exist."
            }
            return JsonResponse(response, status=400)


@csrf_exempt
def block_user(request):
    if request.method == 'POST':
        user_getting_blocked = request.POST.get('user_getting_blocked')
        user_blocking = request.POST.get('user_blocking')

        user_getting_blocked = User42.objects.get(id42=user_getting_blocked)
        user_blocking = User42.objects.get(id42=user_blocking)

        user_blocking.blocked.add(user_getting_blocked)
        response = {
            'blocked': user_getting_blocked.login
        }
        return JsonResponse(response, status=200)
    return JsonResponse({}, status=400)

@csrf_exempt
def remove_friend_request(request):
    if request.method == 'POST':
        receiver_user_id = request.POST.get('receiver_user_id')
        sender_user_id = request.POST.get('sender_user_id')

        try:
            receiver = User42.objects.get(id42=receiver_user_id)
            sender = User42.objects.get(id42=sender_user_id)
            
            sender.userFriends.remove(receiver)
            receiver.userFriends.remove(sender)

            FriendRequest.objects.filter(sender=sender, receiver=receiver).delete()

            response = {
                'response': "Friend removed."
            }

            updated_friend_list = list(sender.userFriends.all().values(
                'id42', 'profil_url', 'login', 'pseudo', 'email', 'wallet', 'pool_year', 'image', 'last_name', 'first_name', 'connected'
            ))

            response['friends'] = updated_friend_list
            
            response['receiver'] = [{
                'id42': receiver.id42, 
                'profil_url': receiver.profil_url,
                'login': receiver.login,
                'pseudo': receiver.pseudo,
                'email': receiver.email,
                'wallet': receiver.wallet,
                'pool_year': receiver.pool_year,
                'image': receiver.image,
                'last_name': receiver.last_name,
                'first_name': receiver.first_name,
                'connected': receiver.connected,
            }]

            return JsonResponse(response)
        
        except User42.DoesNotExist:
            response = {
                'response': "User does not exist."
            }
            return JsonResponse(response, status=400)

def view():
    return HttpResponse()

def get_statistics(request):
    user = User42.objects.get(login=request.session['user']['login'])
    gamePlayed = user.GameHistory.values('userScore')
    if (gamePlayed.count() == 0):
        gamePlayed = {
            'gamesPlayed': False
        }
    else:
        gamePlayed = {
            'user_histories' : list(gamePlayed),
            'response': 'stats found.',
            'gamesPlayed': True,
        }
    return JsonResponse(gamePlayed, status=200)

def get_tournames(request):
    if (request.method == 'GET'):
        tour_names = User42.objects.filter(TourName__isnull=False).values_list('TourName', flat=True)
        tour_names_list = list(tour_names)
        tour_names_dict = {"tour_names": tour_names_list}
        return JsonResponse(tour_names_dict, status=200)

def login(request):
    try:
        check_token_present = request.session['token']
    except:
        check_token_present = False

    if check_token_present:
        app_state = get_user_info(check_token_present)
        if app_state['ok']:
            return redirect('home')
    
    usr = request.user
    client_id = request.META.get('REQUEST_HOST')
    if client_id is not None:
        global CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, LINK
        CLIENT_SECRET = os.getenv('CLIENT_SECRET')
        CLIENT_ID = os.getenv('CLIENT_ID')
        REDIRECT_URI = os.getenv('REDIRECT_URI')
        LINK = os.getenv('URI')
    
    code = request.GET.get('code', '')
    if code:
        data = {
            'grant_type': GRANT_TYPE,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI
        }

        response = requests.post(OAUTH_TOKEN_URL, data=data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            refresh_token = token_data.get('refresh_token')
            new_app_state = get_user_info(token)

            if new_app_state['ok']:
                request.session['token'] = token
                request.session['refresh_token'] = refresh_token
                request.session['user'] = new_app_state['user']
                request.session['location'] = new_app_state['user']['location']
                try:
                    user = User42.objects.get(id42 = new_app_state['user']['id'])
                    new_app_state['user']['image'] = user.image
                except User42.DoesNotExist:
                    user = User42.objects.create(
                        profil_url=new_app_state['user']['url'],
                        login=new_app_state['user']['login'],
                        pseudo=new_app_state['user']['login'],
                        email=new_app_state['user']['email'],
                        wallet=new_app_state['user']['wallet'],
                        pool_year=new_app_state['user']['pool_year'],
                        image=new_app_state['user']['image']['link'],
                        last_name=new_app_state['user']['last_name'],
                        first_name=new_app_state['user']['first_name'],
                        id42=new_app_state['user']['id'],
                        connected=True
                    )

                    new_app_state['user']['image'] = user.image

                user.connected = True
                user.save()
            return redirect('home')
        else:
            return HttpResponse(
                'Error exchanging code',
                status=response.status_code
            )

    return render(request, 'login.html', {'code': code, 'LINK': os.getenv('URI')})

def getContext(request):
    try:
        check_token_present = request.session['token']
    except KeyError:
        check_token_present = False

    #current session user
    try:
        user = User42.objects.get(login=request.session['user']['login'])
    except KeyError:
        return print ('user not found')
    #current user friends
    friendList = user.userFriends.all()
    users = User42.objects.all().exclude(id42__in=friendList.values_list('id42', flat=True))
    chatrooms = ChatGroup.objects.filter(authors=user)
    form = ChatmessageCreateForm()
    
    context = {
        'users_are_connected': users.exists(),
        'users': users,
        'pseudo': user.pseudo,
        'newimage': user.image,
        'current_user': {'login': user.login, 'pseudo': user.pseudo, 'id42': user.id42},
        'friends': friendList.exists(),
        'FriendList': friendList,
        'token': request.session['token'],
        'chatrooms': chatrooms,
        'form': form,
    }
    context.update(get_user_info_from_session(request.session))
    context['last_name'] = user.last_name
    context['first_name'] = user.first_name
    return context

def game(request):
    try:
        check_token_present = request.session['token']
    except KeyError:
        check_token_present = False
    if (check_token_present):
        return render(request, 'home.html', getContext(request))

    return redirect('/')

def statistics(request):
    try:
        check_token_present = request.session['token']
    except KeyError:
        check_token_present = False
    if (check_token_present):
        user = User42.objects.get(login=request.session['user']['login'])
        context = getContext(request)
        if (user.GameHistory.all().count() == 0):
            gamePlayed = {
                'gamesPlayed': False,
            }
        else:
            sumPoint = 0
            for point in user.GameHistory.all():
                sumPoint += point.userScore
            gamePlayed = {
                'user_histories' : user.GameHistory.all().order_by('-date')[:5],
                'point_scored': sumPoint,
                'average': sumPoint / user.GameHistory.all().count(),
                'gamesPlayed': True,
                        }
        context.update(gamePlayed)
        return render(request, 'home.html', context)
    return redirect('/')

def params(request):
    try:
        check_token_present = request.session['token']
    except KeyError:
        check_token_present = False
    if (check_token_present):
        context = getContext(request)
        context.update(get_user_info_from_session(request.session))
        return render(request, 'home.html', context)
    return redirect('/')

def friends(request):
    try:
        check_token_present = request.session['token']
    except KeyError:
        check_token_present = False
    if (check_token_present):
        return render(request, 'home.html', getContext(request))
    return redirect('/')

def home1(request):
    try:
        check_token_present = request.session['token']
    except:
        check_token_present = False

    if (check_token_present):
        context = {'token': request.session['token']}
        context.update(get_user_info_from_session(request.session))
        user = User42.objects.get(login=request.session['user']['login'])
        context.update({'newimage': user.image})
        context['last_name'] = user.last_name
        context['first_name'] = user.first_name
        return render(
            request,
            'home.html',
            context
        )
    return redirect('/')

def profile(request, user):
    try:
        check_token_present = request.session['token']
    except KeyError:
        check_token_present = False
    context_user = User42.objects.get(login=user)
    current_user = get_user_info_from_session(request.session)
    friendList = context_user.userFriends.all()
    areWeFriends = next((friend for friend in friendList if friend.login == current_user['login']), None)
    gamePlayed = context_user.GameHistory.filter(opponent=current_user['login']).order_by('-date')[:5]
    gamePlayed = {
        'user_histories' : gamePlayed,
        'gamesPlayed': True if gamePlayed.count() != 0 else False
    }
    dict_context = {
        'profile': {
            'image': context_user.image,
            'login': context_user.login,
            'pseudo': context_user.pseudo,
            'first_name': context_user.first_name,
            'last_name': context_user.last_name,
            'connected': context_user.connected,
            'pool_year': context_user.pool_year,
            'wallet': context_user.wallet,
            'areWeFriends': True if areWeFriends else False
            },
        'current_user': current_user
    }
    dict_context.update(gamePlayed)
    return render(request, 'profile.html', dict_context)

def home(request, page):
    try:
        check_token_present = request.session['token']
    except KeyError:
        check_token_present = False

    #current session user
    user = User42.objects.get(login=request.session['user']['login'])
    #current user friends
    friendList = user.userFriends.all()
    users = User42.objects.all().exclude(id42__in=friendList.values_list('id42', flat=True))
    chatrooms = ChatGroup.objects.filter(authors=user)
    form = ChatmessageCreateForm()
    
    context = {
        'users_are_connected': users.exists(),
        'users': users,
        'pseudo': user.pseudo,
        'newimage': user.image,
        'current_user': {'login': user.login,'pseudo': user.pseudo, 'id42': user.id42},
        'friends': friendList.exists(),
        'FriendList': friendList,
        'token': request.session['token'],
        'chatrooms': chatrooms,
        'form': form,
    }
    context.update(get_user_info_from_session(request.session))
    context['last_name'] = user.last_name
    context['first_name'] = user.first_name
    if check_token_present:
        if page == "leaderboard":
            template_string = render_to_string('toInject/leaderboard.html', context)
        elif page == "game":
            template_string = render_to_string('toInject/game.html', context)
        elif page == "params":
            template_string = render_to_string('toInject/params.html', context)
        elif page == "statistics":
            if (user.GameHistory.all().count() == 0):
                gamePlayed = {
                    'gamesPlayed': False,
                }
            else:
                sumPoint = 0
                for point in user.GameHistory.all():
                    sumPoint += point.userScore
                gamePlayed = {
                    'user_histories' : user.GameHistory.all().order_by('-date')[:5],
                    'point_scored': sumPoint,
                    'average': sumPoint / user.GameHistory.all().count(),
                    'gamesPlayed': True,
                }
                context.update(gamePlayed)
            template_string = render_to_string('toInject/statistics.html', context)
        elif page == "friends":
            template_string = render_to_string('toInject/friends.html', context)
        elif page == "chatbox":
            form = ChatmessageCreateForm()
            formContext = {
                'form': form
            }
            context.update(formContext)
            template_string = render_to_string('toInject/chatbox.html', context)
        else:
            return render(request, 'home.html', context)
        return HttpResponse(template_string)
    return redirect('/')


def logout(request):
    try:
        if 'user' in request.session and 'id' in request.session['user']:
            user = User42.objects.get(id42=request.session['user']['id'])
            user.connected = False
            user.save()
        else:
            raise KeyError('user')
    except KeyError:
        request.session.flush()
        return redirect('/')
    
    request.session.flush()
    return redirect('/')


@csrf_exempt
def update_profile(request):
    if request.method == 'POST':
        psd = request.POST.get('pseudo')
        ln = request.POST.get('last_name')
        fn = request.POST.get('first_name')

        user = User42.objects.get(id42 = request.session['user']['id'])
        if user:
            user.pseudo = psd
            user.last_name = ln
            user.first_name = fn
            user.save()
            return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
def upload_avatar(request):
    if request.method == 'POST' and request.FILES['avatar']:
        avatar = request.FILES['avatar']
        mime = avatar.content_type
        extension = mime.split('/').pop()
        key = f"{request.session['user']['id']}/{uuid.uuid4()}.{extension}"

        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

        response = s3_client.list_objects_v2(
            Bucket=settings.AWS_AVATAR_BUCKET,
            Prefix=f"{request.session['user']['id']}/"
        )

        if 'Contents' in response:
            keys = [{
                    'Key': obj['Key']
                }
                for obj in response['Contents']
            ]

            s3_client.delete_objects(
                Bucket=settings.AWS_AVATAR_BUCKET,
                Delete={
                    'Objects': keys
                }
            )

        s3_client.upload_fileobj(
            avatar,
            settings.AWS_AVATAR_BUCKET,
            key,
            ExtraArgs={
                'ACL':'public-read'
            }
        )
   
        url = f"https://{settings.AWS_AVATAR_BUCKET}.s3.amazonaws.com/{key}"
        user = User42.objects.get(id42 = request.session['user']['id'])
        if user:
            user.image = url
            user.save()

            # sessions = Session.objects.all()
            # for session in sessions:
            #     data = session.get_decoded()
            #     data['user']['image'] = url
            #     session.session_data = SessionStore().encode(data)
            #     session.save()

            return JsonResponse({
                    'ok': True,
                    'url': url
                },
                status=201
            )

    return JsonResponse({
            'ok': False
        },
        status=400
    )