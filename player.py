# Succi Player Class
import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, animations, animation_speeds, scale_corrections, jump_fx, cast_fx):
        super().__init__()

        # Physics & Positioning
        self.x = x
        self.y_ground = y
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.speed_walk = 180.0
        self.speed_run = 320.0
        self.jump_impulse = -800.0
        self.gravity = 1500.0
        self.on_ground = True
        self.facing_right = True

        # Health System (Starts at 1 hit = death, upgrades to 3 later)
        self.health = 1
        self.max_health = 1
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
        self.current_spell_type = "normal"

        # Assets & Animations
        self.animations = animations
        self.anim_speeds = animation_speeds
        self.scale_corrections = scale_corrections
        self.jump_fx = jump_fx
        self.cast_fx = cast_fx

        # Collision Mask setup based on starting frame
        self.image = self.animations[self.current_anim][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()

    def handle_input(self, keys):
        moving = False
        run_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        duck_pressed = keys[pygame.K_DOWN] or keys[pygame.K_s]  # Now supports 'S' key

        self.recovering_duck = (self.current_anim == "duck" and not duck_pressed and self.playing)
        self.attacking = (self.current_anim in ["attack", "run_attack"] and self.playing)

        # Horizontal Movement Intent (Now supports A and D)
        if self.current_anim == "attack" or self.recovering_duck or (duck_pressed and self.on_ground):
            self.vx = 0
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.facing_right = False
            moving = True
            self.vx = - (self.speed_run if run_pressed else self.speed_walk)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.facing_right = True
            moving = True
            self.vx = (self.speed_run if run_pressed else self.speed_walk)
        else:
            self.vx = 0

        # Jump Intent
        if keys[pygame.K_SPACE] and self.on_ground and not duck_pressed and not self.recovering_duck and not self.attacking:
            if moving and "run_jump" in self.animations:
                self.current_anim = "run_jump"
            else:
                self.current_anim = "jump"
            self.current_frame = 0
            self.animation_timer = 0
            self.playing = True
            self.vy = self.jump_impulse
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
            self.vy += self.gravity * dt
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
        delay = self.anim_speeds.get(self.current_anim, 120)
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
        if pygame.time.get_ticks() - self.invulnerable_timer < 1000:
            return False  # Still invincible from last hit

        self.health -= 1
        self.invulnerable_timer = pygame.time.get_ticks()

        if self.health <= 0:
            return True
        return False

    def update(self, keys, dt, dt_ms, platform_group, loops_dict):
        moving, run_pressed, duck_pressed = self.handle_input(keys)
        self.duck_pressed = duck_pressed
        self.update_physics(dt, platform_group)
        self.update_animation_state(moving, run_pressed, duck_pressed)
        self.advance_frame(dt_ms, loops_dict)

    def draw(self, screen, camera_x):
        frame_surf = self.animations[self.current_anim][self.current_frame]
        display_w, display_h = frame_surf.get_size()

        base_scale_factor = 0.25
        correction = self.scale_corrections.get(self.current_anim, 1.0)
        final_scale = base_scale_factor * correction

        frame_to_draw = pygame.transform.smoothscale(frame_surf,
                                                     (int(display_w * final_scale), int(display_h * final_scale)))

        if not self.facing_right:
            frame_to_draw = pygame.transform.flip(frame_to_draw, True, False)

        fw, fh = frame_to_draw.get_size()
        screen_x = self.x - camera_x
        blit_x = int(screen_x - fw // 2)

        y_offset = 0
        x_offset = 0
        if self.current_anim == "attack":
            y_offset = 230
            shift_amount = 200
            if self.facing_right:
                x_offset = shift_amount
            else:
                x_offset = -shift_amount

        blit_x += x_offset
        blit_y = int(self.y - fh) + y_offset

        self.mask = pygame.mask.from_surface(frame_to_draw)
        self.rect = frame_to_draw.get_rect(topleft=(blit_x, blit_y))

        # Flicker effect if invulnerable
        if pygame.time.get_ticks() - self.invulnerable_timer < 1000:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                return blit_x, blit_y  # Skip rendering to blink

        screen.blit(frame_to_draw, (blit_x, blit_y))
        return blit_x, blit_y