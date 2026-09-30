import math
import random


class ServerPellet:
	def __init__(
		self,
		owner_id: str,
		x: float,
		y: float,
		dir_x: float,
		dir_y: float,
		velocity: float = 15.0,
		damage: float = 8.0,
		radius: float = 4.0,
		lifetime: float = 1.2,
		active: bool = True,
	) -> None:
		self.owner_id = owner_id
		self.x = x
		self.y = y
		self.dir_x = dir_x
		self.dir_y = dir_y
		self.velocity = velocity
		self.damage = damage
		self.radius = radius
		self.lifetime = lifetime
		self.active = active


def spawn_shotgun_pellets(
	owner_id: str,
	start_x: float,
	start_y: float,
	aim_x: float,
	aim_y: float,
) -> list[ServerPellet]:
	base_angle = math.atan2(aim_y, aim_x)
	pellets = []
	for index in range(10):
		spread_degrees = -15.0 + index * (30.0 / 9.0)
		angle = base_angle + math.radians(
			spread_degrees + random.uniform(-4.0, 4.0)
		)
		pellets.append(
			ServerPellet(
				owner_id,
				start_x,
				start_y,
				math.cos(angle),
				math.sin(angle),
			)
		)
	return pellets


def _player_value(player, name, default=None):
	if isinstance(player, dict):
		return player.get(name, default)
	return getattr(player, name, default)


def update_all_pellets(
	pellets: list[ServerPellet],
	dt: float,
	walls: list[tuple],
	players: dict,
	current_time: float,
) -> list[dict]:
	hit_events = []
	for pellet in pellets:
		if not pellet.active:
			continue

		pellet.x += pellet.dir_x * pellet.velocity
		pellet.y += pellet.dir_y * pellet.velocity
		pellet.lifetime -= dt
		if pellet.lifetime <= 0:
			pellet.active = False
			continue

		if any(
			wx <= pellet.x <= wx + ww and wy <= pellet.y <= wy + wh
			for wx, wy, ww, wh in walls
		):
			pellet.active = False
			continue

		for player_id, player in players.items():
			if player_id == pellet.owner_id or not _player_value(player, "alive", False):
				continue
			player_x = _player_value(player, "x")
			player_y = _player_value(player, "y")
			player_radius = _player_value(player, "radius", 0)
			if player_x is None or player_y is None:
				continue
			if math.hypot(pellet.x - player_x, pellet.y - player_y) < (
				pellet.radius + player_radius
			):
				player.take_damage(pellet.damage, current_time)
				pellet.active = False
				hit_events.append(
					{
						"attacker": pellet.owner_id,
						"target": player_id,
						"damage": pellet.damage,
					}
				)
				break

	pellets[:] = [pellet for pellet in pellets if pellet.active]
	return hit_events


def serialize_pellets(pellets: list[ServerPellet]) -> list[list]:
	return [
		[round(pellet.x, 1), round(pellet.y, 1)]
		for pellet in pellets
		if pellet.active
	]
