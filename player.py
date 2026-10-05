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

        # Double Jump Capabilities
        self.has_double_jump = False
        self.can_double_jump = False
        self.jump_key_released = True

        # ======================================================================
        # --- DASH STATE VARIABLES ---
        # ======================================================================
        self.has_dash = False  # Unlocked via Percy's Dash Potion
        self.is_dashing = False  # True while actively bursting forward
        self.dash_timer = 0  # Tracks burst duration remaining
        self.dash_direction = 1  # 1 for right, -1 for left
        self.dash_charges = getattr(config, 'PLAYER_DASH_MAX_CHARGES', 2)
        self.dash_recharge_timer = 0  # Sequential timer for regenerating charges
        self.w_key_released = True  # Requires tapping W, not holding it

        # Ghost Afterimages trail management
        self.dash_ghosts = []  # Active fading ghost surfaces
        self.ghost_spawn_timer = 0  # Timer to drop a ghost every ~35ms
        # ======================================================================

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

        self.enemies_hit = []

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
        space_pressed = keys[pygame.K_SPACE]
        w_pressed = keys[pygame.K_w]

        self.recovering_duck = (self.current_anim == "duck" and not duck_pressed and self.playing)
        self.attacking = (self.current_anim in ["attack", "run_attack", "kick", "jump_kick"] and self.playing)

        # ======================================================================
        # --- DASH ACTIVATION TRIGGER (W KEY) ---
        # ======================================================================
        # Can only activate if unlocked, key was released, charges available, and not ducking
        if w_pressed and self.w_key_released and self.has_dash and not self.is_dashing and self.dash_charges > 0 and not self.recovering_duck and not duck_pressed:
            self.is_dashing = True
            self.dash_timer = getattr(config, 'PLAYER_DASH_DURATION', 180)
            self.dash_charges -= 1
            self.dash_direction = 1 if self.facing_right else -1
            self.ghost_spawn_timer = 0  # Spawn first ghost immediately
            if self.jump_fx:
                try:
                    self.jump_fx.play()  # Play wind whoosh on burst
                except Exception:
                    pass

        # Track W key release so holding W doesn't accidentally consume both dashes
        self.w_key_released = not w_pressed
        # ======================================================================

        # Horizontal Movement Intent (Disabled while actively dashing)
        if self.is_dashing:
            pass  # Velocity locked to dash speed in update_physics()
        elif self.current_anim in ["attack", "kick"] or self.recovering_duck or (duck_pressed and self.on_ground):
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

        # Jump Intent (Ground Jump)
        if space_pressed and self.on_ground and not duck_pressed and not self.recovering_duck and not self.attacking and not self.is_dashing:
            if moving and "run_jump" in self.animations:
                self.current_anim = "run_jump"
            else:
                self.current_anim = "jump"
            self.current_frame = 0
            self.animation_timer = 0
            self.playing = True
            self.vy = config.PLAYER_JUMP_IMPULSE
            self.on_ground = False
            self.can_double_jump = self.has_double_jump
            if self.jump_fx:
                self.jump_fx.play()

        # Double Jump Intent (Mid-Air Leap)
        elif space_pressed and not self.on_ground and self.can_double_jump and self.jump_key_released and not self.attacking and not self.is_dashing:
            if moving and "run_jump" in self.animations:
                self.current_anim = "run_jump"
            else:
                self.current_anim = "jump"
            self.current_frame = 0
            self.animation_timer = 0
            self.playing = True

            # Reset downward velocity instantly for snappy jump feel
            self.vy = getattr(config, 'PLAYER_DOUBLE_JUMP_IMPULSE', config.PLAYER_JUMP_IMPULSE)
            self.can_double_jump = False
            if self.jump_fx:
                self.jump_fx.play()

        self.jump_key_released = not space_pressed

        return moving, run_pressed, duck_pressed

    def trigger_attack(self, run_pressed, moving):
        """Triggered externally by mouse clicks in main.py"""
        if not getattr(self, 'duck_pressed', False) and not self.recovering_duck and not self.is_dashing:
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

    def trigger_kick(self):
        """Triggered externally by middle mouse or '3' key"""
        if not getattr(self, 'duck_pressed', False) and not self.recovering_duck and not self.is_dashing:
            if not self.attacking:
                if self.on_ground:
                    self.current_anim = "kick"
                else:
                    self.current_anim = "jump_kick"

                self.current_frame = 0
                self.animation_timer = 0
                self.playing = True
                self.attacking = True
                self.fireball_spawned = True
                self.enemies_hit.clear()

    def update_physics(self, dt, platform_group):
        # ======================================================================
        # --- DASH PHYSICS & ZERO-GRAVITY LOCK ---
        # ======================================================================
        if self.is_dashing:
            dash_spd = getattr(config, 'PLAYER_DASH_SPEED', 850.0)
            self.vx = self.dash_direction * dash_spd
            self.vy = 0.0  # Freezes gravity so aerial dashes zip perfectly straight!
            self.x += self.vx * dt
            return  # Bypass normal falling gravity while actively dashing
        # ======================================================================

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
                        self.can_double_jump = self.has_double_jump
                        break

            if self.y >= self.y_ground:
                self.y = self.y_ground
                self.vy = 0
                self.on_ground = True
                self.can_double_jump = self.has_double_jump
        else:
            on_platform = False
            for platform in platform_group:
                col_rect = getattr(platform, 'collision_rect', platform.rect)
                if col_rect.colliderect(self.x - 20, self.y, 40, 5):
                    on_platform = True
                    break
            if not on_platform and self.y < self.y_ground:
                self.on_ground = False
                self.can_double_jump = self.has_double_jump

    def update_animation_state(self, moving, run_pressed, duck_pressed):
        if self.is_dashing:
            pass  # Dashes use aerodynamic sprint frame prepared in prepare_frame()
        elif self.attacking or not self.on_ground or self.recovering_duck:
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
        if self.current_anim == "jump_kick" and not self.on_ground:
            if self.current_frame >= 5:
                self.current_frame = 5
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
        # When actively dashing, lock to her dynamic forward-leaning sprint frame
        if self.is_dashing and "run" in self.animations:
            frame_surf = self.animations["run"][3]  # Aerodynamic extended stride frame
            correction = self.scale_corrections.get("run", 1.08)
        else:
            frame_surf = self.animations[self.current_anim][self.current_frame]
            correction = self.scale_corrections.get(self.current_anim, 1.0)

        display_w, display_h = frame_surf.get_size()
        final_scale = config.PLAYER_BASE_SCALE * correction

        self.current_image = pygame.transform.smoothscale(
            frame_surf, (int(display_w * final_scale), int(display_h * final_scale))
        )

        if not self.facing_right:
            self.current_image = pygame.transform.flip(self.current_image, True, False)

        fw, fh = self.current_image.get_size()

        y_offset = 0
        x_offset = 0

        if self.current_anim == "attack":
            y_offset = config.PLAYER_ATTACK_Y_OFFSET
            x_offset = config.PLAYER_ATTACK_X_SHIFT if self.facing_right else -config.PLAYER_ATTACK_X_SHIFT

        elif self.current_anim in ["kick", "jump_kick"]:
            y_offset = 210
            kick_x_shift = 40
            x_offset = kick_x_shift if self.facing_right else -kick_x_shift

        world_x = int(self.x - fw // 2) + x_offset
        world_y = int(self.y - fh) + y_offset

        self.rect = self.current_image.get_rect(topleft=(world_x, world_y))
        self.mask = pygame.mask.from_surface(self.current_image)

    def spawn_dash_ghost(self):
        """Generates a tinted, translucent afterimage ghost at her current position."""
        if not self.current_image:
            return

        ghost_surf = self.current_image.copy()

        # Colorize the silhouette with a vibrant violet/purple soul wash
        tint_overlay = pygame.Surface(ghost_surf.get_size(), pygame.SRCALPHA)
        tint_overlay.fill((175, 45, 225, 255))  # Rich neon purple
        ghost_surf.blit(tint_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        self.dash_ghosts.append({
            "image": ghost_surf,
            "x": self.rect.x,
            "y": self.rect.y,
            "alpha": 180.0  # Starting opacity (dissolves to 0)
        })

    def update(self, keys, dt, dt_ms, platform_group, loops_dict):
        # 1. Update Dash Burst Duration
        if self.is_dashing:
            self.dash_timer -= dt_ms

            # Spawn afterimage ghosts every 35 milliseconds
            self.ghost_spawn_timer += dt_ms
            if self.ghost_spawn_timer >= 35:
                self.spawn_dash_ghost()
                self.ghost_spawn_timer = 0

            if self.dash_timer <= 0:
                self.is_dashing = False

        # 2. Independent Sequential Recharge Logic for Dash Charges
        max_c = getattr(config, 'PLAYER_DASH_MAX_CHARGES', 2)
        rech_time = getattr(config, 'PLAYER_DASH_RECHARGE_TIME', 2000)
        if self.dash_charges < max_c:
            self.dash_recharge_timer += dt_ms
            if self.dash_recharge_timer >= rech_time:
                self.dash_charges += 1
                self.dash_recharge_timer = 0
        else:
            self.dash_recharge_timer = 0

        # 3. Update Fading Ghost Afterimages
        for ghost in self.dash_ghosts[:]:
            ghost["alpha"] -= 850.0 * dt  # Fades out over approx 200ms
            if ghost["alpha"] <= 0:
                self.dash_ghosts.remove(ghost)

        # Standard state updates
        moving, run_pressed, duck_pressed = self.handle_input(keys)
        self.duck_pressed = duck_pressed
        self.update_physics(dt, platform_group)
        self.update_animation_state(moving, run_pressed, duck_pressed)
        self.advance_frame(dt_ms, loops_dict)
        self.prepare_frame()

    def draw(self, screen, camera_x):
        # 1. Render all active purple ghost afterimages behind Succi
        for ghost in self.dash_ghosts:
            ghost_surf = ghost["image"].copy()
            ghost_surf.set_alpha(max(0, min(255, int(ghost["alpha"]))))
            screen.blit(ghost_surf, (ghost["x"] - camera_x, ghost["y"]))

        # 2. Flicker effect if invulnerable
        if pygame.time.get_ticks() - self.invulnerable_timer < config.PLAYER_INVULNERABLE_DURATION:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                return self.rect.x - camera_x, self.rect.y  # Skip rendering to blink

        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y

        # 3. Render Succi's main sprite
        screen.blit(self.current_image, (screen_x, screen_y))
        return screen_x, screen_y