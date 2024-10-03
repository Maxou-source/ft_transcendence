from django.db import models
from django.conf import settings

class UserHistory(models.Model):
    userScore = models.IntegerField(default=0)
    otherScore = models.IntegerField(default=0)
    opponent = models.CharField(max_length=50)#opponent login
    date = models.DateTimeField(auto_now_add=True)
    mode = models.CharField(max_length=50)

class User42(models.Model):
    profil_url = models.CharField(max_length=100)
    login = models.CharField(max_length=50)
    pseudo = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=100)
    wallet = models.BigIntegerField()
    pool_year = models.BigIntegerField()
    image = models.CharField(max_length=100)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    id42 = models.IntegerField(default=0)
    connected = models.BooleanField(default=False)
    chatId = models.IntegerField(default=0)
    userFriends = models.ManyToManyField("self", blank=True, symmetrical=True, related_name='friends_set')
    blocked = models.ManyToManyField("self", blank=True, symmetrical=True, related_name='blocked_set')
    GameHistory = models.ManyToManyField(UserHistory, blank=True, related_name="game_history")
    TourName = models.CharField(max_length=255, blank=True, null=True, unique=True)

    def __str__(self):
        return self.login

class Friend(models.Model):
    from_user = models.ForeignKey(User42, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User42, related_name='to_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class FriendList(models.Model):
    user  = models.OneToOneField(User42, on_delete=models.CASCADE,
                                 related_name="User42")
    friends = models.ManyToManyField(User42, blank=True,
                                     related_name="friends")

    def __str__(self):
        return self.user.login
    
    def add_friend(self, account):
        if not account in self.friends.all():
            self.friends.add(account)
            self.save()

    def remove_friend(self, account):
        if account in self.friends.all():
            self.remove(account)

    def unfriend(self, removee):
        remover_friends_list = self

        remover_friends_list.remove_friend(removee)

        friends_list = FriendList.object.get(user=removee)
        friends_list.remove_friend(self.user)
    
    def areWeFriends(self, friend):
        if friend in self.friends.all():
            return True
        return False

class FriendRequest(models.Model):
    sender = models.ForeignKey(User42, blank=True, null=True, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User42, blank=True, null=True, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}"

class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128, unique=True)
    authors = models.ManyToManyField(User42, related_name='chat_groups')

    def __str__(self):
        # author_list = ', '.join([author.login for author in self.authors.all()])
        # return f'{self.group_name} | Authors: {author_list}'
        return f" chatgroup {self.group_name}"

class GroupMessage(models.Model):
	group = models.ForeignKey(ChatGroup, related_name='chat_messages', on_delete=models.CASCADE)
	author = models.ForeignKey(User42, on_delete=models.CASCADE)
	body = models.CharField(max_length=300)
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.author.username} : {self.body}'

	class Meta:
		ordering = ['-created']


class GameRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    player1 = models.ForeignKey(User42, on_delete=models.CASCADE, related_name='player1', null=True, blank=True)
    player2 = models.ForeignKey(User42, on_delete=models.CASCADE, related_name='player2', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    withFriends = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} | players: {self.player1} | {self.player2}"

class TournamentRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    game = models.ForeignKey(GameRoom, on_delete=models.CASCADE, related_name='tournamentGameRoom', null=True, blank=True)
    players = models.ManyToManyField(User42, blank=True, related_name="TournamentPlayers")
    player_count = models.IntegerField(default=0)
    disconnect = models.BooleanField(default=False)

    def __str__(self):
        return self.name

