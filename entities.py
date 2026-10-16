# -entities-#

import pygame
import sys
import math


class SpriteSheet:
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale, colour):
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        image.set_colorkey(colour)
        return image


# ==============================================================================
# --- MID-LEVEL CHECKPOINT SHRINE (THE WEEPING SERAPH STATUE) ---
# ==============================================================================
class CheckpointShrine(pygame.sprite.Sprite):
    def __init__(self, x, y_ground, scale=1.20, y_offset=300):
        super().__init__()
        self.x = x
        self.y_ground = y_ground
        self.scale = scale
        self.y_offset = y_offset

        # Load 4 rows x 7 columns grid sheet (28 frames total)
        try:
            raw_sheet = pygame.image.load("spritesheets/check point/check_point_sheet.png").convert_alpha()
            cols, rows = 7, 4
            sw, sh = raw_sheet.get_size()
            fw, fh = sw // cols, sh // rows
            self.frames = []
            for r in range(rows):
                for c in range(cols):
                    sub = raw_sheet.subsurface((c * fw, r * fh, fw, fh))
                    self.frames.append(pygame.transform.smoothscale(sub, (int(fw * scale), int(fh * scale))))
        except pygame.error as e:
            print(f"Error loading checkpoint shrine sheet: {e}")
            self.frames = [pygame.Surface((120, 180), pygame.SRCALPHA)]

        self.frame_index = 0
        self.activated = False
        self.update_time = pygame.time.get_ticks()
        self.anim_speed = 70  # ms per frame

        self.image = self.frames[0]
        # Pushed down by y_offset so the stone pedestal firmly touches the walking surface
        self.rect = self.image.get_rect(midbottom=(self.x, self.y_ground + self.y_offset))

        try:
            self.fx = pygame.mixer.Sound("mats/audio/check_point.mp3")
            self.fx.set_volume(0.40)
        except pygame.error:
            self.fx = None

    def trigger(self):
        """Activates the shrine when Succi crosses its coordinates."""
        if not self.activated:
            self.activated = True
            self.frame_index = 1
            self.update_time = pygame.time.get_ticks()
            if self.fx:
                try:
                    self.fx.play()
                except Exception:
                    pass

    def update(self, dt_ms):
        if not self.activated:
            # Stays as sleeping weeping stone statue (Frame 0)
            self.image = self.frames[0]
        else:
            # Awakening animation sequence
            now = pygame.time.get_ticks()
            if now - self.update_time > self.anim_speed:
                self.update_time = now
                if self.frame_index < 22:
                    # Sequential stand-up and ignite animation (Frames 1 to 21)
                    self.frame_index += 1
                else:
                    # Loop the last 6 frames continuously on purple fire (Frames 22 to 27)
                    self.frame_index = 22 + ((self.frame_index - 22 + 1) % 6)

            self.image = self.frames[min(self.frame_index, len(self.frames) - 1)]

        # Lock the pedestal base firmly to the floor across all frames
        old_midbottom = self.rect.midbottom
        self.rect = self.image.get_rect()
        self.rect.midbottom = old_midbottom

    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, fireball_img, explode_img, fly_scale=0.45, exp_scale=0.45, exp_offset=0,
                 damage=1, dir_y=0.0):
        super().__init__()
        self.direction = direction
        self.dir_y = dir_y
        self.speed = 800.0
        self.state = "fly"
        self.frame_index, self.update_time = 0, pygame.time.get_ticks()

        self.exp_offset = exp_offset
        self.damage = damage

        rotation_angle = 0
        if dir_y < 0:
            rotation_angle = 35 if direction == 1 else -35
        elif dir_y > 0:
            rotation_angle = -35 if direction == 1 else 35

        fw, fh = fireball_img.get_width() // 6, fireball_img.get_height()
        raw_fly_frames = [
            pygame.transform.flip(
                pygame.transform.smoothscale(
                    fireball_img.subsurface((i * fw, 0, fw, fh)),
                    (int(fw * fly_scale), int(fh * fly_scale))
                ), direction == -1, False
            ) for i in range(6)
        ]

        if rotation_angle != 0:
            self.fly_frames = [pygame.transform.rotate(f, rotation_angle) for f in raw_fly_frames]
        else:
            self.fly_frames = raw_fly_frames

        ew, eh = explode_img.get_width() // 8, explode_img.get_height()
        self.exp_frames = [
            pygame.transform.flip(
                pygame.transform.smoothscale(
                    explode_img.subsurface((i * ew, 0, ew, eh)),
                    (int(ew * exp_scale), int(eh * exp_scale))
                ), direction == -1, False
            ) for i in range(8)
        ]

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
            norm_x = 0.707 if self.dir_y != 0 else 1.0
            norm_y = 0.707 if self.dir_y != 0 else 0.0

            self.rect.x += self.direction * self.speed * norm_x * dt
            self.rect.y += self.dir_y * self.speed * norm_y * dt

            if getattr(self, "last_image", None) != self.image:
                self.mask = pygame.mask.from_surface(self.image)
                self.last_image = self.image

            if self.rect.right < camera_x - 500 or self.rect.left > camera_x + screen_width + 500 or self.rect.bottom < -200 or self.rect.top > 1000:
                self.kill()

    def explode(self):
        if self.state != "explode":
            self.state, self.frame_index, self.update_time = "explode", 0, pygame.time.get_ticks()
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
    def __init__(self, screen_width, screen_height, sheet_filename, columns=7, rows=4, target_duration=9600):
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


class Companion(pygame.sprite.Sprite):
    def __init__(self, frames, anim_speed=70):
        super().__init__()
        self.frames = frames
        self.anim_speed = anim_speed
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()

    def update(self, target_x, target_y, target_facing_right, is_flying=False):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.anim_speed:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.last_update = current_time

        self.image = self.frames[self.frame_index]

        if not target_facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        offset_x = -160 if target_facing_right else 160
        offset_y = -135 if is_flying else -265

        self.rect.centerx = target_x + offset_x
        self.rect.centery = target_y + offset_y

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)


# ==============================================================================
# --- ADJUST LOOT PILE & ABSORPTION HAND SCALE HERE ---
# Increase to 0.35 or 0.40 if you want an even bigger treasure presence!
# ==============================================================================
LOOT_DEFAULT_SCALE = 0.32


# ==============================================================================
# --- ENEMY DEATH VOID SLIT VFX ---
# ==============================================================================
class DeathSlit(pygame.sprite.Sprite):
    cached_scale = None
    cached_frames = None

    def __init__(self, x, y, y_ground, rem_value, sheet_img, fx, loot_pile_sheet, loot_hand_sheet, loot_pile_fx,
                 loot_hand_fx, scale=0.35):
        super().__init__()
        self.x = x
        self.y = y
        self.y_ground = y_ground
        self.rem_value = rem_value
        self.fx = fx
        self.loot_pile_sheet = loot_pile_sheet
        self.loot_hand_sheet = loot_hand_sheet
        self.loot_pile_fx = loot_pile_fx
        self.loot_hand_fx = loot_hand_fx
        self.scale = scale

        # Class-level cache: slice and scale ONCE, never re-process on enemy death!
        if DeathSlit.cached_frames is None or DeathSlit.cached_scale != scale:
            DeathSlit.cached_scale = scale
            cols, rows = 8, 2
            sw, sh = sheet_img.get_size()
            fw, fh = sw // cols, sh // rows
            all_frames = []
            for r in range(rows):
                for c in range(cols):
                    frame = pygame.Surface((fw, fh), pygame.SRCALPHA)
                    frame.blit(sheet_img, (0, 0), (c * fw, r * fh, fw, fh))
                    scaled = pygame.transform.smoothscale(frame, (int(fw * scale), int(fh * scale)))
                    all_frames.append(scaled)
            # Only play the first 11 high-impact frames (drops the empty/invisible tail)
            DeathSlit.cached_frames = all_frames[:11]

        self.frames = DeathSlit.cached_frames
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.anim_speed = 75  # 40ms per frame (~0.44s total) for an instant, responsive snap: changed to 75 cause 44 was too quick of an animation
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))

        if self.fx:
            try:
                self.fx.set_volume(0.35)
                self.fx.play()
            except Exception:
                pass

    def update(self, dt, camera_x, loot_group):
        now = pygame.time.get_ticks()
        if now - self.update_time > self.anim_speed:
            self.update_time = now
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                # When slit snaps shut, spawn RemLoot at the exact same center position
                if loot_group is not None:
                    loot_group.add(RemLoot(
                        self.rect.centerx, self.rect.centery, self.y_ground, self.rem_value,
                        self.loot_pile_sheet, self.loot_hand_sheet,
                        self.loot_pile_fx, self.loot_hand_fx
                    ))
                self.kill()
                return

        self.image = self.frames[min(self.frame_index, len(self.frames) - 1)]

    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))


# ==============================================================================
# --- GROUND REM LOOT PILE & ABSORPTION HAND ---
# ==============================================================================
class RemLoot(pygame.sprite.Sprite):
    cached_scale = None
    cached_idle_frames = None
    cached_absorb_left = None
    cached_absorb_right = None

    def __init__(self, x, y, y_ground, rem_value, idle_sheet_img, absorb_sheet_img, land_fx, absorb_fx,
                 scale=LOOT_DEFAULT_SCALE):
        super().__init__()
        self.world_x = float(x)
        self.world_y = float(y)
        self.y_ground = float(y_ground)
        self.rem_value = rem_value
        self.land_fx = land_fx
        self.absorb_fx = absorb_fx
        self.scale = scale

        # State Machine: "drop" -> "idle" -> "absorb"
        self.state = "drop"
        self.vy = 40.0
        self.reach_left = True
        self.spawn_time = pygame.time.get_ticks()
        self.lifespan = 8500  # 8.5 seconds before despawning

        # Class-level cache: slice and scale ONCE, eliminating in-game freeze lag!
        if RemLoot.cached_idle_frames is None or RemLoot.cached_scale != scale:
            RemLoot.cached_scale = scale

            # Load 18 frames idle (9 cols x 2 rows)
            i_cols, i_rows = 9, 2
            sw_i, sh_i = idle_sheet_img.get_size()
            fw_i, fh_i = sw_i // i_cols, sh_i // i_rows
            RemLoot.cached_idle_frames = []
            for r in range(i_rows):
                for c in range(i_cols):
                    frame = pygame.Surface((fw_i, fh_i), pygame.SRCALPHA)
                    frame.blit(idle_sheet_img, (0, 0), (c * fw_i, r * fh_i, fw_i, fh_i))
                    RemLoot.cached_idle_frames.append(
                        pygame.transform.smoothscale(frame, (int(fw_i * scale), int(fh_i * scale))))

            # Load 28 frames absorb (7 cols x 4 rows)
            a_cols, a_rows = 7, 4
            sw_a, sh_a = absorb_sheet_img.get_size()
            fw_a, fh_a = sw_a // a_cols, sh_a // a_rows
            RemLoot.cached_absorb_left = []
            RemLoot.cached_absorb_right = []
            for r in range(a_rows):
                for c in range(a_cols):
                    frame = pygame.Surface((fw_a, fh_a), pygame.SRCALPHA)
                    frame.blit(absorb_sheet_img, (0, 0), (c * fw_a, r * fh_a, fw_a, fh_a))
                    scaled = pygame.transform.smoothscale(frame, (int(fw_a * scale), int(fh_a * scale)))
                    RemLoot.cached_absorb_left.append(scaled)
                    RemLoot.cached_absorb_right.append(pygame.transform.flip(scaled, True, False))

        self.idle_frames = RemLoot.cached_idle_frames
        self.absorb_frames_left = RemLoot.cached_absorb_left
        self.absorb_frames_right = RemLoot.cached_absorb_right

        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect(center=(int(self.world_x), int(self.world_y)))

    def update(self, dt, camera_x, succi, platform_group):
        now = pygame.time.get_ticks()
        earned_rem = 0

        # State 1: Drop to Floor with Gravity (Starting at the exact center of the death slit)
        if self.state == "drop":
            self.vy += 800.0 * dt
            self.world_y += self.vy * dt

            # Distance from canvas center (540) to visible pile bottom (741) is 201px.
            # This lands the base of the treasure directly onto the stone floor tiles!
            target_floor_center = self.y_ground + 20 - int(201 * self.scale)
            if self.world_y >= target_floor_center:
                self.world_y = target_floor_center
                self.vy = 0.0
                self.state = "idle"
                self.frame_index = 0
                self.update_time = now
                if self.land_fx:
                    try:
                        self.land_fx.set_volume(0.25)
                        self.land_fx.play()
                    except Exception:
                        pass

        # State 2: Idle Sparkling Loop on Floor
        elif self.state == "idle":
            # Cycle 18 idle frames (~110ms per frame)
            if now - self.update_time > 110:
                self.update_time = now
                self.frame_index = (self.frame_index + 1) % len(self.idle_frames)

            # Despawn / Decay check (8.5 seconds)
            elapsed = now - self.spawn_time
            if elapsed > self.lifespan:
                self.kill()
                return 0

            # Proximity check to Succi's actual body center (succi.rect)
            dist_x = abs(succi.rect.centerx - self.rect.centerx)
            dist_y = abs(succi.rect.centery - self.rect.centery)
            if dist_x < 170 and dist_y < 160:
                # Lock direction toward Succi on pickup trigger
                self.reach_left = (succi.rect.centerx < self.rect.centerx)
                self.state = "absorb"
                self.frame_index = 0
                self.update_time = now
                if self.absorb_fx:
                    try:
                        self.absorb_fx.set_volume(0.35)
                        self.absorb_fx.play()
                    except Exception:
                        pass

        # State 3: Rapid Hand Siphon Absorption into Succi
        elif self.state == "absorb":
            # Dynamically tracks Succi during reach-out phase so it never reaches away if she runs past
            if self.frame_index < 14:
                self.reach_left = (succi.rect.centerx < self.rect.centerx)

            # High-speed 20ms cadence (~0.56s total for 28 frames) for an explosive mana siphon
            if now - self.update_time > 20:
                self.update_time = now
                self.frame_index += 1
                if self.frame_index >= len(self.absorb_frames_left):
                    # Award REM on the final frame when completely siphoned!
                    earned_rem = self.rem_value
                    self.kill()
                    return earned_rem

        # Set Current Frame Image
        if self.state in ["drop", "idle"]:
            self.image = self.idle_frames[self.frame_index % len(self.idle_frames)]
            # Rapid blink during final 2 seconds before despawn
            if self.state == "idle" and (now - self.spawn_time) > 6500:
                if (now // 100) % 2 == 0:
                    self.image = pygame.Surface((0, 0))
        else:
            frames = self.absorb_frames_left if self.reach_left else self.absorb_frames_right
            self.image = frames[min(self.frame_index, len(frames) - 1)]

        # Consistently anchor by center throughout all animation states
        if self.image.get_width() > 0:
            self.rect = self.image.get_rect(center=(int(self.world_x), int(self.world_y)))

        return earned_rem

    def draw(self, screen, camera_x):
        if self.image.get_width() > 0:
            screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))


# ==============================================================================
# --- GARGOYLE AERIAL CELESTIAL REM COIN ---
# ==============================================================================
class RemCoin(pygame.sprite.Sprite):
    cached_scale = None
    cached_frames = None

    def __init__(self, x, y, rem_value, sheet_img, scale=0.18):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.rem_value = rem_value
        self.scale = scale
        self.bob_timer = 0.0

        # Class-level cache: slice and scale ONCE, zero runtime lag on gargoyle kill
        if RemCoin.cached_frames is None or RemCoin.cached_scale != scale:
            RemCoin.cached_scale = scale
            cols, rows = 8, 2
            sw, sh = sheet_img.get_size()
            fw, fh = sw // cols, sh // rows
            RemCoin.cached_frames = []
            for r in range(rows):
                for c in range(cols):
                    frame = pygame.Surface((fw, fh), pygame.SRCALPHA)
                    frame.blit(sheet_img, (0, 0), (c * fw, r * fh, fw, fh))
                    RemCoin.cached_frames.append(
                        pygame.transform.smoothscale(frame, (int(fw * scale), int(fh * scale))))

        self.frames = RemCoin.cached_frames
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.spawn_time = pygame.time.get_ticks()
        self.lifespan = 8500  # 8.5 seconds lifespan (matching ground loot)
        self.anim_speed = 80  # 16 frames * 80ms = 1.28s per rotation
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self, dt, camera_x, succi):
        now = pygame.time.get_ticks()
        earned_rem = 0

        # Despawn / Decay check (8.5 seconds total)
        elapsed = now - self.spawn_time
        if elapsed > self.lifespan:
            self.kill()
            return 0

        # Smooth 360-degree rotation animation
        if now - self.update_time > self.anim_speed:
            self.update_time = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        # Rapid blink during final 2 seconds before de-spawn
        if elapsed > 6500 and (now // 100) % 2 == 0:
            self.image = pygame.Surface((0, 0))
        else:
            self.image = self.frames[self.frame_index]

        # Gentle floating hover bob
        self.bob_timer += dt * 3.5
        self.rect.centery = int(self.y + math.sin(self.bob_timer) * 6.0)

        # Full-body collision pickup check (300ms delay ensures coin visibly appears first)
        if now - self.spawn_time > 300:
            coin_hitbox = self.rect.inflate(-65, -110)
            succi_body = succi.rect.inflate(-110, -20)
            if coin_hitbox.colliderect(succi_body):
                earned_rem = self.rem_value
                self.kill()

        return earned_rem

    def draw(self, screen, camera_x):
        if self.image.get_width() > 0:
            screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))