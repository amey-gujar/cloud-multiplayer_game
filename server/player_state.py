import math


class PlayerState:
    def __init__(self, player_id: str, username: str, start_x: float, start_y: float):
        self.player_id = player_id
        self.username = username
        self.x = float(start_x)
        self.y = float(start_y)
        self.vx = 0.0
        self.vy = 0.0

        self.health = 100.0
        self.max_health = 100.0
        self.shield = 50.0
        self.max_shield = 50.0
        self.last_damage_time = 0.0
        self.is_alive = True

        self.ammo = 8
        self.capacity = 8
        self.reserve_ammo = 40
        self.shot_delay = 0.85
        self.last_shot_time = -0.85
        self.reloading = False
        self.shell_reload_time = 0.375
        self.last_shell_time = 0.0

        self.move_x = 0
        self.move_y = 0
        self.aim_dir_x = 1.0
        self.aim_dir_y = 0.0

    def apply_input(self, input_data: dict) -> None:
        self.move_x = max(-1.0, min(1.0, float(input_data.get("move_x", 0))))
        self.move_y = max(-1.0, min(1.0, float(input_data.get("move_y", 0))))

        aim_x = float(input_data.get("aim_dir_x", self.aim_dir_x))
        aim_y = float(input_data.get("aim_dir_y", self.aim_dir_y))
        magnitude = math.hypot(aim_x, aim_y)
        if magnitude > 0.0:
            self.aim_dir_x = aim_x / magnitude
            self.aim_dir_y = aim_y / magnitude

    def take_damage(self, damage: float, current_time: float) -> None:
        self.last_damage_time = current_time
        remaining = max(0.0, float(damage))
        absorbed = min(self.shield, remaining)
        self.shield -= absorbed
        remaining -= absorbed
        self.health = max(0.0, self.health - remaining)
        if self.health == 0.0:
            self.is_alive = False

    def update_shield(self, current_time: float, dt: float) -> None:
        if current_time - self.last_damage_time >= 7.0 and self.shield < self.max_shield:
            self.shield = min(self.max_shield, self.shield + 10.0 * max(0.0, dt))

    def can_shoot(self, current_time: float) -> bool:
        return (
            self.is_alive
            and not self.reloading
            and current_time - self.last_shot_time >= self.shot_delay
            and self.ammo > 0
        )

    def start_reload(self, current_time: float) -> None:
        if self.ammo < self.capacity and self.reserve_ammo > 0:
            self.reloading = True
            self.last_shell_time = current_time

    def update_reload(self, current_time: float) -> None:
        if not self.reloading:
            return
        if self.ammo >= self.capacity or self.reserve_ammo <= 0:
            self.reloading = False
            return
        if current_time - self.last_shell_time >= self.shell_reload_time:
            self.ammo += 1
            self.reserve_ammo -= 1
            self.last_shell_time = current_time
            if self.ammo >= self.capacity or self.reserve_ammo <= 0:
                self.reloading = False

    def to_dict(self) -> dict:
        return {
            "id": self.player_id,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "vx": round(self.vx, 1),
            "vy": round(self.vy, 1),
            "hp": int(self.health),
            "sh": int(self.shield),
            "ammo": self.ammo,
            "res": self.reserve_ammo,
            "reload": self.reloading,
            "alive": self.is_alive,
        }