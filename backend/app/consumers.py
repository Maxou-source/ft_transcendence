import json, string, random, time, redis, threading, sys, asyncio
from django.db import transaction, IntegrityError
from .models import GameRoom, User42, ChatGroup, GroupMessage, TournamentRoom, UserHistory
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.db.models import Q
from urllib.parse import parse_qs

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
ROOM_NUM_LOCK = threading.Lock()
ROOM_NUM = 0
TOUR_NUM_LOCK = threading.Lock()
TOUR_NUM = 0
TOUR_PLYR_LOCK = threading.Lock()
TOUR_PLYR_NUM = 0
room_lock = asyncio.Lock()

def err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

@database_sync_to_async
def is_room_full(room):
    return room.player1 is not None and room.player2 is not None

def intersectP1(ball, p1):
    return (ball['xpos'] - ball['radius'] <= p1['xpos'] + p1['padWidth'] and
            ball['ypos'] >= p1['ypos'] and 
            ball['ypos'] <= p1['ypos'] + p1['padHeight'])


def intersectP2(ball, p2):
    return (ball['xpos'] + ball['radius'] >= p2['xpos'] and
            ball['ypos'] >= p2['ypos'] and 
            ball['ypos'] <= p2['ypos'] + p2['padHeight'])


def reset(ball, canvas):
    ball['ypos'] = canvas['height'] / 2
    ball['dx'] = 1 * ball['speed']
    ball['dy'] = 1 * ball['speed']

async def ball_update(self, json, mode):
    ball = json['ball']
    p1 = json['p1']
    p2 = json['p2']
    canvas = json['canvas']
    p1Scored = False
    p2Scored = False
    if ball['xpos'] + ball['radius'] > canvas['width']:
        reset(ball, canvas)
        p1Scored = True
    if ball['xpos'] - ball['radius'] < 0:
        reset(ball, canvas)
        p2Scored = True
    if (ball['ypos'] - ball['radius'] < 0) or (ball['ypos'] + ball['radius'] > ball['canvas_height']):
        ball['dy'] = -ball['dy']
    if intersectP1(ball, p1):
        ball['dx'] *= 1.1
        ball['dx'] = abs(ball['dx'])
    elif intersectP2(ball, p2):
        ball['dx'] *= 1.1
        ball['dx'] = -abs(ball['dx'])
    ball['ypos'] += ball['dy']
    ball['xpos'] += ball['dx']
    if mode == 'Tournament':
        await TournamentConsumer.send_game_update(self, ball, p1Scored, p2Scored, p1, p2)
    else:
        await GameConsumer.send_game_update(self, ball, p1Scored, p2Scored, p1, p2)

async def update_winner(self, msg):
    userH = UserHistory.objects.create()
    userH.userScore =  msg['userScore']
    userH.otherScore =  msg['otherScore']
    userH.opponent = msg['opponent']
    userH.date = msg['date']
    userH.mode = msg['mode']

    try:
        room = GameRoom.objects.get(name=self.room_group_name)
    except GameRoom.DoesNotExist as str: return err(str)

    self.user.GameHistory.add(userH)
    userH.save()

    if msg['mode'] == 'Tournament':
        try:
            old_playerCount = TournamentRoom.objects.get(name=self.tour_group_name)
        except TournamentRoom.DoesNotExist as str: return err(str), await self.disconnect('failToFetch')

        if msg['otherScore'] > msg['userScore']:
            self.game_running = False
            return await self.disconnect("update_winner")

        start_time = time.time()
        timeout = 3

        try:
                tour = TournamentRoom.objects.get(name=self.tour_group_name)
        except: err('timeout')

        while not tour.disconnect:
            await asyncio.sleep(0.5)
            tour.refresh_from_db()
            if time.time() - start_time > timeout: break

        await self.GameEnd()
    elif msg['mode'] == 'Online Game':
        return await self.disconnect("update_winner")

class TournamentConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = 'None'
        self.tour_group_name = 'None'
        self.game_running = False
    
    async def connect(self):
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            return await self.close()
        
        await self.assign_room()

        is_host = False
        tourRoom = TournamentRoom.objects.get(name=self.tour_group_name)
        if tourRoom.game.player1 == self.scope["user"]:
            is_host = True

        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'host_status',
            'message': 'host_status',
            'isHost': is_host,
        }))

    def isReady(self):
        try:
            tour = TournamentRoom.objects.get(name=self.tour_group_name)
        except TournamentRoom.DoesNotExist as str: return err(str), False

        try:
            player = tour.players.get(login=self.user)
        except User42.DoesNotExist as str: return err(str), False

        if self.game_running: return False

        if tour.game.player1 == player or tour.game.player2 == player:
            return True       

    async def assign_room(self):
        global ROOM_NUM, TOUR_NUM
        tourRoom = TournamentRoom.objects.filter(player_count__lt=10).first()
        
        if tourRoom:
            self.tour_group_name = tourRoom.name
            tourRoom.players.add(self.user)
            tourRoom.player_count += 1
            
            if not tourRoom.game.player1 and tourRoom.game.player2 != self.user:
                tourRoom.game.player1 = self.user
                self.room_group_name = tourRoom.game.name
                await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            
            elif not tourRoom.game.player2 and tourRoom.game.player1 != self.user:
                tourRoom.game.player2 = self.user
                self.room_group_name = tourRoom.game.name
                await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            
            tourRoom.game.save()
            tourRoom.save()
            await self.channel_layer.group_add(self.tour_group_name, self.channel_name)
        elif not tourRoom:
            with ROOM_NUM_LOCK and TOUR_NUM_LOCK:
                while True:
                    try:
                        with transaction.atomic():
                            room = GameRoom.objects.create(player1=self.user, name=f'TournamentGameRoom{ROOM_NUM}')
                            self.room_group_name = room.name
                            room.player1 = self.user
                            room.save()
                            
                            tourRoom = TournamentRoom.objects.create(game=room, name=f'TournamentRoom{TOUR_NUM}')
                            self.tour_group_name = tourRoom.name
                            tourRoom.players.add(self.user)
                            tourRoom.player_count += 1
                            tourRoom.game = room
                            tourRoom.save()

                            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
                            await self.channel_layer.group_add(self.tour_group_name, self.channel_name)
                            break
                    except IntegrityError:
                        ROOM_NUM += 1
                        TOUR_NUM += 1
                ROOM_NUM += 1
                TOUR_NUM += 1
    
    async def remove_user_from_room(self):
        global ROOM_NUM
        if self.room_group_name:
            try:
                room = GameRoom.objects.get(name=self.room_group_name)
                if room.player1_id == self.user.id:
                    room.player1 = None
                elif room.player2_id == self.user.id:
                    room.player2 = None
                room.save()
                
                if not room.player1_id and not room.player2_id :
                    room.delete()
                    ROOM_NUM -= 1
                await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            except GameRoom.DoesNotExist:
                pass
            except GameRoom.player1.RelatedObjectDoesNotExist:
                room.delete()

    async def remove_user_from_tour(self):
        global TOUR_NUM
        self.user.TourId = 0
        if self.tour_group_name:
            try:
                tourRoom = TournamentRoom.objects.get(name=self.tour_group_name)
            except TournamentRoom.DoesNotExist as str: return err(str)
            if tourRoom.players.filter(id=self.user.id).exists():
                tourRoom.players.remove(self.user)
                tourRoom.player_count -= 1
                tourRoom.save()
            if not tourRoom.players.exists():
                tourRoom.delete()
                TOUR_NUM -= 1
        await self.channel_layer.group_discard(self.tour_group_name, self.channel_name)

    async def disconnect(self, close_code):
        try:
            tourRoom = TournamentRoom.objects.get(name=self.tour_group_name)
        except TournamentRoom.DoesNotExist as str: return err(str)
        if self.tour_group_name:
            if self.game_running:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {'type': 'stop_game',
                        'players': list(tourRoom.players.exclude(id=self.user.id).values('TourName', 'connected', 'image')),
                        'message': close_code,
                        'user': self.user.login
                    }
                )
            try:
                player = tourRoom.players.get(id=self.user.id).TourName
            except User42.DoesNotExist as str: return err(str)

            await self.channel_layer.group_send(
                self.tour_group_name,
                {
                    'message': f'removing player {self.user}',
                    'type': 'removing_player',
                    'player': player
                }
            )
            
            if (tourRoom.player_count - 1) > 2:
                # (f'{self.user} update_room from disconnect')
                await self.channel_layer.group_send(
                    self.tour_group_name,
                    {
                        'type': 'update_room',
                        'user': self.user.login
                    }
                )

            await self.remove_user_from_room()
            await self.remove_user_from_tour()

            if close_code == 'update_winner':
                try:
                    tour = TournamentRoom.objects.get(name=self.tour_group_name)
                except TournamentRoom.DoesNotExist as str: return err(str)
                tour.disconnect = True
                tour.save()

    
    async def host_status(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'isHost': event['isHost'],
        }))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        try:
            tour = TournamentRoom.objects.get(name=self.tour_group_name)
        except TournamentRoom.DoesNotExist as str: return (str)
       
        if message_type == 'ball_update':
            await ball_update(self, text_data_json, 'Tournament')
        elif message_type == 'pad_update':
            paddle = text_data_json['pad']
            paddle['type'] = 'pad_update'
            paddle['message'] = 'pad_update'
            isHost = text_data_json['isHost']
            if isHost:
                paddle["player"] = "p1"
            else:
                paddle["player"] = "p2"
            await self.channel_layer.group_send(
                self.room_group_name, paddle)
        elif message_type == 'adding_player':
            player = tour.players.get(id=self.user.id)
            player.TourName = text_data_json['playername']
            player.save()

            await self.channel_layer.group_send(
                self.tour_group_name,
                {
                    'message': f'adding player {player}',
                    'type': 'adding_player',
                    'player': [player.TourName, player.connected, player.image],
                    'players': list(tour.players.values('TourName', 'connected', 'image')),
                    'user': self.user.id,
                    'ready': self.isReady()
                }
            )

            await self.joining_tournament({'players': list(tour.players.values('TourName', 'connected', 'image'))})
        elif message_type == 'removing_player':
            await self.channel_layer.group_send(
                self.tour_group_name,
                {
                    'type': 'removing_player',
                    'player': text_data_json['player'] 
                }
            )
        elif message_type == 'update_winner':
            await update_winner(self, text_data_json)
        elif message_type == 'starting_game':
            try:
                tour = TournamentRoom.objects.get(name=self.tour_group_name)
            except TournamentRoom.DoesNotExist as str: return (str)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'start_game',
                    'player1_image': tour.game.player1.image,
                    'player2_image': tour.game.player2.image,
                    'player1_name': tour.game.player1.login,
                    'player2_name': tour.game.player2.login
                }
            )
        elif message_type == 'updating_room':
            tourRoom = TournamentRoom.objects.get(name=self.tour_group_name)
            if tourRoom and (tourRoom.game.player1 == self.user or tourRoom.game.player2 == self.user):
                await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        elif message_type == 'disconnect':
            await self.disconnect(text_data_json['message'])
        elif message_type == 'stop_game':
            await self.send(text_data=json.dumps({'type': 'stop_game', 'message': 'Tournament', 'user': text_data_json['user']}))

    async def pad_update(self, event):
        if self.game_running:
            await self.send(text_data=json.dumps({
                'player': event['player'],
                'ypos': event['ypos'],
                'message': event['message'],
                'type': event['type']
                }
            ))
    
    async def send_game_update(self, ball, p1Scored, p2Scored, p1, p2):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'message': 'update game ball',
                'type': 'game_update',
                'ball': {'xpos': ball['xpos'], 
                        'ypos': ball['ypos'],
                        'dx': ball['dx'],
                        'dy': ball['dy']},
                'p1Scored': p1Scored,
                'p2Scored': p2Scored,
                'p1': {'xpos': p1['xpos'],
                        'ypos': p1['ypos']},
                'p2': {'xpos': p2['xpos'],
                        'ypos': p2['ypos'],}
            }
        )

    async def removing_player(self, event):
        player = event['player']
        await self.send(text_data=json.dumps({
            'message': 'removing player',
            'type': 'removing_player',
            'player': event['player'],
            'ready': self.isReady()
            }))

    async def game_update(self, event):
        if self.game_running:
            await self.send(text_data=json.dumps({
                'message': 'game update',
                'type': 'ball_update',
                'player': event.get('player'),
                'direction': event.get('direction'),
                'xpos': event.get('ball')['xpos'],
                'ypos': event.get('ball')['ypos'],
                'dx': event.get('ball')['dx'],
                'dy': event.get('ball')['dy'],
                'p1Scored': event.get('p1Scored'),
                'p2Scored': event.get('p2Scored'),
                'p1xpos': event.get('p1')['xpos'],
                'p1ypos': event.get('p1')['ypos'],
                'p2xpos': event.get('p2')['xpos'],
                'p2ypos': event.get('p2')['ypos'],
            }))
        
    async def GameEnd(self):
        try:
            tour = TournamentRoom.objects.get(name=self.tour_group_name)
        except TournamentRoom.DoesNotExist as str: return err(str)
        
        tour.disconnect = False
        tour.save()

        if not tour.player_count > 1:
            await self.tourWinner()
        else:
            await self.nextTour()
    
    async def tourWinner(self):
        self.game_running = False
        await self.send(text_data=json.dumps({
            'type': 'tourWinner',
            'message': 'Announcing Winner',
            'Winner': self.user.login
        }))
    
    async def update_room(self, msg):
        try:
            tour = TournamentRoom.objects.get(name=self.tour_group_name)
        except TournamentRoom.DoesNotExist as str: return err(str)
        
        try:
            nextPlayer = tour.players.exclude(login=msg['user']).first()
        except TournamentRoom.DoesNotExist as str: return err(str)

        if self.user != nextPlayer: return

        try:
            game = GameRoom.objects.get(name=tour.game.name)
        except GameRoom.DoesNotExist as str: return err(str)

        game.player2 = self.user

        game.save()
        tour.save()


        self.room_group_name = tour.game.name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.channel_layer.group_send(self.room_group_name, {'type': 'host_status',
            'message': 'host_status',
            'isHost': False})
        
        await self.channel_layer.group_send(self.room_group_name, 
        {'type': 'addButton', 'players': list(tour.players.values('TourName', 'connected', 'image')), 'ready': self.isReady()})

    async def nextTour(self):
        try:
            tour = TournamentRoom.objects.get(name=self.tour_group_name)
        except TournamentRoom.DoesNotExist as str: return err(str)
        
        self.game_running = False

        #this is where you resetlist 
        await self.send(text_data=json.dumps({
            'type': 'nextTour',
            'players': list(tour.players.values('TourName', 'connected', 'image')),
            'ready': self.isReady()
        }))

        await self.send(text_data=json.dumps({
            'type': 'host_status',
            'isHost': True}))

        tour.game.player2 = None
        tour.game.player1 = self.user
        tour.game.save()
        tour.save()

        await self.channel_layer.group_send(self.tour_group_name, {
            'type': 'update_room', 'user': self.user.login})

        # await self.channel_layer.group_send({'type': 'addButton'})
    
    async def stop_game(self, event):
        self.game_running = False
        if event['message'] == 'handleClickonSidebar' and event['user'] == self.user.login: 
            return 

        await self.send(text_data=json.dumps({
            'type': 'stop_game',
            'message': 'Tournament',
            'players': event['players']
        }))

    async def adding_player(self, event):
        user = event['user']
        if self.user.id != event['user']:
            await self.send(text_data=json.dumps({
                    'message': event['message'],
                    'type': event['type'],
                    'player': event['player'],
                    'ready': self.isReady(),
                    'players': event['players']
                    # 'inRoom': event['inRoom']
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'addButton',
                'players': event['players'],
                'ready': self.isReady()
            }))
        

    async def addButton(self, event):
        await self.send(text_data=json.dumps({
                'type': 'addButton',
                'players': event['players'],
                'ready': self.isReady()
            }))
        


    async def start_game(self, event):
        self.game_running = True
        await self.send(text_data=json.dumps({
            'message': 'The game is starting!',
            'type': 'start_game',
            'player1_image': event['player1_image'],
            'player2_image': event['player2_image'],
            'player1_name': event['player1_name'],
            'player2_name': event['player2_name'],
        }))
     
    async def joining_tournament(self, event):
        await self.send(text_data=json.dumps({
                'type': 'joining_tournament',
                'message': 'joining tournament',
                'players': event['players'],
                'ready': self.isReady()
                # 'inRoom': event['inRoom']
        }))

class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = 'None'
        self.game_running = False

    async def connect(self):
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            return await self.close()
        
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        self.friend = query_params.get('?friend', [None])[0]


        if self.friend:
            user_to_accept = User42.objects.get(id42=self.friend)
            self.room_group_name = await self.assign_room_with_friends(user_to_accept)
        else:
            self.room_group_name = await self.assign_room()
            if self.room_group_name is None:
                return await self.close()

        is_host = False
        room = GameRoom.objects.get(name=self.room_group_name)
        if room.player1 == self.scope["user"]:
            is_host = True
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'host_status',
            'message': 'host_status',
            'isHost': is_host,
        }))

        room_full = await is_room_full(room)
        if room_full:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'start_game',
                    'message': 'The game is starting!',
                    'player1_image': room.player1.image,
                    'player2_image': room.player2.image,
                    'player1_name': room.player1.login,
                    'player2_name': room.player2.login
                }
            )
    
    async def remove_user_from_room(self):
        global ROOM_NUM
        if self.room_group_name:
            try:
                room = GameRoom.objects.get(name=self.room_group_name)
                room.delete()
                ROOM_NUM -= 1
            except GameRoom.DoesNotExist:
                pass
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def disconnect(self, close_code):
        if self.room_group_name:
            try:
                rooms = GameRoom.objects.get(name=self.room_group_name)
            except GameRoom.DoesNotExist as str: return err(str)
            
            if self.game_running and close_code == 'handleClickonSidebar':
                await self.channel_layer.group_send(self.room_group_name, {'type': 'stop_game', 'message': close_code, 'user': self.user.login})
            await self.remove_user_from_room()

    @database_sync_to_async
    def assign_room_with_friends(self, user_to_accept):
        global ROOM_NUM
        #find a gameRoom missing one player and not already joined 
        room = GameRoom.objects.filter(
        Q(player2__isnull=True) | Q(player1__isnull=True)
        ).exclude(
        Q(player1=self.user) | Q(player2=self.user)
        ).exclude(
        Q(name__icontains='Tournament')
        ).exclude(
        Q(withFriends=False)
        ).filter(
        Q(player1=user_to_accept) | Q(player2=user_to_accept)  # Only include rooms where self.friend is player1 or player2
        ).first()  

        if room and ((room.player1 != self.scope["user"]) or (room.player2 != self.scope["user"])):
            if room.player1:
                room.player2 = self.user
            else: 
                room.player1 = self.user
            room.save()
        elif not room:
            with ROOM_NUM_LOCK:
                while True:
                        try:
                            room_name = f'OnlineGameRoom{ROOM_NUM}'
                            room = GameRoom.objects.create(player1=self.user, name=room_name, withFriends=True)
                            ROOM_NUM += 1
                            break
                        except IntegrityError:
                            ROOM_NUM += 1
        return room.name


    @database_sync_to_async
    def assign_room(self):
        global ROOM_NUM
        room = GameRoom.objects.filter(
        Q(player2__isnull=True) | Q(player1__isnull=True)
        ).exclude(
        Q(player1=self.user) | Q(player2=self.user)
        ).exclude(
        Q(name__icontains='Tournament')
        ).first()  
    
        self_scope = self.scope['user']
        if room and ((room.player1 != self.scope["user"]) or (room.player2 != self.scope["user"])):
            if room.player1:
                room.player2 = self.user
            else: 
                room.player1 = self.user
            room.save()
        elif not room:
            with ROOM_NUM_LOCK:
                while True:
                        try:
                            room_name = f'OnlineGameRoom{ROOM_NUM}'
                            room = GameRoom.objects.create(player1=self.user, name=room_name)
                            ROOM_NUM += 1
                            break
                        except IntegrityError:
                            ROOM_NUM += 1
        return room.name
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        if message_type == 'move':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'message': 'update game move',
                    'type': 'game_update',
                    'player': text_data_json['player'],
                    'direction': text_data_json['direction']
                }
            )
        elif message_type == 'ball_update':
            await ball_update(self, text_data_json, 'Game')
        elif message_type == 'stop_game':
            if self.game_running:
                await self.channel_layer.group_send({'type': 'stop_game', 'message': 'onlineGame', 'user': text_data_json['user']})
        elif message_type == 'disconnect':
            return await self.disconnect(text_data_json['message'])
        elif message_type == 'pad_update':
            paddle = text_data_json['pad']
            paddle['type'] = 'pad_update'
            paddle['message'] = 'pad_update'
            isHost = text_data_json['isHost']
            if isHost:
                paddle["player"] = "p1"
            else:
                paddle["player"] = "p2"
            await self.channel_layer.group_send(
                self.room_group_name, paddle)
        elif message_type == 'update_winner':
            await update_winner(self, text_data_json)
    
    async def pad_update(self, event):
        if self.game_running:
            await self.send(text_data=json.dumps({
                'player': event['player'],
                'ypos': event['ypos'],
                'message': event['message'],
                'type': event['type']
                }
            ))
    
    async def send_game_update(self, ball, p1Scored, p2Scored, p1, p2):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'message': 'update game ball',
                'type': 'game_update',
                'ball': {'xpos': ball['xpos'], 
                        'ypos': ball['ypos'],
                        'dx': ball['dx'],
                        'dy': ball['dy']},
                'p1Scored': p1Scored,
                'p2Scored': p2Scored,
                'p1': {'xpos': p1['xpos'],
                        'ypos': p1['ypos']},
                'p2': {'xpos': p2['xpos'],
                        'ypos': p2['ypos'],}
            }
        )
    
    async def game_update(self, event):
        if self.game_running:
            await self.send(text_data=json.dumps({
                'message': 'game update',
                'type': 'ball_update',
                'player': event.get('player'),
                'direction': event.get('direction'),
                'xpos': event.get('ball')['xpos'],
                'ypos': event.get('ball')['ypos'],
                'dx': event.get('ball')['dx'],
                'dy': event.get('ball')['dy'],
                'p1Scored': event.get('p1Scored'),
                'p2Scored': event.get('p2Scored'),
                'p1xpos': event.get('p1')['xpos'],
                'p1ypos': event.get('p1')['ypos'],
                'p2xpos': event.get('p2')['xpos'],
                'p2ypos': event.get('p2')['ypos'],
            }))
    
    async def stop_game(self, event):

        if event['message'] == 'handleClickonSidebar' and event['user'] == self.user.login: 
            return 

        if self.game_running:
            await self.send(text_data=json.dumps({
                'type': 'stop_game',
                'message': 'onlineGame',
            }))
        self.game_running = False

    async def host_status(self, event):
        await self.send(text_data=text_data_json({
            'message': event['message'],
            'isHost': event['isHost'],
        }))
    
    async def start_game(self, event):
        self.game_running = True
        await self.send(text_data=json.dumps({
            'message': 'The game is starting!',
            'player1_image': event['player1_image'],
            'player2_image': event['player2_image'],
            'player1_name': event['player1_name'],
            'player2_name': event['player2_name']
        }))

class ChatroomConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_group_name = 'None'
        self.receiver = None
        self.id = 1

    async def connect(self):

        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        await self.accept()

    @staticmethod
    def generate_random_name(length=12):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(length))
    

    @database_sync_to_async
    def assign_chat_group(self):
        user = User42.objects.get(login=self.user.login)
        chatgroups = ChatGroup.objects.filter(authors=user).filter(authors=self.receiver)
        if chatgroups.count() == 0:
            while (ChatGroup.objects.filter(id=self.id).first()):
                self.id = self.id + 1
            chatgroup = ChatGroup.objects.create(id=self.id, group_name=self.generate_random_name())
            chatgroup.save()
            ChatGroup.objects.get(pk=self.id).authors.add(user, self.receiver)
            self.id = self.id + 1
            self.chatgroup = chatgroup
            return chatgroup.group_name

        if chatgroups.count() == 1:
            self.chatgroup = chatgroups.first()
            chatgroups.first().authors.add(self.receiver)
            return chatgroups.first().group_name
        return None
            

    def checkBlocked(self):
        blocked = self.receiver.blocked.filter(login=self.user.login)
        blocked2 = self.user.blocked.filter(login=self.receiver.login)
        if blocked or blocked2:
            return 1
        return 0

    async def disconnect(self, code):
        print('disconnect')

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
    
        if "addReceiver" in text_data_json:
            receiver_id = text_data_json["addReceiver"]
            try:
                self.receiver = User42.objects.get(id42=receiver_id)
            except User42.DoesNotExist:
                return
            self.chat_group_name = await self.assign_chat_group()
            await self.channel_layer.group_add(
                self.chat_group_name,
                self.channel_name
            )
            block = self.checkBlocked()
            if (block):
                await self.channel_layer.group_send(
                    self.chat_group_name, {
                        'type': "blocked_user",
                    }
                )
                return
            if self.chat_group_name is None:
                await self.close()
                return
        else:
            block = self.checkBlocked()
            if (block):
                await self.channel_layer.group_send(
                    self.chat_group_name, {
                        'type': "blocked_user",
                    }
                )
                return
            # text_data_json = json.loads(text_data)
            body = text_data_json['body']

            message = GroupMessage.objects.create(
                body = body,
                author = self.user,
                group = self.chatgroup
            )

            await self.channel_layer.group_send(
                self.chat_group_name, {
                    'type': "message_handler",
                    'message_id': message.id
                }
            )

    async def message_handler(self, event):
        message_id = event["message_id"]
        message = GroupMessage.objects.get(id=message_id)
        context = {
            'message': message,
            'user': self.user,
            'blocked': False,
        }
        html = render_to_string("toInject/chat_message_p.html", context=context)
        await self.send(text_data=html)

    async def blocked_user(self, event):
        context = {
            'blocked': True,
        }
        html = render_to_string("toInject/chat_message_p.html", context)
        await self.send(text_data=html)

