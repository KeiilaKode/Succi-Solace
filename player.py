# Succi Player Class
import pygame
import math
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

        # Mode Flag: True when in Level 8 (Flight Level)
        self.is_flying_level = False
        self.hover_sine_timer = 0.0

        # Double Jump Capabilities
        self.has_double_jump = False
        self.can_double_jump = False
        self.jump_key_released = True

        # Dash State Variables
        self.has_dash = False
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_direction = 1
        self.dash_charges = getattr(config, 'PLAYER_DASH_MAX_CHARGES', 2)
        self.dash_recharge_timer = 0
        self.dash_key_released = True

        # Ghost Afterimages trail management
        self.dash_ghosts = []
        self.ghost_spawn_timer = 0

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

        # Directional Aiming for Projectiles (0.0 = Straight, -1.0 = Up Diagonal, 1.0 = Down Diagonal)
        self.aim_dir_y = 0.0
        self.cast_aim_dir_y = 0.0

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

        if self.is_flying_level:
            duck_pressed = False
        else:
            duck_pressed = keys[pygame.K_DOWN] or keys[pygame.K_s]

        space_pressed = keys[pygame.K_SPACE]
        w_pressed = keys[pygame.K_w]

        self.recovering_duck = (self.current_anim == "duck" and not duck_pressed and self.playing)
        self.attacking = (self.current_anim in ["attack", "run_attack", "kick", "jump_kick", "idle_fly_shot",
                                                "fly_shot_reg"] and self.playing)

        # ======================================================================
        # --- LEVEL 8: FLIGHT CONTROLS ---
        # ======================================================================
        if self.is_flying_level:
            fly_speed = getattr(config, 'PLAYER_FLY_SPEED_FAST', 400.0) if run_pressed else getattr(config,
                                                                                                    'PLAYER_FLY_SPEED_CRUISE',
                                                                                                    240.0)

            # In flight mode, SPACE BAR triggers the aerial dash!
            if space_pressed and self.dash_key_released and self.has_dash and not self.is_dashing and self.dash_charges > 0:
                self.is_dashing = True
                self.dash_timer = getattr(config, 'PLAYER_DASH_DURATION', 180)
                self.dash_charges -= 1
                self.dash_direction = 1 if self.facing_right else -1
                self.ghost_spawn_timer = 0
                if self.jump_fx:
                    try:
                        self.jump_fx.play()
                    except Exception:
                        pass

            self.dash_key_released = not space_pressed

            if self.is_dashing:
                return moving, run_pressed, duck_pressed

            # 8-Way Flight Navigation
            self.vx, self.vy = 0.0, 0.0

            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.vx = -fly_speed
                self.facing_right = False
                moving = True
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.vx = fly_speed
                self.facing_right = True
                moving = True

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.vy = -fly_speed
                moving = True
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.vy = fly_speed
                moving = True

            if self.vx != 0 and self.vy != 0:
                self.vx *= 0.707
                self.vy *= 0.707

            # Continuous intent tracking
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.aim_dir_y = -1.0
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.aim_dir_y = 1.0
            else:
                self.aim_dir_y = 0.0

            return moving, run_pressed, duck_pressed

        # ======================================================================
        # --- GROUNDED CONTROLS (LEVELS 1 - 7) ---
        # ======================================================================
        if w_pressed and self.dash_key_released and self.has_dash and not self.is_dashing and self.dash_charges > 0 and not self.recovering_duck and not duck_pressed:
            self.is_dashing = True
            self.dash_timer = getattr(config, 'PLAYER_DASH_DURATION', 180)
            self.dash_charges -= 1
            self.dash_direction = 1 if self.facing_right else -1
            self.ghost_spawn_timer = 0
            if self.jump_fx:
                try:
                    self.jump_fx.play()
                except Exception:
                    pass

        self.dash_key_released = not w_pressed

        if self.is_dashing:
            pass
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
            self.vy = getattr(config, 'PLAYER_DOUBLE_JUMP_IMPULSE', config.PLAYER_JUMP_IMPULSE)
            self.can_double_jump = False
            if self.jump_fx:
                self.jump_fx.play()

        self.jump_key_released = not space_pressed
        self.aim_dir_y = 0.0

        return moving, run_pressed, duck_pressed

    def trigger_attack(self, run_pressed, moving):
        """Triggered externally by mouse clicks in main.py"""
        can_attack = (
                                 self.is_flying_level or not self.duck_pressed) and not self.recovering_duck and not self.is_dashing

        if can_attack and not self.attacking:
            # ==================================================================
            # --- REAL-TIME INSTANT KEY EVALUATION AT THE MOMENT OF CLICK ---
            # Evaluates current keys directly to eliminate frame-polling latency!
            # ==================================================================
            live_keys = pygame.key.get_pressed()
            if self.is_flying_level:
                if live_keys[pygame.K_w] or live_keys[pygame.K_UP]:
                    self.cast_aim_dir_y = -1.0  # Aim Up-Diagonal
                elif live_keys[pygame.K_s] or live_keys[pygame.K_DOWN]:
                    self.cast_aim_dir_y = 1.0  # Aim Down-Diagonal
                else:
                    self.cast_aim_dir_y = 0.0  # Aim Straight
            else:
                self.cast_aim_dir_y = 0.0

            # Determine flight casting animation
            if self.is_flying_level:
                if moving:
                    self.current_anim = "fly_shot_reg" if "fly_shot_reg" in self.animations else "flying"
                else:
                    self.current_anim = "idle_fly_shot" if "idle_fly_shot" in self.animations else "idle_fly"
            else:
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
        if not self.is_flying_level and not getattr(self, 'duck_pressed',
                                                    False) and not self.recovering_duck and not self.is_dashing:
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
        if self.is_dashing:
            dash_spd = getattr(config, 'PLAYER_DASH_SPEED', 850.0)
            self.vx = self.dash_direction * dash_spd
            self.vy = 0.0
            self.x += self.vx * dt
            if self.is_flying_level:
                self.y = max(60.0, min(700.0, self.y))
            return

        if self.is_flying_level:
            self.x += self.vx * dt
            self.y += self.vy * dt

            if self.vx == 0 and self.vy == 0:
                self.hover_sine_timer += dt * 3.5
                self.y += math.sin(self.hover_sine_timer) * 0.45

            self.y = max(60.0, min(700.0, self.y))
            self.on_ground = False
            return

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
            pass
        elif self.attacking:
            pass
        elif self.is_flying_level:
            if moving:
                if "flying" in self.animations and self.current_anim != "flying":
                    self.current_anim = "flying"
                    self.current_frame = 0
                    self.animation_timer = 0
                    self.playing = True
            else:
                if "idle_fly" in self.animations and self.current_anim != "idle_fly":
                    self.current_anim = "idle_fly"
                    self.current_frame = 0
                    self.animation_timer = 0
                    self.playing = True
        elif not self.on_ground or self.recovering_duck:
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
                    self.attacking = False

    def take_damage(self):
        if pygame.time.get_ticks() - self.invulnerable_timer < config.PLAYER_INVULNERABLE_DURATION:
            return False

        self.health -= 1
        self.invulnerable_timer = pygame.time.get_ticks()

        if self.health <= 0:
            return True
        return False

    def prepare_frame(self):
        if self.is_dashing:
            if self.is_flying_level and "flying" in self.animations:
                frame_surf = self.animations["flying"][3]
                correction = self.scale_corrections.get("flying", 2.5)
            elif "run" in self.animations:
                frame_surf = self.animations["run"][3]
                correction = self.scale_corrections.get("run", 1.08)
            else:
                frame_surf = self.animations[self.current_anim][self.current_frame]
                correction = self.scale_corrections.get(self.current_anim, 1.0)
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

        if self.is_flying_level:
            world_x = int(self.x - fw // 2)
            world_y = int(self.y - fh // 2)
        else:
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
        if not self.current_image:
            return

        ghost_surf = self.current_image.copy()
        tint_overlay = pygame.Surface(ghost_surf.get_size(), pygame.SRCALPHA)
        tint_overlay.fill((175, 45, 225, 255))
        ghost_surf.blit(tint_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        self.dash_ghosts.append({
            "image": ghost_surf,
            "x": self.rect.x,
            "y": self.rect.y,
            "alpha": 180.0
        })

    def update(self, keys, dt, dt_ms, platform_group, loops_dict):
        if self.is_dashing:
            self.dash_timer -= dt_ms
            self.ghost_spawn_timer += dt_ms
            if self.ghost_spawn_timer >= 35:
                self.spawn_dash_ghost()
                self.ghost_spawn_timer = 0

            if self.dash_timer <= 0:
                self.is_dashing = False

        max_c = getattr(config, 'PLAYER_DASH_MAX_CHARGES', 2)
        rech_time = getattr(config, 'PLAYER_DASH_RECHARGE_TIME', 2000)
        if self.dash_charges < max_c:
            self.dash_recharge_timer += dt_ms
            if self.dash_recharge_timer >= rech_time:
                self.dash_charges += 1
                self.dash_recharge_timer = 0
        else:
            self.dash_recharge_timer = 0

        for ghost in self.dash_ghosts[:]:
            ghost["alpha"] -= 850.0 * dt
            if ghost["alpha"] <= 0:
                self.dash_ghosts.remove(ghost)

        moving, run_pressed, duck_pressed = self.handle_input(keys)
        self.duck_pressed = duck_pressed
        self.update_physics(dt, platform_group)
        self.update_animation_state(moving, run_pressed, duck_pressed)
        self.advance_frame(dt_ms, loops_dict)
        self.prepare_frame()

    def draw(self, screen, camera_x):
        for ghost in self.dash_ghosts:
            ghost_surf = ghost["image"].copy()
            ghost_surf.set_alpha(max(0, min(255, int(ghost["alpha"]))))
            screen.blit(ghost_surf, (ghost["x"] - camera_x, ghost["y"]))

        if pygame.time.get_ticks() - self.invulnerable_timer < config.PLAYER_INVULNERABLE_DURATION:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                return self.rect.x - camera_x, self.rect.y

        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y

        screen.blit(self.current_image, (screen_x, screen_y))
        return screen_x, screen_y