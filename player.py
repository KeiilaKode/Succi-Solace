# Succi Player Class
import pygame
import config


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, animations, animation_speeds, scale_corrections, jump_fx, cast_fx):
        super().__init__()

        # Physics & Positioning
        self.x = x
        self.y_ground = y
        self.y = y
        self.vx = 0.0
        self.vy = 0.0

        self.on_ground = True
        self.facing_right = True

        # Health System
        self.health = config.PLAYER_STARTING_HEALTH
        self.max_health = config.PLAYER_STARTING_HEALTH
        self.invulnerable_timer = 0

        # State Management
        self.current_anim = "idle"
        self.current_frame = 0
        self.animation_timer = 0
        self.playing = True
        self.fireball_spawned = False
        self.attacking = False
        self.recovering_duck = False
        self.duck_pressed = False

        # Dual-Wield Spell Inventory Hooks
        self.spell_left_click = "normal"
        self.spell_right_click = None

        # Assets & Animations
        self.animations = animations
        self.anim_speeds = animation_speeds
        self.scale_corrections = scale_corrections
        self.jump_fx = jump_fx
        self.cast_fx = cast_fx

        # Collision Mask setup
        self.current_image = self.animations[self.current_anim][0]
        self.mask = pygame.mask.from_surface(self.current_image)
        self.rect = self.current_image.get_rect()

    def handle_input(self, keys):
        moving = False
        run_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        duck_pressed = keys[pygame.K_DOWN] or keys[pygame.K_s]

        self.recovering_duck = (self.current_anim == "duck" and not duck_pressed and self.playing)
        self.attacking = (self.current_anim in ["attack", "run_attack"] and self.playing)

        # Horizontal Movement Intent
        if self.current_anim == "attack" or self.recovering_duck or (duck_pressed and self.on_ground):
            self.vx = 0
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.facing_right = False
            moving = True
            self.vx = - (config.PLAYER_SPEED_RUN if run_pressed else config.PLAYER_SPEED_WALK)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.facing_right = True
            moving = True
            self.vx = (config.PLAYER_SPEED_RUN if run_pressed else config.PLAYER_SPEED_WALK)
        else:
            self.vx = 0

        # Jump Intent
        if keys[
            pygame.K_SPACE] and self.on_ground and not duck_pressed and not self.recovering_duck and not self.attacking:
            if moving and "run_jump" in self.animations:
                self.current_anim = "run_jump"
            else:
                self.current_anim = "jump"
            self.current_frame = 0
            self.animation_timer = 0
            self.playing = True
            self.vy = config.PLAYER_JUMP_IMPULSE
            self.on_ground = False
            if self.jump_fx:
                self.jump_fx.play()

        return moving, run_pressed, duck_pressed

    def trigger_attack(self, run_pressed, moving):
        """Triggered externally by mouse clicks in main.py"""
        if not getattr(self, 'duck_pressed', False) and not self.recovering_duck:
            if not self.attacking:
                if (moving and run_pressed) or not self.on_ground:
                    self.current_anim = "run_attack"
                else:
                    self.current_anim = "attack"

                self.current_frame = 0
                self.animation_timer = 0
                self.playing = True
                self.fireball_spawned = False
                self.attacking = True

    def update_physics(self, dt, platform_group):
        self.x += self.vx * dt

        if not self.on_ground:
            self.vy += config.PLAYER_GRAVITY * dt
            self.y += self.vy * dt

            for platform in platform_group:
                col_rect = getattr(platform, 'collision_rect', platform.rect)
                if self.vy > 0 and col_rect.colliderect(self.x - 20, self.y - 5, 40, 10):
                    if self.y - self.vy * dt <= col_rect.top + 10:
                        self.y = col_rect.top
                        self.vy = 0
                        self.on_ground = True
                        break

            if self.y >= self.y_ground:
                self.y = self.y_ground
                self.vy = 0
                self.on_ground = True
        else:
            on_platform = False
            for platform in platform_group:
                col_rect = getattr(platform, 'collision_rect', platform.rect)
                if col_rect.colliderect(self.x - 20, self.y, 40, 5):
                    on_platform = True
                    break
            if not on_platform and self.y < self.y_ground:
                self.on_ground = False

    def update_animation_state(self, moving, run_pressed, duck_pressed):
        if self.attacking or not self.on_ground or self.recovering_duck:
            pass
        elif duck_pressed:
            if self.current_anim != "duck":
                self.current_anim = "duck"
                self.current_frame = 0
                self.animation_timer = 0
                self.playing = True
        elif moving:
            if run_pressed and "run" in self.animations:
                if self.current_anim != "run":
                    self.current_anim = "run"
                    self.current_frame = 0
                    self.animation_timer = 0
                    self.playing = True
            else:
                if "walk" in self.animations and self.current_anim != "walk":
                    self.current_anim = "walk"
                    self.current_frame = 0
                    self.animation_timer = 0
                    self.playing = True
        else:
            if "idle" in self.animations and self.current_anim != "idle":
                self.current_anim = "idle"
                self.current_frame = 0
                self.animation_timer = 0
                self.playing = True

    def advance_frame(self, dt_ms, loops_dict):
        anim_frames = self.animations[self.current_anim]
        delay = self.anim_speeds.get(self.current_anim, config.DEFAULT_ANIM_DELAY)
        loop = loops_dict.get(self.current_anim, True)
        self.animation_timer += dt_ms

        if self.current_anim == "duck" and getattr(self, 'duck_pressed', False):
            if self.current_frame >= 6:
                self.current_frame = 6
                self.animation_timer = 0
        if self.current_anim == "jump" and not self.on_ground:
            if self.current_frame >= 5:
                self.current_frame = 5
                self.animation_timer = 0
        if self.current_anim == "run_jump" and not self.on_ground:
            if self.current_frame >= 9:
                self.current_frame = 9
                self.animation_timer = 0

        if loop:
            if self.animation_timer >= delay:
                steps = self.animation_timer // delay
                self.animation_timer = self.animation_timer % delay
                self.current_frame = (self.current_frame + int(steps)) % max(1, len(anim_frames))
        else:
            if self.animation_timer >= delay and self.playing:
                steps = self.animation_timer // delay
                self.animation_timer = self.animation_timer % delay
                self.current_frame += int(steps)
                if self.current_frame >= len(anim_frames) - 1:
                    self.current_frame = len(anim_frames) - 1
                    self.playing = False

    def take_damage(self):
        """Returns True if the player dies, False if they survive."""
        if pygame.time.get_ticks() - self.invulnerable_timer < config.PLAYER_INVULNERABLE_DURATION:
            return False  # Still invincible from last hit

        self.health -= 1
        self.invulnerable_timer = pygame.time.get_ticks()

        if self.health <= 0:
            return True
        return False

    def prepare_frame(self):
        """Calculates scaling, flipping, and collision masks before drawing."""
        frame_surf = self.animations[self.current_anim][self.current_frame]
        display_w, display_h = frame_surf.get_size()

        correction = self.scale_corrections.get(self.current_anim, 1.0)
        final_scale = config.PLAYER_BASE_SCALE * correction

        self.current_image = pygame.transform.smoothscale(
            frame_surf, (int(display_w * final_scale), int(display_h * final_scale))
        )

        if not self.facing_right:
            self.current_image = pygame.transform.flip(self.current_image, True, False)

        fw, fh = self.current_image.get_size()

        y_offset = config.PLAYER_ATTACK_Y_OFFSET if self.current_anim == "attack" else 0
        x_offset = 0
        if self.current_anim == "attack":
            x_offset = config.PLAYER_ATTACK_X_SHIFT if self.facing_right else -config.PLAYER_ATTACK_X_SHIFT

        world_x = int(self.x - fw // 2) + x_offset
        world_y = int(self.y - fh) + y_offset

        self.rect = self.current_image.get_rect(topleft=(world_x, world_y))
        self.mask = pygame.mask.from_surface(self.current_image)

    def update(self, keys, dt, dt_ms, platform_group, loops_dict):
        moving, run_pressed, duck_pressed = self.handle_input(keys)
        self.duck_pressed = duck_pressed
        self.update_physics(dt, platform_group)
        self.update_animation_state(moving, run_pressed, duck_pressed)
        self.advance_frame(dt_ms, loops_dict)
        self.prepare_frame()

    def draw(self, screen, camera_x):
        # Flicker effect if invulnerable
        if pygame.time.get_ticks() - self.invulnerable_timer < config.PLAYER_INVULNERABLE_DURATION:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                return self.rect.x - camera_x, self.rect.y  # Skip rendering to blink

        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y

        screen.blit(self.current_image, (screen_x, screen_y))
        return screen_x, screen_y