import pygame
import random
import sys


class SpriteSheet:
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale, colour):
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        image.set_colorkey(colour)
        return image


# ==========================================
# MASTER ENEMY CLASSES
# ==========================================

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                 health, rem_value, speed, anim_speed, y_offset=160):
        super().__init__()
        self.health = health
        self.rem_value = rem_value
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l

        self.frame_index, self.update_time = 0, pygame.time.get_ticks()
        self.anim_speed = anim_speed
        self.patrol_start_x, self.patrol_end_x = patrol_start_x, patrol_end_x
        self.speed, self.direction, self.state = speed, 1, "walk"

        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.rect.bottom = y_pos + y_offset
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def update(self, camera_x, player_x=None, player_y=None):
        # Aggro Logic
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 320 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1

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
                 health, rem_value, speed, anim_speed, y_offset=160):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health, rem_value, speed, anim_speed, y_offset)
        self.idle_frames_right = idle_r
        self.idle_frames_left = idle_l

    def update(self, camera_x, player_x=None, player_y=None):
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 300 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1

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
# SPECIFIC ENEMIES (Refactored)
# ==========================================

class Demon(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=1, rem_value=5, speed=2.0, anim_speed=100, y_offset=85)


class Helldog(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=2, rem_value=10, speed=3.5, anim_speed=80)


class Mau(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=3, rem_value=12, speed=2.0, anim_speed=100)


class Pkgrim(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=2, rem_value=8, speed=2.5, anim_speed=90)


class Azule(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=3, rem_value=12, speed=2.2, anim_speed=90)


class Titus(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=4, rem_value=15, speed=1.8, anim_speed=100)


class Lionel(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=4, rem_value=15, speed=2.5, anim_speed=90)


class Elaine(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=5, rem_value=18, speed=2.5, anim_speed=90)


class RoyalHH(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=4, rem_value=15, speed=3.8, anim_speed=80)


class RoyalZombie(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=5, rem_value=18, speed=2.0, anim_speed=100)


class Zombie1(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=3, rem_value=10, speed=1.9, anim_speed=100)


class Zombie2(BaseEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l,
                         health=3, rem_value=12, speed=2.1, anim_speed=100)


# ==========================================
# IDLE ENEMIES (Refactored)
# ==========================================

class Skeleton(BaseIdleEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r,
                 attack_l):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r,
                         attack_l,
                         health=1, rem_value=5, speed=1.8, anim_speed=100, y_offset=240)


class Demented(BaseIdleEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r,
                 attack_l):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r,
                         attack_l,
                         health=3, rem_value=12, speed=1.8, anim_speed=100)


class Groundskeeper(BaseIdleEnemy):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r,
                 attack_l):
        super().__init__(spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r,
                         attack_l,
                         health=4, rem_value=15, speed=1.8, anim_speed=100)


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


class Projectile(pygame.sprite.Sprite):
    # --- ADDED exp_offset=0 HERE ---
    def __init__(self, x, y, direction, fireball_img, explode_img, fly_scale=0.45, exp_scale=0.45, exp_offset=0):
        super().__init__()
        self.direction, self.speed, self.state = direction, 800.0, "fly"
        self.frame_index, self.update_time = 0, pygame.time.get_ticks()

        # Save the offset to use later
        self.exp_offset = exp_offset

        fw, fh = fireball_img.get_width() // 6, fireball_img.get_height()
        self.fly_frames = [pygame.transform.flip(
            pygame.transform.smoothscale(fireball_img.subsurface((i * fw, 0, fw, fh)),
                                         (int(fw * fly_scale), int(fh * fly_scale))), direction == -1, False) for i in
            range(6)]

        ew, eh = explode_img.get_width() // 8, explode_img.get_height()
        self.exp_frames = [pygame.transform.flip(
            pygame.transform.smoothscale(explode_img.subsurface((i * ew, 0, ew, eh)),
                                         (int(ew * exp_scale), int(eh * exp_scale))),
            direction == -1, False) for i in range(8)]

        self.image = self.fly_frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt, camera_x, screen_width):
        if pygame.time.get_ticks() - self.update_time > (50 if self.state == "fly" else 40):
            self.update_time, self.frame_index = pygame.time.get_ticks(), self.frame_index + 1

            old_center = self.rect.center

            if self.state == "fly":
                self.frame_index %= len(self.fly_frames)
                self.image = self.fly_frames[self.frame_index]
            else:
                if self.frame_index >= len(self.exp_frames):
                    self.kill()
                    return
                self.image = self.exp_frames[self.frame_index]

            self.rect = self.image.get_rect(center=old_center)

        if self.state == "fly":
            self.rect.x += self.direction * self.speed * dt
            if getattr(self, "last_image", None) != self.image:
                self.mask = pygame.mask.from_surface(self.image)
                self.last_image = self.image

            if self.rect.right < camera_x - 500 or self.rect.left > camera_x + screen_width + 500:
                self.kill()

    def explode(self):
        if self.state != "explode":
            self.state, self.frame_index, self.update_time = "explode", 0, pygame.time.get_ticks()

            # --- USE THE CUSTOM OFFSET HERE ---
            self.rect.x += self.direction * self.exp_offset


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, platform_image, offset_ratio=0.0):
        super().__init__()
        orig_w, orig_h = platform_image.get_size()
        scale = width / orig_w
        height = int(orig_h * scale)
        self.image = pygame.transform.smoothscale(platform_image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        top_offset = int(height * offset_ratio)
        self.collision_rect = pygame.Rect(self.rect.x, self.rect.y + top_offset, self.rect.width, 10)


class Merchant(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height, sheet_filename, columns=7, rows=4, target_duration=10000):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height

        try:
            sheet = pygame.image.load(sheet_filename).convert()
        except pygame.error as e:
            print(f"Unable to load merchant sprite sheet: {e}")
            sys.exit()

        sw, sh = sheet.get_size()
        fw = sw // columns
        fh = sh // rows

        self.intro_frames = []
        scale_factor = screen_width / fw
        new_h = int(fh * scale_factor)

        for row in range(rows):
            for col in range(columns):
                frame = pygame.Surface((fw, fh)).convert()
                frame.blit(sheet, (0, 0), (col * fw, row * fh, fw, fh))
                scaled_frame = pygame.transform.smoothscale(frame, (screen_width, new_h))
                self.intro_frames.append(scaled_frame)

        self.frame_index = 0
        self.animation_timer = 0
        self.anim_speed = max(20, int(target_duration / len(self.intro_frames)))
        self.state = "intro"
        self.image = self.intro_frames[0]
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height // 2))
        self.audio_played = False

    def update(self, dt_ms, voice_fx):
        if self.state == "intro":
            if not self.audio_played:
                voice_fx.play()
                self.audio_played = True

            self.animation_timer += dt_ms
            if self.animation_timer >= self.anim_speed:
                self.animation_timer = 0
                self.frame_index += 1

                if self.frame_index >= len(self.intro_frames):
                    self.frame_index = len(self.intro_frames) - 1
                    self.state = "idle"

            self.image = self.intro_frames[self.frame_index]

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)