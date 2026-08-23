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


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x_pos, y, bird_sheet_img, scale, forced_direction=None):
        super().__init__()
        self.rem_value = 3  # REM value for Flyer
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

        # --- PERFORMANCE FIX: Only generate mask if animation frame changed ---
        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        self.rect.x += self.direction * 4
        if self.rect.right < camera_x - 400 or self.rect.left > camera_x + screen_width + 400:
            self.kill()


class Demon(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__()
        self.rem_value = 5  # REM value for Demon
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.frame_index, self.update_time, self.anim_speed = 0, pygame.time.get_ticks(), 100
        self.patrol_start_x, self.patrol_end_x, self.speed, self.direction, self.state = patrol_start_x, patrol_end_x, 2.0, 1, "walk"
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.rect.bottom = y_pos + 85
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, camera_x, player_x=None, player_y=None):
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 300 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1

        if self.state == "walk":
            self.rect.x += self.direction * self.speed
            if self.rect.x >= self.patrol_end_x:
                self.rect.x, self.direction = self.patrol_end_x, -1
            elif self.rect.x <= self.patrol_start_x:
                self.rect.x, self.direction = self.patrol_start_x, 1
            if pygame.time.get_ticks() - self.update_time > self.anim_speed:
                self.update_time = pygame.time.get_ticks()
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_right)
            self.image = self.walk_frames_right[self.frame_index] if self.direction == 1 else self.walk_frames_left[
                self.frame_index]

        elif self.state == "attack":
            if pygame.time.get_ticks() - self.update_time > 70:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.attack_frames_right): self.state, self.frame_index = "walk", 0
            if self.state == "attack":
                self.image = self.attack_frames_right[self.frame_index] if self.direction == 1 else \
                    self.attack_frames_left[self.frame_index]

        old_bottom = self.rect.bottom
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.bottom = old_bottom

        # --- PERFORMANCE FIX: Only generate mask if animation frame changed ---
        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        if self.rect.right < camera_x - 1000: self.kill()


class Skeleton(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r,
                 attack_l):
        super().__init__()
        self.rem_value = 5  # REM value for Skeleton
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.idle_frames_right, self.idle_frames_left = idle_r, idle_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.frame_index, self.update_time, self.anim_speed = 0, pygame.time.get_ticks(), 100
        self.patrol_start_x, self.patrol_end_x, self.speed, self.direction, self.state = patrol_start_x, patrol_end_x, 1.8, 1, "walk"
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.rect.bottom = y_pos + 240
        self.mask = pygame.mask.from_surface(self.image)

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
            if self.state == "idle": self.image = self.idle_frames_right[self.frame_index] if self.direction == 1 else \
                self.idle_frames_left[self.frame_index]

        if self.state == "attack":
            if pygame.time.get_ticks() - self.update_time > 80:
                self.update_time, self.frame_index = pygame.time.get_ticks(), self.frame_index + 1
                if self.frame_index >= len(self.attack_frames_right): self.state, self.frame_index = "walk", 0
            if self.state == "attack": self.image = self.attack_frames_right[
                self.frame_index] if self.direction == 1 else self.attack_frames_left[self.frame_index]

        old_bottom = self.rect.bottom
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.bottom = old_bottom

        # --- PERFORMANCE FIX: Only generate mask if animation frame changed ---
        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        if self.rect.right < camera_x - 1000: self.kill()


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, fireball_img, explode_img, scale=0.45):
        super().__init__()
        self.direction, self.speed, self.state = direction, 800.0, "fly"
        self.frame_index, self.update_time = 0, pygame.time.get_ticks()

        fw, fh = fireball_img.get_width() // 6, fireball_img.get_height()
        self.fly_frames = [pygame.transform.flip(
            pygame.transform.smoothscale(fireball_img.subsurface((i * fw, 0, fw, fh)),
                                         (int(fw * scale), int(fh * scale))), direction == -1, False) for i in range(6)]
        ew, eh = explode_img.get_width() // 8, explode_img.get_height()
        self.exp_frames = [pygame.transform.flip(
            pygame.transform.smoothscale(explode_img.subsurface((i * ew, 0, ew, eh)),
                                         (int(ew * scale), int(fh * scale) if False else int(eh * scale))),
            direction == -1, False) for i in range(8)]

        self.image = self.fly_frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt, camera_x, screen_width):
        if pygame.time.get_ticks() - self.update_time > (50 if self.state == "fly" else 40):
            self.update_time, self.frame_index = pygame.time.get_ticks(), self.frame_index + 1
            if self.state == "fly":
                self.frame_index %= len(self.fly_frames)
                self.image = self.fly_frames[self.frame_index]
            else:
                if self.frame_index >= len(self.exp_frames): self.kill(); return
                self.image = self.exp_frames[self.frame_index]

        if self.state == "fly":
            self.rect.x += self.direction * self.speed * dt

            # --- PERFORMANCE FIX ---
            if getattr(self, "last_image", None) != self.image:
                self.mask = pygame.mask.from_surface(self.image)
                self.last_image = self.image

            if self.rect.right < camera_x - 500 or self.rect.left > camera_x + screen_width + 500:
                self.kill()

    def explode(self):
        if self.state != "explode":
            self.state, self.frame_index, self.update_time = "explode", 0, pygame.time.get_ticks()


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


class Merchant_UI:
    def __init__(self, screen_width, screen_height, sold_out_ref):
        try:
            self.sold_out = sold_out_ref  # Keeps the persistent reference
            raw_bg = pygame.image.load("mats/ui/M_inventory_empty.png").convert()
            self.bg = pygame.transform.smoothscale(raw_bg, (screen_width, screen_height))

            # --- ORIGINAL POTIONS ---
            self.health_p = pygame.transform.smoothscale(pygame.image.load("mats/ui/health_p.png").convert_alpha(),
                                                         (110, 150))
            self.mana_p = pygame.transform.smoothscale(pygame.image.load("mats/ui/mana_p.png").convert_alpha(), (110, 150))
            self.purple_p = pygame.transform.smoothscale(pygame.image.load("mats/ui/purple_p.png").convert_alpha(),
                                                         (110, 150))
            self.rainbow_p = pygame.transform.smoothscale(pygame.image.load(
                "mats/ui/secret_potion.png").convert_alpha(),
                                                          (110, 150))

            wings_raw = pygame.image.load("mats/ui/wings_p_ss.png").convert_alpha()
            ww, wh = wings_raw.get_size()
            self.wings_p = pygame.transform.smoothscale(wings_raw.subsurface((0, int(wh * 0.15), ww, int(wh * 0.70))),
                                                        (110, 150))

            # --- NEW POTIONS ---
            self.teal_p = pygame.transform.smoothscale(pygame.image.load("mats/ui/teal potion.png").convert_alpha(),
                                                       (110, 150))
            self.emerald_p = pygame.transform.smoothscale(pygame.image.load("mats/ui/emerald_hup.png").convert_alpha(),
                                                          (110, 150))
            self.pink_p = pygame.transform.smoothscale(pygame.image.load("mats/ui/pink potion.png").convert_alpha(),
                                                       (110, 150))
            self.mysterious_p = pygame.transform.smoothscale(
                pygame.image.load("mats/ui/mysterious potion.png").convert_alpha(), (110, 150))
            self.silver_p = pygame.transform.smoothscale(pygame.image.load("mats/ui/silver potion.png").convert_alpha(),
                                                         (110, 150))
            self.royal_p = pygame.transform.smoothscale(pygame.image.load("mats/ui/royal potion.png").convert_alpha(),
                                                        (110, 150))
            self.gold_p = pygame.transform.smoothscale(pygame.image.load("mats/ui/gold potion.png").convert_alpha(),
                                                       (110, 150))

            # --- LOAD & SCALE ARROWS ---
            raw_left = pygame.image.load("mats/ui/left.png").convert_alpha()
            raw_right = pygame.image.load("mats/ui/right.png").convert_alpha()

            # Base size: larger and correctly proportioned
            arrow_w, arrow_h = 245, 120  # 220, 95
            self.left_arrow_img = pygame.transform.smoothscale(raw_left, (arrow_w, arrow_h))
            self.right_arrow_img = pygame.transform.smoothscale(raw_right, (arrow_w, arrow_h))

            # Hover size: 10% larger
            hover_w, hover_h = int(arrow_w * 1.10), int(arrow_h * 1.10)
            self.left_arrow_hover = pygame.transform.smoothscale(raw_left, (hover_w, hover_h))
            self.right_arrow_hover = pygame.transform.smoothscale(raw_right, (hover_w, hover_h))

        except pygame.error as e:
            print(f"Error loading UI: {e}")
            import sys;
            sys.exit()

        # The 9 static UI slots on the background image
        self.grid_rects = [
            pygame.Rect(680, 165, 130, 130), pygame.Rect(890, 165, 130, 130), pygame.Rect(1100, 165, 130, 130),
            pygame.Rect(680, 360, 130, 130), pygame.Rect(890, 360, 130, 130), pygame.Rect(1100, 360, 130, 130),
            pygame.Rect(680, 555, 130, 130), pygame.Rect(890, 555, 130, 130), pygame.Rect(1100, 555, 130, 130)
        ]

        self.buy_rect = pygame.Rect(270, 650, 210, 65)

        # Position base hitboxes beside the BUY button
        self.left_arrow_rect = self.left_arrow_img.get_rect(midright=(self.buy_rect.left - 15, self.buy_rect.centery))
        self.right_arrow_rect = self.right_arrow_img.get_rect(midleft=(self.buy_rect.right + 15, self.buy_rect.centery))

        # --- MASTER INVENTORY LIST ---
        self.inventory = [
            # Page 1
            {"id": "Health Potion", "img": self.health_p, "title": "Base Health", "desc": ["Unlocks 3 Max Health."],
             "cost": 50, "color": (50, 255, 50)},
            {"id": "Teal Potion", "img": self.teal_p, "title": "Minor Heal", "desc": ["Restores up to 3 Health."],
             "cost": 50, "color": (50, 200, 255)},
            {"id": "Emerald Potion", "img": self.emerald_p, "title": "Advanced Health", "desc": ["Adds +2 Max Health."],
             "cost": 150, "color": (100, 255, 100)},
            {"id": "Pink Potion", "img": self.pink_p, "title": "Major Heal", "desc": ["Restores up to 5 Health."],
             "cost": 100, "color": (255, 100, 200)},
            {"id": "Mysterious Potion", "img": self.mysterious_p, "title": "Mysterious Potion",
             "desc": ["Unlocks Double Jump."], "cost": 200, "color": (150, 50, 255)},
            {"id": "Silver Potion", "img": self.silver_p, "title": "Silver Potion", "desc": ["Unlocks Melee Attack."],
             "cost": 150, "color": (220, 220, 220)},
            {"id": "Wings Potion", "img": self.wings_p, "title": "Wings Potion",
             "desc": ["Unlocks the ability to Fly."], "cost": 200, "color": (255, 200, 50)},
            {"id": "Purple Potion", "img": self.purple_p, "title": "Purple Potion",
             "desc": ["Unlocks Purple Fireball."], "cost": 100, "color": (180, 50, 255)},
            {"id": "Mana Potion", "img": self.mana_p, "title": "Mana Potion", "desc": ["Magic mysteries await..."],
             "cost": 75, "color": (50, 50, 255)},

            # Page 2
            {"id": "Rainbow Potion", "img": self.rainbow_p, "title": "Rainbow Potion",
             "desc": ["Unlocks ultimate secrets."], "cost": 150, "color": (255, 100, 255)},
            {"id": "Royal Potion", "img": self.royal_p, "title": "Royal Potion", "desc": ["Summons a loyal companion."],
             "cost": 300, "color": (255, 180, 50)},
            {"id": "Gold Potion", "img": self.gold_p, "title": "Gold Potion", "desc": ["Adds +1 final Max Health."],
             "cost": 250, "color": (255, 220, 50)}
        ]

        self.current_page = 0
        self.selected_item_data = None

        self.font_title = pygame.font.SysFont("Lucida Sans", 36)
        self.font_desc = pygame.font.SysFont("Lucida Sans", 24)
        self.font_rem = pygame.font.SysFont("Lucida Sans", 30)

        self.last_click_time = 0

    @property
    def max_pages(self):
        return max(1, (len(self.inventory) + 8) // 9)

    def update(self, mouse_pos, mouse_click, rem):
        bought_item = None
        current_time = pygame.time.get_ticks()

        start_idx = self.current_page * 9
        page_items = self.inventory[start_idx: start_idx + 9]

        if mouse_click and (current_time - self.last_click_time > 200):
            self.last_click_time = current_time

            # Check Arrow Clicks
            if self.right_arrow_rect.collidepoint(mouse_pos) and self.current_page < self.max_pages - 1:
                self.current_page += 1
                self.selected_item_data = None
            elif self.left_arrow_rect.collidepoint(mouse_pos) and self.current_page > 0:
                self.current_page -= 1
                self.selected_item_data = None

            # Check Buy Button Click
            elif self.buy_rect.collidepoint(mouse_pos) and self.selected_item_data:
                item_id = self.selected_item_data["id"]
                if rem >= self.selected_item_data["cost"] and not self.sold_out.get(item_id, False):
                    bought_item = item_id

            # Check Item Slot Clicks
            else:
                clicked_on_item = False
                for i, item in enumerate(page_items):
                    if self.grid_rects[i].collidepoint(mouse_pos):
                        if not self.sold_out.get(item["id"], False):
                            self.selected_item_data = item
                        clicked_on_item = True
                        break

                if not clicked_on_item:
                    self.selected_item_data = None

        return bought_item

    def draw(self, screen, mouse_pos, rem):
        screen.blit(self.bg, (0, 0))

        start_idx = self.current_page * 9
        page_items = self.inventory[start_idx: start_idx + 9]

        # Draw Items on Grid
        for i, item in enumerate(page_items):
            if not self.sold_out.get(item["id"], False):
                slot = self.grid_rects[i]
                screen.blit(item["img"], (slot.x + 10, slot.y - 10))

                if slot.collidepoint(mouse_pos) or (
                        self.selected_item_data and self.selected_item_data["id"] == item["id"]):
                    pygame.draw.rect(screen, (255, 255, 255), slot, 3)

        # Draw Left Arrow with Hover State
        if self.current_page > 0:
            if self.left_arrow_rect.collidepoint(mouse_pos):
                hover_rect = self.left_arrow_hover.get_rect(center=self.left_arrow_rect.center)
                screen.blit(self.left_arrow_hover, hover_rect)
            else:
                screen.blit(self.left_arrow_img, self.left_arrow_rect)

        # Draw Right Arrow with Hover State
        if self.current_page < self.max_pages - 1:
            if self.right_arrow_rect.collidepoint(mouse_pos):
                hover_rect = self.right_arrow_hover.get_rect(center=self.right_arrow_rect.center)
                screen.blit(self.right_arrow_hover, hover_rect)
            else:
                screen.blit(self.right_arrow_img, self.right_arrow_rect)

        # Draw Buy Button Highlight
        if self.buy_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (255, 50, 50), self.buy_rect, 3, border_radius=8)

        # Draw Player REM
        screen.blit(self.font_rem.render(str(rem), True, (253, 117, 234)), (280, 570))

        # Draw Selected Item Info
        if self.selected_item_data and not self.sold_out.get(self.selected_item_data["id"], False):
            text_x = 270
            screen.blit(
                self.font_title.render(self.selected_item_data["title"], True, self.selected_item_data["color"]),
                (text_x, 155))

            y_offset = 205
            for line in self.selected_item_data["desc"]:
                screen.blit(self.font_desc.render(line, True, (190, 200, 200)), (text_x, y_offset))
                y_offset += 25

            screen.blit(self.font_title.render(f"COST: {self.selected_item_data['cost']} REM", True, (253, 117, 234)),
                        (text_x, y_offset + 10))

class Helldog(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__()
        self.health = 2
        self.rem_value = 10
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.frame_index, self.update_time, self.anim_speed = 0, pygame.time.get_ticks(), 80
        self.patrol_start_x, self.patrol_end_x, self.speed, self.direction, self.state = patrol_start_x, patrol_end_x, 3.5, 1, "walk"
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.y_offset = 160
        self.rect.bottom = y_pos + self.y_offset
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def update(self, camera_x, player_x=None, player_y=None):
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 320 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1

        if self.state == "walk":
            self.rect.x += self.direction * self.speed
            if self.rect.x >= self.patrol_end_x:
                self.rect.x, self.direction = self.patrol_end_x, -1
            elif self.rect.x <= self.patrol_start_x:
                self.rect.x, self.direction = self.patrol_start_x, 1
            if pygame.time.get_ticks() - self.update_time > self.anim_speed:
                self.update_time = pygame.time.get_ticks()
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_right)
            self.image = self.walk_frames_right[self.frame_index] if self.direction == 1 else self.walk_frames_left[
                self.frame_index]

        elif self.state == "attack":
            if pygame.time.get_ticks() - self.update_time > 60:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.attack_frames_right): self.state, self.frame_index = "walk", 0
            if self.state == "attack":
                self.image = self.attack_frames_right[self.frame_index] if self.direction == 1 else \
                    self.attack_frames_left[self.frame_index]

        old_bottom = self.rect.bottom
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.bottom = old_bottom

        # --- PERFORMANCE FIX: Only generate mask if animation frame changed ---
        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        if self.rect.right < camera_x - 1000: self.kill()


class Mau(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__()
        # Boosted Mau's health to 3 to throw players off!
        self.health = 3
        self.rem_value = 12
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.frame_index, self.update_time, self.anim_speed = 0, pygame.time.get_ticks(), 100
        self.patrol_start_x, self.patrol_end_x, self.speed, self.direction, self.state = patrol_start_x, patrol_end_x, 2.0, 1, "walk"
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.y_offset = 160
        self.rect.bottom = y_pos + self.y_offset
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def update(self, camera_x, player_x=None, player_y=None):
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 300 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1

        if self.state == "walk":
            self.rect.x += self.direction * self.speed
            if self.rect.x >= self.patrol_end_x:
                self.rect.x, self.direction = self.patrol_end_x, -1
            elif self.rect.x <= self.patrol_start_x:
                self.rect.x, self.direction = self.patrol_start_x, 1
            if pygame.time.get_ticks() - self.update_time > self.anim_speed:
                self.update_time = pygame.time.get_ticks()
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_right)
            self.image = self.walk_frames_right[self.frame_index] if self.direction == 1 else self.walk_frames_left[
                self.frame_index]

        elif self.state == "attack":
            if pygame.time.get_ticks() - self.update_time > 80:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.attack_frames_right): self.state, self.frame_index = "walk", 0
            if self.state == "attack":
                self.image = self.attack_frames_right[self.frame_index] if self.direction == 1 else \
                    self.attack_frames_left[self.frame_index]

        old_bottom = self.rect.bottom
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.bottom = old_bottom

        # --- PERFORMANCE FIX: Only generate mask if animation frame changed ---
        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        if self.rect.right < camera_x - 1000: self.kill()


class Pkgrim(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__()
        self.health = 2
        self.rem_value = 8
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.frame_index, self.update_time, self.anim_speed = 0, pygame.time.get_ticks(), 90
        self.patrol_start_x, self.patrol_end_x, self.speed, self.direction, self.state = patrol_start_x, patrol_end_x, 2.5, 1, "walk"
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.y_offset = 160
        self.rect.bottom = y_pos + self.y_offset
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def update(self, camera_x, player_x=None, player_y=None):
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 300 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1

        if self.state == "walk":
            self.rect.x += self.direction * self.speed
            if self.rect.x >= self.patrol_end_x:
                self.rect.x, self.direction = self.patrol_end_x, -1
            elif self.rect.x <= self.patrol_start_x:
                self.rect.x, self.direction = self.patrol_start_x, 1
            if pygame.time.get_ticks() - self.update_time > self.anim_speed:
                self.update_time = pygame.time.get_ticks()
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_right)
            self.image = self.walk_frames_right[self.frame_index] if self.direction == 1 else self.walk_frames_left[
                self.frame_index]

        elif self.state == "attack":
            if pygame.time.get_ticks() - self.update_time > 70:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.attack_frames_right): self.state, self.frame_index = "walk", 0
            if self.state == "attack":
                self.image = self.attack_frames_right[self.frame_index] if self.direction == 1 else \
                    self.attack_frames_left[self.frame_index]

        old_bottom = self.rect.bottom
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.bottom = old_bottom

        # --- PERFORMANCE FIX: Only generate mask if animation frame changed ---
        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        if self.rect.right < camera_x - 1000: self.kill()


class Azule(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__()
        self.health = 3
        self.rem_value = 12
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.frame_index, self.update_time, self.anim_speed = 0, pygame.time.get_ticks(), 90
        self.patrol_start_x, self.patrol_end_x, self.speed, self.direction, self.state = patrol_start_x, patrol_end_x, 2.2, 1, "walk"
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.y_offset = 160
        self.rect.bottom = y_pos + self.y_offset
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def update(self, camera_x, player_x=None, player_y=None):
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 320 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1

        if self.state == "walk":
            self.rect.x += self.direction * self.speed
            if self.rect.x >= self.patrol_end_x:
                self.rect.x, self.direction = self.patrol_end_x, -1
            elif self.rect.x <= self.patrol_start_x:
                self.rect.x, self.direction = self.patrol_start_x, 1
            if pygame.time.get_ticks() - self.update_time > self.anim_speed:
                self.update_time = pygame.time.get_ticks()
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_right)
            self.image = self.walk_frames_right[self.frame_index] if self.direction == 1 else self.walk_frames_left[
                self.frame_index]

        elif self.state == "attack":
            if pygame.time.get_ticks() - self.update_time > 70:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.attack_frames_right):
                    self.state, self.frame_index = "walk", 0
            if self.state == "attack":
                self.image = self.attack_frames_right[self.frame_index] if self.direction == 1 else \
                self.attack_frames_left[self.frame_index]

        old_bottom = self.rect.bottom
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.bottom = old_bottom

        # --- PERFORMANCE FIX: Only generate mask if animation frame changed ---
        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        if self.rect.right < camera_x - 1000:
            self.kill()


class Titus(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__()
        self.health = 4
        self.rem_value = 15
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.frame_index, self.update_time, self.anim_speed = 0, pygame.time.get_ticks(), 100
        self.patrol_start_x, self.patrol_end_x, self.speed, self.direction, self.state = patrol_start_x, patrol_end_x, 1.8, 1, "walk"
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.y_offset = 160
        self.rect.bottom = y_pos + self.y_offset
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def update(self, camera_x, player_x=None, player_y=None):
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 350 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1

        if self.state == "walk":
            self.rect.x += self.direction * self.speed
            if self.rect.x >= self.patrol_end_x:
                self.rect.x, self.direction = self.patrol_end_x, -1
            elif self.rect.x <= self.patrol_start_x:
                self.rect.x, self.direction = self.patrol_start_x, 1
            if pygame.time.get_ticks() - self.update_time > self.anim_speed:
                self.update_time = pygame.time.get_ticks()
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_right)
            self.image = self.walk_frames_right[self.frame_index] if self.direction == 1 else self.walk_frames_left[
                self.frame_index]

        elif self.state == "attack":
            if pygame.time.get_ticks() - self.update_time > 70:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.attack_frames_right):
                    self.state, self.frame_index = "walk", 0
            if self.state == "attack":
                self.image = self.attack_frames_right[self.frame_index] if self.direction == 1 else \
                self.attack_frames_left[self.frame_index]

        old_bottom = self.rect.bottom
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.bottom = old_bottom

        # --- PERFORMANCE FIX: Only generate mask if animation frame changed ---
        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        if self.rect.right < camera_x - 1000:
            self.kill()


class Lionel(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__()
        self.health = 4
        self.rem_value = 15
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.frame_index, self.update_time, self.anim_speed = 0, pygame.time.get_ticks(), 90
        self.patrol_start_x, self.patrol_end_x, self.speed, self.direction, self.state = patrol_start_x, patrol_end_x, 2.5, 1, "walk"
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.y_offset = 160
        self.rect.bottom = y_pos + self.y_offset
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def update(self, camera_x, player_x=None, player_y=None):
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 320 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1

        if self.state == "walk":
            self.rect.x += self.direction * self.speed
            if self.rect.x >= self.patrol_end_x:
                self.rect.x, self.direction = self.patrol_end_x, -1
            elif self.rect.x <= self.patrol_start_x:
                self.rect.x, self.direction = self.patrol_start_x, 1
            if pygame.time.get_ticks() - self.update_time > self.anim_speed:
                self.update_time = pygame.time.get_ticks()
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_right)
            self.image = self.walk_frames_right[self.frame_index] if self.direction == 1 else self.walk_frames_left[
                self.frame_index]

        elif self.state == "attack":
            if pygame.time.get_ticks() - self.update_time > 70:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.attack_frames_right):
                    self.state, self.frame_index = "walk", 0
            if self.state == "attack":
                self.image = self.attack_frames_right[self.frame_index] if self.direction == 1 else \
                self.attack_frames_left[self.frame_index]

        old_bottom = self.rect.bottom
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.bottom = old_bottom

        # --- PERFORMANCE FIX ---
        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        if self.rect.right < camera_x - 1000:
            self.kill()


class Demented(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r,
                 attack_l):
        super().__init__()
        self.health = 3
        self.rem_value = 12
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.idle_frames_right, self.idle_frames_left = idle_r, idle_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.frame_index, self.update_time, self.anim_speed = 0, pygame.time.get_ticks(), 100
        self.patrol_start_x, self.patrol_end_x, self.speed, self.direction, self.state = patrol_start_x, patrol_end_x, 1.8, 1, "walk"
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.y_offset = 160
        self.rect.bottom = y_pos + self.y_offset
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

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

        # --- PERFORMANCE FIX ---
        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        if self.rect.right < camera_x - 1000: self.kill()


# ==========================================
# NEW LEVEL 4 ENEMIES
# ==========================================

class Elaine(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__()
        self.health = 5
        self.rem_value = 18
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.frame_index, self.update_time, self.anim_speed = 0, pygame.time.get_ticks(), 90
        self.patrol_start_x, self.patrol_end_x, self.speed, self.direction, self.state = patrol_start_x, patrol_end_x, 2.5, 1, "walk"
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.y_offset = 160
        self.rect.bottom = y_pos + self.y_offset
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def update(self, camera_x, player_x=None, player_y=None):
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 320 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1

        if self.state == "walk":
            self.rect.x += self.direction * self.speed
            if self.rect.x >= self.patrol_end_x:
                self.rect.x, self.direction = self.patrol_end_x, -1
            elif self.rect.x <= self.patrol_start_x:
                self.rect.x, self.direction = self.patrol_start_x, 1
            if pygame.time.get_ticks() - self.update_time > self.anim_speed:
                self.update_time = pygame.time.get_ticks()
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_right)
            self.image = self.walk_frames_right[self.frame_index] if self.direction == 1 else self.walk_frames_left[
                self.frame_index]

        elif self.state == "attack":
            if pygame.time.get_ticks() - self.update_time > 70:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.attack_frames_right):
                    self.state, self.frame_index = "walk", 0
            if self.state == "attack":
                self.image = self.attack_frames_right[self.frame_index] if self.direction == 1 else \
                self.attack_frames_left[self.frame_index]

        old_bottom = self.rect.bottom
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.bottom = old_bottom

        if getattr(self, "last_image", None) != self.image:
            self.mask = pygame.mask.from_surface(self.image)
            self.last_image = self.image

        if self.rect.right < camera_x - 1000:
            self.kill()


class Groundskeeper(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, idle_r, idle_l, attack_r, attack_l):
        super().__init__()
        self.health = 4
        self.rem_value = 15
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.idle_frames_right, self.idle_frames_left = idle_r, idle_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.frame_index, self.update_time, self.anim_speed = 0, pygame.time.get_ticks(), 100
        self.patrol_start_x, self.patrol_end_x, self.speed, self.direction, self.state = patrol_start_x, patrol_end_x, 1.8, 1, "walk"
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.y_offset = 160
        self.rect.bottom = y_pos + self.y_offset
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

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


class RoyalHH(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__()
        self.health = 4
        self.rem_value = 15
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.frame_index, self.update_time, self.anim_speed = 0, pygame.time.get_ticks(), 80
        self.patrol_start_x, self.patrol_end_x, self.speed, self.direction, self.state = patrol_start_x, patrol_end_x, 3.8, 1, "walk"
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.y_offset = 160
        self.rect.bottom = y_pos + self.y_offset
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def update(self, camera_x, player_x=None, player_y=None):
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 320 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1

        if self.state == "walk":
            self.rect.x += self.direction * self.speed
            if self.rect.x >= self.patrol_end_x:
                self.rect.x, self.direction = self.patrol_end_x, -1
            elif self.rect.x <= self.patrol_start_x:
                self.rect.x, self.direction = self.patrol_start_x, 1
            if pygame.time.get_ticks() - self.update_time > self.anim_speed:
                self.update_time = pygame.time.get_ticks()
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_right)
            self.image = self.walk_frames_right[self.frame_index] if self.direction == 1 else self.walk_frames_left[
                self.frame_index]

        elif self.state == "attack":
            if pygame.time.get_ticks() - self.update_time > 60:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
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


class RoyalZombie(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__()
        self.health = 5
        self.rem_value = 18
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.frame_index, self.update_time, self.anim_speed = 0, pygame.time.get_ticks(), 100
        self.patrol_start_x, self.patrol_end_x, self.speed, self.direction, self.state = patrol_start_x, patrol_end_x, 2.0, 1, "walk"
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.y_offset = 160
        self.rect.bottom = y_pos + self.y_offset
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def update(self, camera_x, player_x=None, player_y=None):
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 300 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1

        if self.state == "walk":
            self.rect.x += self.direction * self.speed
            if self.rect.x >= self.patrol_end_x:
                self.rect.x, self.direction = self.patrol_end_x, -1
            elif self.rect.x <= self.patrol_start_x:
                self.rect.x, self.direction = self.patrol_start_x, 1
            if pygame.time.get_ticks() - self.update_time > self.anim_speed:
                self.update_time = pygame.time.get_ticks()
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_right)
            self.image = self.walk_frames_right[self.frame_index] if self.direction == 1 else self.walk_frames_left[
                self.frame_index]

        elif self.state == "attack":
            if pygame.time.get_ticks() - self.update_time > 80:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
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


class Zombie1(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__()
        self.health = 3
        self.rem_value = 10
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.frame_index, self.update_time, self.anim_speed = 0, pygame.time.get_ticks(), 100
        self.patrol_start_x, self.patrol_end_x, self.speed, self.direction, self.state = patrol_start_x, patrol_end_x, 1.9, 1, "walk"
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.y_offset = 160
        self.rect.bottom = y_pos + self.y_offset
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def update(self, camera_x, player_x=None, player_y=None):
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 300 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1

        if self.state == "walk":
            self.rect.x += self.direction * self.speed
            if self.rect.x >= self.patrol_end_x:
                self.rect.x, self.direction = self.patrol_end_x, -1
            elif self.rect.x <= self.patrol_start_x:
                self.rect.x, self.direction = self.patrol_start_x, 1
            if pygame.time.get_ticks() - self.update_time > self.anim_speed:
                self.update_time = pygame.time.get_ticks()
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_right)
            self.image = self.walk_frames_right[self.frame_index] if self.direction == 1 else self.walk_frames_left[
                self.frame_index]

        elif self.state == "attack":
            if pygame.time.get_ticks() - self.update_time > 80:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
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


class Zombie2(pygame.sprite.Sprite):
    def __init__(self, spawn_x, y_pos, patrol_start_x, patrol_end_x, walk_r, walk_l, attack_r, attack_l):
        super().__init__()
        self.health = 3
        self.rem_value = 12
        self.walk_frames_right, self.walk_frames_left = walk_r, walk_l
        self.attack_frames_right, self.attack_frames_left = attack_r, attack_l
        self.frame_index, self.update_time, self.anim_speed = 0, pygame.time.get_ticks(), 100
        self.patrol_start_x, self.patrol_end_x, self.speed, self.direction, self.state = patrol_start_x, patrol_end_x, 2.1, 1, "walk"
        self.image = self.walk_frames_right[0]
        self.rect = self.image.get_rect(x=spawn_x)
        self.y_offset = 160
        self.rect.bottom = y_pos + self.y_offset
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def update(self, camera_x, player_x=None, player_y=None):
        if player_x and player_y and abs(player_y - self.rect.centery) < 350:
            if abs(player_x - self.rect.centerx) < 300 and self.state != "attack":
                self.state, self.frame_index, self.update_time = "attack", 0, pygame.time.get_ticks()
                self.direction = 1 if player_x > self.rect.centerx else -1

        if self.state == "walk":
            self.rect.x += self.direction * self.speed
            if self.rect.x >= self.patrol_end_x:
                self.rect.x, self.direction = self.patrol_end_x, -1
            elif self.rect.x <= self.patrol_start_x:
                self.rect.x, self.direction = self.patrol_start_x, 1
            if pygame.time.get_ticks() - self.update_time > self.anim_speed:
                self.update_time = pygame.time.get_ticks()
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames_right)
            self.image = self.walk_frames_right[self.frame_index] if self.direction == 1 else self.walk_frames_left[
                self.frame_index]

        elif self.state == "attack":
            if pygame.time.get_ticks() - self.update_time > 80:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
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