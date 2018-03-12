
from db import *

class User(Entry):
	_table_name = 'users'
	
	def __init__(self):
		Entry.__init__(self)
		self.name = ''
		self.pswd = ''
		self.data = ''

add_entry_subclass(User)


class Request(Entry):
	_table_name = 'requests'
	
	def __init__(self):
		Entry.__init__(self)
		self.user = None
		self.number_of_players = 2
		self.title = ''
		self.data = ''
		self.game = None


add_entry_subclass(Request)


class Game(Entry):
	_table_name = 'games'
	
	def __init__(self):
		Entry.__init__(self)
		self.title = ''
		self.data = ''

add_entry_subclass(Game)


class Move(Entry):
	_table_name = 'moves'
	
	def __init__(self):
		Entry.__init__(self)
		self.player = None
		self.game = None
		self.data = ''

add_entry_subclass(Move)


class Server:
	def __init__(self):
		self.error = ''
	
	def open(self):
		self._db = Database()
		self._db.open('games.sqlite')
	
	
	def close(self):
		self._db.close()
	
	
	def create_account(self, name, pswd, data):
		'''Create a new user with the given info'''
		u_already = self.get_user(name, '', False)
		
		if u_already:
			self.error = 'User already exists.'
			return False
		else:
			user = User()
			user.name = name
			user.pswd = pswd
			user.data = data
			self._db.save(user)
			return True
	
	
	def update_account(self, name, pswd, newpswd, data):
		'''Modifies an existing user with the given info'''
		user = self.get_user(name, pswd)
		
		if not user:
			return False
		else:
			if newpswd:
				user.pswd = newpswd
			if data:
				user.data = data
			self._db.save(user)
			return True
	
	
	def authenticate(self, u, pswd):
		if u.pswd == pswd:
			return True
		self.error = 'Authentication error.'
		return False
	
	
	def get_user(self, name, pswd, auth_needed = True):
		l = self._db.load(User, 'name = ' + repr(name))
		if not l:
			self.error = 'User does not exist.'
			return None
		user = l[0]
		if not auth_needed:
			return user
		if not self.authenticate(user, pswd):
			return None
		return user
	
	
	def create_request(self, name, pswd, title, number_of_players=2, data=''):
		'''Makes a request on behalf of the named user'''
		user = self.get_user(name, pswd)
		if not user:
			return False
		r = Request()
		r.user = user
		r.number_of_players = number_of_players
		r.title = title
		r.data = data
		self._db.save(r)
		self.marshal_requests()
		return True
	
	
	def marshal_requests(self):
		'''Iterates through the requests and collects them to form games.'''
		
		unfilled_requests = self._db.load(Request, 'game = ""')
		
		number_request_map = {}
		for request in unfilled_requests:
			number_title = (request.number_of_players, request.title)
			base = number_request_map.get(number_title, [])
			number_request_map[number_title] = base + [request]
		
		for n, title in number_request_map:
			request_list = number_request_map[(n, title)]
			
			if len(request_list) >= n:
				player_request_map = {}
				
				for request in request_list:
					base = player_request_map.get(request.user, [])
					player_request_map[request.user] = base + [request]
				
				while len(player_request_map) >= n:
					game = Game()
					game.title = title
					self._db.save(game)
					i = 0
					delete_keys = []
					# obtain data from the earliest request
					date = 0
					for player in player_request_map:
						request = player_request_map[player].pop()
						if date==0 or request._created_at < date:
							game.data = request.data
							date = request._created_at
						if not player_request_map[player]:
							delete_keys.append(player)
						request.game = game
						self._db.save(request)
						self._db.save(game)
						i += 1
						if i >= n:
							break
					for k in delete_keys:
						del player_request_map[k]
	
	
	def get_request(self, request_id):
		requests = self._db.load(Request, 'id = ' + str(request_id))
		if not requests:
			self.error = 'Request not found.'
			return
		return requests[0]
	
	
	def get_requests(self, name, pswd, title):
		'''Gets all requests for a given user with a name and password.'''
		self.marshal_requests()
		user = self.get_user(name, pswd)
		if not user:
			return
		requests = self._db.load(Request, 'title = ' + repr(title) + ' and user = "User ' + str(user._id) + '"')
		def compare_requests(a, b):
			d = a._created_at - b._created_at
			if d != 0:
				return d
			return a._id - b._id
		requests.sort()
		return requests
	
	
	def get_request_map(self, name, pswd, title):
		'''Gets a map whose keys are requests and whose values are the game
		that request turned into if there is one'''
		requests = self.get_requests(name, pswd, title)
		if requests == None:
			return
		grm = {}
		for request in requests:
			grm[request] = request.game
		return grm
	
	
	def cancel_request(self, name, pswd, title, request):
		'''Cancels a request'''
		
		if not request:
			return False
		
		if not request.user:
			return False
		
		user = self.get_user(request.user.name, request.user.pswd)
		if not user:
			return False
		
		criteria = 'title = ' + repr(title)
		criteria += ' and user = "User ' + str(user._id) + '"'
		criteria += ' and title = ' + repr(title)
		criteria += ' and id = ' + str(request._id)
		
		requests = self._db.load(Request, criteria)
		
		if not requests:
			return False
		
		self._db.delete(requests[0])
		self.marshal_requests()
		return True
	
	
	def make_move(self, name, pswd, game, data, game_data):
		'''Saves a move object with the given data string with the associated game.'''
		user = self.get_user(name, pswd)
		
		if not user:
			return
		
		move = Move()
		move.player = user
		move.data = data
		move.game = game
		
		if game_data:
			game.data = game_data
		
		self._db.save(move)
		self._db.save(game)
		return True
	
	
	def get_players(self, game):
		requests = self._db.load(Request, 'game = "Game ' + str(game._id) + '"')
		players = []
		for request in requests:
			players.append(request.user)
		return players
	
	
	def get_game(self, game_id):
		if type(game_id) == str:
			l = game_id.split()
			if len(l) > 1 and l[0] == 'Game':
				game_id = l[1]
		games = self._db.load(Game, 'id = ' + str(game_id))
		if not games:
			self.error = 'Game not found.'
			return
		return games[0]
	
	
	def get_moves(self, name, pswd, game):
		user = self.get_user(name, pswd)
		if not user:
			return
		moves = self._db.load(Move, 'game = "Game ' + str(game._id) + '"')
		return moves
	
	
	## Below are more admin-type queries.
	
	def get_all_users(self):
		users = self._db.load(User, '')
		return users
	
	def get_user_requests(self, name):
		self.marshal_requests()
		user = self.get_user(name, '', False)
		if not user:
			self.error = 'User does not exist.'
			return []
		requests = self._db.load(Request, 'user = "User ' + str(user._id) + '"')
		def compare_requests(a, b):
			d = a._created_at - b._created_at
			if d != 0:
				return d
			return a._id - b._id
		requests.sort()
		return requests
	
	def get_game_moves(self, game_id):
		game_identifier = game_id
		if type(game_id) == str:
			if not game_id.startswith('Game '):
				game_identifier = 'Game ' + game_id
		moves = self._db.load(Move, 'game = "' + game_identifier + '"')
		return moves
	
	def delete_game(self, game):
		'''deletes the game object and the requests that point to it'''
		requests = self._db.load(Request, 'game = "Game ' + str(game._id) + '"')
		moves = self._db.load(Move, 'game = "Game ' + str(game._id) + '"')
		
		self._db.delete(game)
		
		for move in moves:
			self._db.delete(move)
		
		for request in requests:
			self._db.delete(request)
	
	def delete(self, identifier):
		typename, id = identifier.split()
		
		Class = None
		if typename == 'Move':
			Class = Move
		
		if typename == 'User':
			Class = User
		
		if typename == 'Request':
			Class = Request
		
		if typename == 'Game':
			Class = Game
		
		if Class == None:
			self.error = 'Class name ' + typename + ' not found.'
			return False
		
		l = self._db.load(Class, 'id = ' + str(id))
		if not l:
			self.error = typename + ' with id = ' + str(id) + ' not found.'
			return False
		
		obj = l[0]
		
		if Class == Game:
			self.delete_game(obj)
		else:
			self._db.delete(obj)
		
		return True

