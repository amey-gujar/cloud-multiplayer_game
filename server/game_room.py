import math
import time


from map_data import MAP_WIDTH, MAP_HEIGHT, WALLS
from physics import apply_player_movement
from player_state import PlayerState
from weapons import spawn_shotgun_pellets, update_all_pellets, serialize_pellets


class GameRoom:
	def __init__(self, room_id: str, max_players: int = 4):
		self.room_id = room_id
		self.max_players = max_players
		self.state = "WAITING"
		self.players = {}
		self.pellets = []
		self.spawn_points = [(400, 400), (2000, 400), (400, 1600), (2000, 1600)]
		self.center_x = MAP_WIDTH / 2
		self.center_y = MAP_HEIGHT / 2
		self.radius = 1300.0
		self.min_radius = 100.0
		self.shrink_rate = 15.0
		self.storm_damage_rate = 5.0
		self.winner_id = None
		self._initial_player_count = 0

	def add_player(self, player_id: str, username: str) -> bool:
		if len(self.players) >= self.max_players or self.state != "WAITING":
			return False
		spawn_x, spawn_y = self.spawn_points[len(self.players) % len(self.spawn_points)]
		self.players[player_id] = PlayerState(player_id, username, spawn_x, spawn_y)
		if len(self.players) >= 2:
			self.state = "IN_GAME"
			self._initial_player_count = len(self.players)
		return True

	def remove_player(self, player_id: str):
		self.players.pop(player_id, None)

	def handle_player_input(self, player_id: str, input_data: dict, current_time: float):
		player = self.players.get(player_id)
		if player is None:
			return
		player.apply_input(
			input_data.get("move_x", 0),
			input_data.get("move_y", 0),
			input_data.get("shooting", False),
			input_data.get("aim_x", 0),
			input_data.get("aim_y", 0),
		)
		if input_data.get("shoot") and player.can_shoot(current_time):
			self.pellets.extend(
				spawn_shotgun_pellets(player_id, player.x, player.y, player.aim_x, player.aim_y)
			)
			player.ammo -= 1
			player.last_shot_time = current_time
		if input_data.get("reload"):
			player.start_reload(current_time)

	def update(self, dt: float, current_time: float):
		if self.state != "IN_GAME":
			return
		for player in self.players.values():
			if not player.alive:
				continue
			player.x, player.y = apply_player_movement(
				player.x, player.y, player.vx, player.vy,
				player.move_x, player.move_y, WALLS, MAP_WIDTH, MAP_HEIGHT,
			)
			player.update_shield(current_time, dt)
			player.update_reload(current_time)
			if math.hypot(player.x - self.center_x, player.y - self.center_y) > self.radius:
				player.take_damage(self.storm_damage_rate * dt, current_time)

		update_all_pellets(self.pellets, dt, WALLS, self.players, current_time)
		self.radius = max(self.min_radius, self.radius - self.shrink_rate * dt)
		alive_players = [player for player in self.players.values() if player.alive]
		if len(alive_players) == 1 and self._initial_player_count >= 2:
			self.state = "FINISHED"
			self.winner_id = alive_players[0].player_id
		elif len(alive_players) == 0:
			self.state = "FINISHED"
			self.winner_id = "DRAW"

	def get_snapshot(self) -> dict:
		return {
			"state": self.state,
			"winner": self.winner_id,
			"zone": [round(self.center_x, 1), round(self.center_y, 1), round(self.radius, 1)],
			"players": [player.to_dict() for player in self.players.values()],
			"pellets": serialize_pellets(self.pellets),
		}
