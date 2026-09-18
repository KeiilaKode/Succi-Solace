#-enemies-#

import pygame
import random
from entities import SpriteSheet

# ==========================================
# MASTER ENEMY CLASSES
# ==========================================

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                 health, rem_value, speed, anim_speed, y_offset=160, attack_fx=None):
        super().__init__()
        self.health = health
        self.rem_value = rem_value
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.attack_fx = attack_fx

        self.frame_index, self.update_time = 0, pygame.time.get_ticks()
        self.anim_speed = anim_speed
        self.patrol_start_x, self.patrol_end_x = patrol_start_x, patrol_end_x
        self.speed, self.direction, self.state = speed, 1, "walk"

        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.rect.bottom = y_pos + y_offset
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self, amount=1):
        self.health -= amount
        return self.health <= 0

    def update(self, camera_x, player_x=None, player_y=None):
        # Aggro Logic
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 310 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1
                if self.attack_fx:
                    try:
                        self.attack_fx.play()
                    except pygame.error:
                        pass

        # Walk State
        if self.state == "walk":
            self.rect.x += self.direction * self.speed
            if self.rect.x >= self.patrol_end_x:
                self.rect.x, self.direction = self.patrol_end_x, -1
            elif self.rect.x <= self.patrol_start_x:
                self.rect.x, self.direction = self.patrol_start_x, 1

            if pygame.time.get_ticks() - self.update_time > self.anim_speed:
                self.update_time, self.frame_index = pygame.time.get_ticks(), (self.frame_index + 1) % len(
                    self.walk_frames_right)

            self.image = self.walk_frames_right[self.frame_index] if self.direction == 1 else self.walk_frames_left[
                self.frame_index]

        # Attack State
        elif self.state == "attack":
            if pygame.time.get_ticks() - self.update_time > 70:
                self.update_time, self.frame_index = pygame.time.get_ticks(), self.frame_index + 1
                if self.frame_index >= len(self.attack_frames_right):
                    self.state, self.frame_index = "walk", 0

            if self.state == "attack":
                self.image = self.attack_frames_right[self.frame_index] if self.direction == 1 else \
                self.attack_frames_left[self.frame_index]

        # Physics & Mask Updates
        old_bottom = self.rect.bottom
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.bottom = old_bottom

        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        if self.rect.right < camera_x - 1000:
            self.kill()


class BaseIdleEnemy(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r, attack_l,
                 health, rem_value, speed, anim_speed, y_offset=160, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health, rem_value, speed, anim_speed, y_offset, attack_fx)
        self.idle_frames_right = idle_r
        self.idle_frames_left = idle_l

    def update(self, camera_x, player_x=None, player_y=None):
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 300 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1
                if self.attack_fx:
                    try:
                        self.attack_fx.play()
                    except pygame.error:
                        pass

        if self.state == "walk":
            self.rect.x += self.direction * self.speed
            if self.rect.x >= self.patrol_end_x or self.rect.x <= self.patrol_start_x:
                self.rect.x = self.patrol_end_x if self.direction == 1 else self.patrol_start_x
                self.direction *= -1
                self.state, self.frame_index = "idle", 0
            if self.state == "walk":
                if pygame.time.get_ticks() - self.update_time > self.anim_speed:
                    self.update_time, self.frame_index = pygame.time.get_ticks(), (self.frame_index + 1) % len(
                        self.walk_frames_right)
                self.image = self.walk_frames_right[self.frame_index] if self.direction == 1 else self.walk_frames_left[
                    self.frame_index]

        if self.state == "idle":
            if pygame.time.get_ticks() - self.update_time > 120:
                self.update_time, self.frame_index = pygame.time.get_ticks(), self.frame_index + 1
                if self.frame_index >= len(self.idle_frames_right): self.state, self.frame_index = "walk", 0
            if self.state == "idle":
                self.image = self.idle_frames_right[self.frame_index] if self.direction == 1 else self.idle_frames_left[
                    self.frame_index]

        if self.state == "attack":
            if pygame.time.get_ticks() - self.update_time > 80:
                self.update_time, self.frame_index = pygame.time.get_ticks(), self.frame_index + 1
                if self.frame_index >= len(self.attack_frames_right): self.state, self.frame_index = "walk", 0
            if self.state == "attack":
                self.image = self.attack_frames_right[self.frame_index] if self.direction == 1 else \
                self.attack_frames_left[self.frame_index]

        old_bottom = self.rect.bottom
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.bottom = old_bottom

        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        if self.rect.right < camera_x - 1000: self.kill()


# ==========================================
# SPECIFIC ENEMIES
# ==========================================
# - - - LEVEL 1 ENEMIES - - - #

class Demon(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=1, rem_value=5, speed=2.0, anim_speed=100, y_offset=85, attack_fx=attack_fx)

class Cecil(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=2, rem_value=6, speed=2.2, anim_speed=90, y_offset=160, attack_fx=attack_fx)

class Margret(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=2, rem_value=8, speed=2.4, anim_speed=90, y_offset=160, attack_fx=attack_fx)

class Lashly(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=3, rem_value=12, speed=1.8, anim_speed=100, y_offset=160, attack_fx=attack_fx)

class Hellguard(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=2, rem_value=8, speed=1.8, anim_speed=90, y_offset=210, attack_fx=attack_fx)


# - - - LEVEL 2 ENEMIES - - - #

class Helldog(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=2, rem_value=10, speed=3.5, anim_speed=80, attack_fx=attack_fx)

class Mau(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=3, rem_value=12, speed=2.0, anim_speed=100, attack_fx=attack_fx)

class Pkgrim(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=2, rem_value=8, speed=2.5, anim_speed=90, attack_fx=attack_fx)

class Castleguard(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=3, rem_value=12, speed=1.9, anim_speed=90, y_offset=210, attack_fx=attack_fx)


# - - - LEVEL 3 ENEMIES - - - #

class Azule(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=3, rem_value=12, speed=2.2, anim_speed=90, attack_fx=attack_fx)

class Titus(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=4, rem_value=15, speed=1.8, anim_speed=100, attack_fx=attack_fx)

class Lionel(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=4, rem_value=15, speed=2.5, anim_speed=90, attack_fx=attack_fx)


# - - - LEVEL 4 ENEMIES - - - #

class Elaine(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=5, rem_value=18, speed=2.5, anim_speed=90, attack_fx=attack_fx)

class RoyalHH(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=4, rem_value=15, speed=2.8, anim_speed=65, attack_fx=attack_fx)

class RoyalZombie(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=5, rem_value=18, speed=2.0, anim_speed=100, attack_fx=attack_fx)

class Zombie1(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=3, rem_value=10, speed=1.9, anim_speed=100, attack_fx=attack_fx)

class Zombie2(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=3, rem_value=12, speed=2.1, anim_speed=100, attack_fx=attack_fx)


# --- LEVEL 5 ENEMIES --- #

class Priestly(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=5, rem_value=20, speed=2.0, anim_speed=90, attack_fx=attack_fx)

class Realmwalker(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=6, rem_value=22, speed=3.0, anim_speed=80, attack_fx=attack_fx)

class Pursuer(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=6, rem_value=25, speed=2.5, anim_speed=90, attack_fx=attack_fx)

class Braid(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=6, rem_value=24, speed=2.4, anim_speed=90, attack_fx=attack_fx)

class Deadlight(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=6, rem_value=25, speed=2.6, anim_speed=90, attack_fx=attack_fx)


# --- LEVEL 6 ENEMIES --- #

class Victoria(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=7, rem_value=30, speed=2.6, anim_speed=90, attack_fx=attack_fx)

class Kali(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=6, rem_value=28, speed=2.8, anim_speed=90, attack_fx=attack_fx)

class Kimoura(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=7, rem_value=30, speed=2.5, anim_speed=90, attack_fx=attack_fx)

class Cassie(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=7, rem_value=32, speed=2.7, anim_speed=90, attack_fx=attack_fx)

class Silas(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=9, rem_value=35, speed=2.2, anim_speed=100, attack_fx=attack_fx)

class Thad(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=8, rem_value=30, speed=3.0, anim_speed=80, attack_fx=attack_fx)


# --- LEVEL 7 ENEMIES --- #

class Molly(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=10, rem_value=40, speed=2.0, anim_speed=90, y_offset=160, attack_fx=attack_fx)

class Skelter(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=8, rem_value=32, speed=2.6, anim_speed=90, attack_fx=attack_fx)

class Tilde(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=7, rem_value=30, speed=3.2, anim_speed=80, attack_fx=attack_fx)

class Topaz(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=12, rem_value=45, speed=1.8, anim_speed=100, attack_fx=attack_fx)

class Volgrim(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=8, rem_value=35, speed=2.8, anim_speed=90, attack_fx=attack_fx)

class Voss(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=10, rem_value=38, speed=2.2, anim_speed=90, attack_fx=attack_fx)


# ==========================================
# IDLE ENEMIES
# ==========================================
# LEVEL 1 ENEMY #
class Skeleton(BaseIdleEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r,
                 attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r,
                         attack_l,
                         health=1, rem_value=5, speed=1.8, anim_speed=100, y_offset=240, attack_fx=attack_fx)

# LEVEL 3 ENEMY #
class Demented(BaseIdleEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r,
                 attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r,
                         attack_l,
                         health=3, rem_value=12, speed=1.8, anim_speed=100, attack_fx=attack_fx)

# LEVEL 4 ENEMY #
class Groundskeeper(BaseIdleEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r,
                 attack_l, attack_fx=None):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r,
                         attack_l,
                         health=4, rem_value=15, speed=1.8, anim_speed=100, attack_fx=attack_fx)


# ==========================================
# FLYING ENEMY & OTHER ENTITIES
# ==========================================

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x_pos, y, bird_sheet_img, scale, forced_direction=None):
        super().__init__()
        self.rem_value = 3
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.direction = forced_direction if forced_direction is not None else random.choice([-1, 1])

        sprite_sheet = SpriteSheet(bird_sheet_img)
        fw = bird_sheet_img.get_width() // 8
        fh = bird_sheet_img.get_height()

        for i in range(8):
            img = sprite_sheet.get_image(i, fw, fh, scale, (0, 0, 0))
            img = pygame.transform.flip(img, self.direction == 1, False)
            img.set_colorkey((0, 0, 0))
            self.animation_list.append(img)

        self.image = self.animation_list[self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(topleft=(x_pos, y))

    def update(self, camera_x, screen_width):
        if pygame.time.get_ticks() - self.update_time > 125:
            self.update_time = pygame.time.get_ticks()
            self.frame_index = (self.frame_index + 1) % len(self.animation_list)
        self.image = self.animation_list[self.frame_index]

        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        self.rect.x += self.direction * 4
        if self.rect.right < camera_x - 400 or self.rect.left > camera_x + screen_width + 400:
            self.kill()


class GargoyleFlyer(pygame.sprite.Sprite):
    def __init__(self, x_pos, y, sheet_img, scale, forced_direction=None):
        super().__init__()
        self.rem_value = 5
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.direction = forced_direction if forced_direction is not None else random.choice([-1, 1])

        sprite_sheet = SpriteSheet(sheet_img)
        fw = sheet_img.get_width() // 10
        fh = sheet_img.get_height()

        for i in range(10):
            img = sprite_sheet.get_image(i, fw, fh, scale, (0, 0, 0))
            img = pygame.transform.flip(img, self.direction == -1, False)
            img.set_colorkey((0, 0, 0))
            self.animation_list.append(img)

        self.image = self.animation_list[self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(topleft=(x_pos, y))

    def update(self, camera_x, screen_width):
        if pygame.time.get_ticks() - self.update_time > 100:
            self.update_time = pygame.time.get_ticks()
            self.frame_index = (self.frame_index + 1) % len(self.animation_list)
        self.image = self.animation_list[self.frame_index]

        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        self.rect.x += self.direction * 4
        if self.rect.right < camera_x - 400 or self.rect.left > camera_x + screen_width + 400:
            self.kill()


class GreyGargoyleFlyer(pygame.sprite.Sprite):
    def __init__(self, x_pos, y, sheet_img, scale, forced_direction=None):
        super().__init__()
        self.rem_value = 5
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.direction = forced_direction if forced_direction is not None else random.choice([-1, 1])

        sprite_sheet = SpriteSheet(sheet_img)
        fw = sheet_img.get_width() // 12
        fh = sheet_img.get_height()

        for i in range(12):
            img = sprite_sheet.get_image(i, fw, fh, scale, (0, 0, 0))
            img = pygame.transform.flip(img, self.direction == -1, False)
            img.set_colorkey((0, 0, 0))
            self.animation_list.append(img)

        self.image = self.animation_list[self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(topleft=(x_pos, y))

    def update(self, camera_x, screen_width):
        if pygame.time.get_ticks() - self.update_time > 100:
            self.update_time = pygame.time.get_ticks()
            self.frame_index = (self.frame_index + 1) % len(self.animation_list)
        self.image = self.animation_list[self.frame_index]

        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        self.rect.x += self.direction * 4
        if self.rect.right < camera_x - 400 or self.rect.left > camera_x + screen_width + 400:
            self.kill()