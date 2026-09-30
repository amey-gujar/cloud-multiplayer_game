"""Dependency-free authoritative server physics."""

import math

RADIUS = 20
ACCELERATION = 0.45
FRICTION = 0.985
RECOIL_FRICTION = 0.990
MAX_SPEED = 7.0
MAX_RECOIL_SPEED = 20.0
BOUNCE = 0.85


class AABB:
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x, self.y = x, y
        self.width, self.height = width, height

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.height

    def intersects(self, other: "AABB") -> bool:
        return (self.left < other.right and self.right > other.left and
                self.top < other.bottom and self.bottom > other.top)

    def contains_point(self, px: float, py: float) -> bool:
        return self.left <= px <= self.right and self.top <= py <= self.bottom


def _wall(wall):
    return AABB(*wall)


def apply_player_movement(pos_x, pos_y, vel_x, vel_y, move_x, move_y,
                          walls, map_w, map_h):
    length = math.hypot(move_x, move_y)
    if length > 0:
        vel_x += move_x / length * ACCELERATION
        vel_y += move_y / length * ACCELERATION

    speed = math.hypot(vel_x, vel_y)
    if speed > MAX_RECOIL_SPEED:
        factor = MAX_RECOIL_SPEED / speed
        vel_x *= factor
        vel_y *= factor

    pos_x += vel_x
    player = AABB(pos_x - RADIUS, pos_y - RADIUS, RADIUS * 2, RADIUS * 2)
    for wall in walls:
        box = _wall(wall)
        if player.intersects(box):
            pos_x = box.left - RADIUS if vel_x > 0 else box.right + RADIUS
            vel_x = -vel_x * BOUNCE
            player = AABB(pos_x - RADIUS, pos_y - RADIUS, RADIUS * 2, RADIUS * 2)

    pos_y += vel_y
    player = AABB(pos_x - RADIUS, pos_y - RADIUS, RADIUS * 2, RADIUS * 2)
    for wall in walls:
        box = _wall(wall)
        if player.intersects(box):
            pos_y = box.top - RADIUS if vel_y > 0 else box.bottom + RADIUS
            vel_y = -vel_y * BOUNCE
            player = AABB(pos_x - RADIUS, pos_y - RADIUS, RADIUS * 2, RADIUS * 2)

    if pos_x < RADIUS:
        pos_x, vel_x = RADIUS, abs(vel_x) * BOUNCE
    elif pos_x > map_w - RADIUS:
        pos_x, vel_x = map_w - RADIUS, -abs(vel_x) * BOUNCE
    if pos_y < RADIUS:
        pos_y, vel_y = RADIUS, abs(vel_y) * BOUNCE
    elif pos_y > map_h - RADIUS:
        pos_y, vel_y = map_h - RADIUS, -abs(vel_y) * BOUNCE

    friction = RECOIL_FRICTION if math.hypot(vel_x, vel_y) > MAX_SPEED else FRICTION
    return pos_x, pos_y, vel_x * friction, vel_y * friction


def update_bullet(bx, by, dir_x, dir_y, speed, walls):
    bx += dir_x * speed
    by += dir_y * speed
    return bx, by, not any(_wall(wall).contains_point(bx, by) for wall in walls)


def check_bullet_player_hit(bx, by, b_radius, px, py, p_radius) -> bool:
    return math.hypot(bx - px, by - py) < b_radius + p_radius