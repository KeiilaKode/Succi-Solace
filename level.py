#-level-#

#-level-#

# --- level.py ---#
import pygame
import random
import sys
from entities import Platform
from enemies import Enemy, GargoyleFlyer, GreyGargoyleFlyer, Demon, Skeleton, Helldog, Mau, Pkgrim, Azule, \
    Titus, Lionel, Demented, Elaine, \
    Groundskeeper, RoyalHH, RoyalZombie, Zombie1, Zombie2, Priestly, Realmwalker, Pursuer, Braid, Deadlight, Victoria, \
    Hellguard, Cecil, Margret, Lashly, Kali, Kimoura, Cassie, Silas, Thad


def trim_black_side_borders(surface, threshold=15):
    w, h = surface.get_size()
    left, right, top, bottom = 0, w, 0, h

    # Trim Left
    for x in range(w // 4):
        has_content = any(
            surface.get_at((x, y)).r > threshold or
            surface.get_at((x, y)).g > threshold or
            surface.get_at((x, y)).b > threshold
            for y in range(0, h, 10)
        )
        if has_content:
            left = x
            break

    # Trim Right
    for x in range(w - 1, w - 1 - (w // 4), -1):
        has_content = any(
            surface.get_at((x, y)).r > threshold or
            surface.get_at((x, y)).g > threshold or
            surface.get_at((x, y)).b > threshold
            for y in range(0, h, 10)
        )
        if has_content:
            right = x + 1
            break

    # Trim Top
    for y in range(h // 4):
        has_content = any(
            surface.get_at((x, y)).r > threshold or
            surface.get_at((x, y)).g > threshold or
            surface.get_at((x, y)).b > threshold
            for x in range(left, right, 10)
        )
        if has_content:
            top = y
            break

    # Trim Bottom
    for y in range(h - 1, h - 1 - (h // 4), -1):
        has_content = any(
            surface.get_at((x, y)).r > threshold or
            surface.get_at((x, y)).g > threshold or
            surface.get_at((x, y)).b > threshold
            for x in range(left, right, 10)
        )
        if has_content:
            bottom = y + 1
            break

    if right > left and bottom > top:
        return surface.subsurface((left, top, right - left, bottom - top)).copy()
    return surface


def trim_transparent_borders(surface):
    w, h = surface.get_size()
    left, right, top, bottom = w, 0, h, 0

    for y in range(h):
        for x in range(w):
            if surface.get_at((x, y)).a > 0:
                if x < left: left = x
                if x > right: right = x
                if y < top: top = y
                if y > bottom: bottom = y

    if right >= left and bottom >= top:
        return surface.subsurface((left, top, (right - left) + 1, (bottom - top) + 1)).copy()
    return surface


def load_enemy_frames(filename, num_frames, scale):
    sheet = pygame.image.load(filename).convert_alpha()
    frames_r, frames_l = [], []
    fw, fh = sheet.get_width() // num_frames, sheet.get_height()
    for i in range(num_frames):
        frame = pygame.Surface((fw, fh), pygame.SRCALPHA).convert_alpha()
        frame.blit(sheet, (0, 0), (i * fw, 0, fw, fh))
        frame_r = pygame.transform.smoothscale(frame, (int(fw * scale), int(fh * scale)))
        frames_r.append(frame_r)
        frames_l.append(pygame.transform.flip(frame_r, True, False))
    return frames_r, frames_l


class Level_01:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.y_ground = 730.0

        if not hasattr(self, 'floor_y_offset'):
            self.floor_y_offset = 20

        if not hasattr(self, 'platform_offset_ratio'):
            self.platform_offset_ratio = 0.18  # Push Succi down into the new 3D platforms

        # Parameterize platform sizes and spawn heights so other levels don't break
        if not hasattr(self, 'plat_min_w'): self.plat_min_w = 80
        if not hasattr(self, 'plat_max_w'): self.plat_max_w = 140
        if not hasattr(self, 'plat_min_y'): self.plat_min_y = 400
        if not hasattr(self, 'plat_max_y'): self.plat_max_y = 660
        if not hasattr(self, 'start_plat_widths'): self.start_plat_widths = [120, 130, 110]

        self.platform_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()

        # --- NEW GROUPS ---
        self.cecil_group = pygame.sprite.Group()
        self.margret_group = pygame.sprite.Group()
        self.lashly_group = pygame.sprite.Group()
        self.hellguard_group = pygame.sprite.Group()

        # --- NOT IN USE GROUPS ---
        # self.demon_group = pygame.sprite.Group()
        # self.skeleton_group = pygame.sprite.Group()

        self.last_spawned_bg_index = -1
        self.load_assets()

        self.level_end_x = self.max_backgrounds * self.bg_w
        self.door_world_x = self.level_end_x - 200

        if not hasattr(self, 'platform_images') or not self.platform_images:
            self.platform_images = [self.platform_image]

        self.platform_group.add(
            Platform(200, 580, self.start_plat_widths[0], random.choice(self.platform_images),
                     self.platform_offset_ratio))
        self.platform_group.add(
            Platform(450, 380, self.start_plat_widths[1], random.choice(self.platform_images),
                     self.platform_offset_ratio))
        self.platform_group.add(
            Platform(800, 480, self.start_plat_widths[2], random.choice(self.platform_images),
                     self.platform_offset_ratio))

    def load_assets(self):
        # NEW LOGIC: Load the 16 distinct panels sequentially
        full_bg_filenames = [f"backgrounds/lvl_1_backgrounds/{i}_lvl1_bg.png" for i in range(1, 17)]

        self.max_backgrounds = len(full_bg_filenames)

        first_raw = pygame.image.load(full_bg_filenames[0]).convert()
        first_trimmed = trim_black_side_borders(first_raw)
        bg_scale_ratio = self.screen_height / first_trimmed.get_height()
        self.bg_w = int(first_trimmed.get_width() * bg_scale_ratio) - 1

        self.bg_list = [pygame.transform.smoothscale(trim_black_side_borders(pygame.image.load(f).convert()),
                                                     (self.bg_w, self.screen_height)) for f in full_bg_filenames]

        # Swapped floor2.PNG for the new floor1.png
        floor_img = pygame.image.load("mats/platforms/level 1 plats/new floor.png").convert()
        floor_img.set_colorkey((0, 0, 0))
        self.target_floor_h = 200
        floor_scale_ratio = self.target_floor_h / floor_img.get_height()
        self.floor_w = int(floor_img.get_width() * floor_scale_ratio) - 1
        self.floor_img = pygame.transform.smoothscale(floor_img, (self.floor_w, self.target_floor_h))
        self.floor_flip_img = pygame.transform.flip(self.floor_img, True, False)

        # --- NEW LEVEL 1 PLATFORMS ---
        self.platform_images = []
        try:
            p1 = pygame.image.load("mats/platforms/level 1 plats/lvl1_plat1.png").convert_alpha()
            p2 = pygame.image.load("mats/platforms/level 1 plats/lvl1_plat2.png").convert_alpha()
            p4 = pygame.image.load("mats/platforms/level 1 plats/lvl1_plat4.png").convert_alpha()
            self.platform_images = [
                trim_transparent_borders(p1),
                trim_transparent_borders(p2),
                trim_transparent_borders(p4)
            ]
        except pygame.error as e:
            print(f"Error loading Level 1 platforms: {e}")
            # Fallback just in case
            self.platform_image = pygame.image.load("mats/platforms/level 1 plats/plat31c.png").convert_alpha()
            self.platform_images = [self.platform_image]

        self.bird_sheet_img = pygame.image.load(
            "spritesheets/enemies/lvl_1_enemies/gargoyle_grey_fly_ss.png").convert_alpha()

        # --- NEW LEVEL 1 ENEMIES ---
        base_scale = 0.60
        self.cecil_walk_r, self.cecil_walk_l = load_enemy_frames("spritesheets/enemies/lvl_1_enemies/cecil_walk_ss.png",
                                                                 8, base_scale)
        self.cecil_attack_r, self.cecil_attack_l = load_enemy_frames(
            "spritesheets/enemies/lvl_1_enemies/cecil_attack_ss.png", 10, base_scale)

        self.margret_walk_r, self.margret_walk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_1_enemies/margret_walk_ss.png", 8, base_scale)
        self.margret_attack_r, self.margret_attack_l = load_enemy_frames(
            "spritesheets/enemies/lvl_1_enemies/margret_attack_ss.png", 12, base_scale)

        self.lashly_walk_r, self.lashly_walk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_1_enemies/lashly_walk_ss.png", 8, base_scale)
        self.lashly_attack_r, self.lashly_attack_l = load_enemy_frames(
            "spritesheets/enemies/lvl_1_enemies/lashly_attack_ss.png", 12, base_scale)

        self.hg_walk_r, self.hg_walk_l = load_enemy_frames("spritesheets/enemies/lvl_1_enemies/hellguard_walk_ss.png",
                                                           8, 0.7)
        self.hg_attack_r, self.hg_attack_l = load_enemy_frames(
            "spritesheets/enemies/lvl_1_enemies/hellguard_attack_ss.png", 12, 0.7)

    def reset(self):
        self.platform_group.empty()
        self.enemy_group.empty()

        self.cecil_group.empty()
        self.margret_group.empty()
        self.lashly_group.empty()
        self.hellguard_group.empty()

        self.last_spawned_bg_index = -1

        self.platform_group.add(
            Platform(200, 580, self.start_plat_widths[0], random.choice(self.platform_images),
                     self.platform_offset_ratio))
        self.platform_group.add(
            Platform(450, 380, self.start_plat_widths[1], random.choice(self.platform_images),
                     self.platform_offset_ratio))
        self.platform_group.add(
            Platform(800, 480, self.start_plat_widths[2], random.choice(self.platform_images),
                     self.platform_offset_ratio))

    def update(self, dt, camera_x, player_x, player_y, is_banner_active=False):
        for platform in list(self.platform_group):
            if platform.rect.right < camera_x - 4000: platform.kill()

        if camera_x + self.screen_width < self.level_end_x - 500:
            if len(self.platform_group) < 40:
                last_p = max(self.platform_group, key=lambda p: p.rect.x, default=None)
                p_x = (last_p.rect.right + random.randint(120, 290)) if last_p else (camera_x + self.screen_width + 100)

                chosen_plat_img = random.choice(self.platform_images)
                self.platform_group.add(
                    Platform(p_x, random.randint(self.plat_min_y, self.plat_max_y),
                             random.randint(self.plat_min_w, self.plat_max_w), chosen_plat_img,
                             self.platform_offset_ratio))

            if not is_banner_active and len(self.enemy_group) < 3 and random.randint(1, 60) == 1:
                side = random.choice(["left", "right"])
                ex = (camera_x - 150) if side == "left" else (camera_x + self.screen_width + 150)
                self.enemy_group.add(GreyGargoyleFlyer(ex, random.randint(200, 480), self.bird_sheet_img, 0.31,
                                                       forced_direction=1 if side == "left" else -1))

        current_bg_index = int(player_x // self.bg_w)

        if current_bg_index > self.last_spawned_bg_index and current_bg_index < self.max_backgrounds - 1:
            t_bg = current_bg_index + 1
            p_start, p_end = t_bg * self.bg_w, (t_bg + 1) * self.bg_w - 100

            num_enemies = random.randint(2, 3)
            segment_width = (p_end - p_start) // num_enemies

            for i in range(num_enemies):
                e_start = p_start + (i * segment_width)
                e_end = e_start + segment_width
                spawn_x = random.randint(e_start + 110, e_end - 110)

                spawn_choice = random.randint(1, 4)
                if spawn_choice == 1:
                    self.cecil_group.add(
                        Cecil(spawn_x, self.y_ground, e_start, e_end, self.cecil_walk_r, self.cecil_walk_l,
                              self.cecil_attack_r, self.cecil_attack_l))
                elif spawn_choice == 2:
                    self.margret_group.add(
                        Margret(spawn_x, self.y_ground, e_start, e_end, self.margret_walk_r, self.margret_walk_l,
                                self.margret_attack_r, self.margret_attack_l))
                elif spawn_choice == 3:
                    self.lashly_group.add(
                        Lashly(spawn_x, self.y_ground, e_start, e_end, self.lashly_walk_r, self.lashly_walk_l,
                               self.lashly_attack_r, self.lashly_attack_l))
                else:
                    self.hellguard_group.add(
                        Hellguard(spawn_x, self.y_ground, e_start, e_end, self.hg_walk_r, self.hg_walk_l,
                                  self.hg_attack_r, self.hg_attack_l))

            self.last_spawned_bg_index = current_bg_index

        self.enemy_group.update(camera_x, self.screen_width)
        self.cecil_group.update(camera_x, player_x, player_y)
        self.margret_group.update(camera_x, player_x, player_y)
        self.lashly_group.update(camera_x, player_x, player_y)
        self.hellguard_group.update(camera_x, player_x, player_y)

    def draw(self, screen, camera_x):
        s_bg = int(camera_x // self.bg_w)
        for i in range(s_bg, s_bg + (self.screen_width // self.bg_w) + 2):
            if i < self.max_backgrounds:
                screen.blit(self.bg_list[i], ((i * self.bg_w) - camera_x, 0))

        s_floor = int(camera_x // self.floor_w)
        for i in range(s_floor, s_floor + (self.screen_width // self.floor_w) + 2):
            if (i * self.floor_w) < self.level_end_x:
                screen.blit(self.floor_img if i % 2 == 0 else self.floor_flip_img,
                            ((i * self.floor_w) - camera_x,
                             self.screen_height - self.target_floor_h + self.floor_y_offset))

        for p in self.platform_group:
            if -200 < (px := p.rect.x - camera_x) < self.screen_width + 200: screen.blit(p.image, (px, p.rect.y))

        for enemy in self.enemy_group:
            if -200 < (ex := enemy.rect.x - camera_x) < self.screen_width + 200: screen.blit(enemy.image,
                                                                                             (ex, enemy.rect.y))

        for cecil in self.cecil_group:
            if -200 < (cx := cecil.rect.x - camera_x) < self.screen_width + 200: screen.blit(cecil.image,
                                                                                             (cx, cecil.rect.top))
        for margret in self.margret_group:
            if -200 < (mx := margret.rect.x - camera_x) < self.screen_width + 200: screen.blit(margret.image,
                                                                                               (mx, margret.rect.top))
        for lashly in self.lashly_group:
            if -200 < (lx := lashly.rect.x - camera_x) < self.screen_width + 200: screen.blit(lashly.image,
                                                                                              (lx, lashly.rect.top))
        for hg in self.hellguard_group:
            if -200 < (hx := hg.rect.x - camera_x) < self.screen_width + 200: screen.blit(hg.image, (hx, hg.rect.top))


class Merchant_Room:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.y_ground = 730.0

        try:
            raw_bg = pygame.image.load("backgrounds/lvl_1_bgs_legacy/lvl_1_merchant_bg.png").convert()
            trimmed_bg = trim_black_side_borders(raw_bg)
            scale_ratio = self.screen_height / trimmed_bg.get_height()
            self.bg_w = int(trimmed_bg.get_width() * scale_ratio)
            self.bg_image = pygame.transform.smoothscale(trimmed_bg, (self.bg_w, self.screen_height))

            # Swapped floor2.PNG for floor1.png here as well
            floor_img = pygame.image.load("mats/platforms/level 1 plats/floor1.png").convert()
            floor_img.set_colorkey((0, 0, 0))
            self.target_floor_h = 200
            floor_scale_ratio = self.target_floor_h / floor_img.get_height()
            self.floor_w = int(floor_img.get_width() * floor_scale_ratio) - 1
            self.floor_img = pygame.transform.smoothscale(floor_img, (self.floor_w, self.target_floor_h))
        except pygame.error as e:
            print(f"Error loading Merchant Room assets: {e}")
            sys.exit()

    def draw(self, screen, camera_x):
        screen.blit(self.bg_image, (0 - camera_x, 0))
        s_floor = int(camera_x // self.floor_w)
        for i in range(s_floor, s_floor + (self.screen_width // self.floor_w) + 2):
            screen.blit(self.floor_img, ((i * self.floor_w) - camera_x, self.screen_height - self.target_floor_h + 30))


class Level_02(Level_01):
    def __init__(self, screen_width, screen_height):
        self.platform_offset_ratio = 0.22
        self.floor_y_offset = 0
        self.plat_min_w = 90
        self.plat_max_w = 200
        self.plat_min_y = 320
        self.plat_max_y = 625
        self.start_plat_widths = [180, 200, 160]
        super().__init__(screen_width, screen_height)

        # Level 2 Specific Enemy Groups
        self.helldog_group = pygame.sprite.Group()
        self.mau_group = pygame.sprite.Group()
        self.pkgrim_group = pygame.sprite.Group()

    def load_assets(self):
        base_bg_filenames = [
            "backgrounds/lvl_2_bgs/bg1.png", "backgrounds/lvl_2_bgs/bg2.png",
            "backgrounds/lvl_2_bgs/bg3.png", "backgrounds/lvl_2_bgs/bg4.png",
            "backgrounds/lvl_2_bgs/bg5.png", "backgrounds/lvl_2_bgs/bg6.png",
            "backgrounds/lvl_2_bgs/bg7.png", "backgrounds/lvl_2_bgs/bg8.png"
        ]

        full_bg_filenames = base_bg_filenames * 2
        full_bg_filenames.append("backgrounds/lvl_2_bgs/bg9.png")

        first_raw = pygame.image.load(full_bg_filenames[0]).convert()
        first_trimmed = trim_black_side_borders(first_raw)
        bg_scale_ratio = self.screen_height / first_trimmed.get_height()
        self.bg_w = int(first_trimmed.get_width() * bg_scale_ratio) - 1

        self.bg_list = [pygame.transform.smoothscale(trim_black_side_borders(pygame.image.load(f).convert()),
                                                     (self.bg_w, self.screen_height)) for f in full_bg_filenames]
        self.max_backgrounds = len(full_bg_filenames)

        floor_img = pygame.image.load("mats/platforms/level 2 plats/lvl2_floor.png").convert_alpha()

        self.target_floor_h = 200
        floor_scale_ratio = self.target_floor_h / floor_img.get_height()
        self.floor_w = int(floor_img.get_width() * floor_scale_ratio) - 1
        self.floor_img = pygame.transform.smoothscale(floor_img, (self.floor_w, self.target_floor_h))
        self.floor_flip_img = pygame.transform.flip(self.floor_img, True, False)

        self.platform_image = pygame.image.load("mats/platforms/level 1 plats/plat31c.png").convert_alpha()

        try:
            plat2_raw = pygame.image.load("mats/platforms/level 2 plats/lvl2_p2.png").convert_alpha()
            plat3_raw = pygame.image.load("mats/platforms/level 2 plats/lvl2_p3.PNG").convert_alpha()
            self.platform_images = [trim_transparent_borders(plat2_raw), trim_transparent_borders(plat3_raw)]
        except pygame.error as e:
            print(f"Error loading Level 2 platforms: {e}")
            self.platform_images = [self.platform_image]

        self.bird_sheet_img = pygame.image.load(
            "spritesheets/enemies/lvl_1_enemies/gargoyle_grey_fly_ss.png").convert_alpha()

        enemy_scale = 0.55
        self.hd_walk_r, self.hd_walk_l = load_enemy_frames("spritesheets/enemies/lvl_2_enemies/helldog_walk_ss.png", 8,
                                                           enemy_scale)
        self.hd_atk_r, self.hd_atk_l = load_enemy_frames("spritesheets/enemies/lvl_2_enemies/helldog_attack_ss.png", 11,
                                                         enemy_scale)

        self.mau_walk_r, self.mau_walk_l = load_enemy_frames("spritesheets/enemies/lvl_2_enemies/mau_walk_ss.png", 10,
                                                             enemy_scale)
        self.mau_atk_r, self.mau_atk_l = load_enemy_frames("spritesheets/enemies/lvl_2_enemies/mau_attack_ss.png", 12,
                                                           enemy_scale)

        self.pk_walk_r, self.pk_walk_l = load_enemy_frames("spritesheets/enemies/lvl_2_enemies/pkgrim_walk_ss.png", 8,
                                                           enemy_scale)
        self.pk_atk_r, self.pk_atk_l = load_enemy_frames("spritesheets/enemies/lvl_2_enemies/pkgrim_attack_ss.png", 10,
                                                         enemy_scale)

    def reset(self):
        super().reset()
        self.helldog_group.empty()
        self.mau_group.empty()
        self.pkgrim_group.empty()

    def update(self, dt, camera_x, player_x, player_y, is_banner_active=False):
        for platform in list(self.platform_group):
            if platform.rect.right < camera_x - 4000: platform.kill()

        if camera_x + self.screen_width < self.level_end_x - 500:
            if len(self.platform_group) < 40:
                last_p = max(self.platform_group, key=lambda p: p.rect.x, default=None)
                p_x = (last_p.rect.right + random.randint(120, 290)) if last_p else (camera_x + self.screen_width + 100)
                chosen_plat_img = random.choice(self.platform_images)
                self.platform_group.add(
                    Platform(p_x, random.randint(self.plat_min_y, self.plat_max_y),
                             random.randint(self.plat_min_w, self.plat_max_w), chosen_plat_img,
                             self.platform_offset_ratio))

            if not is_banner_active and len(self.enemy_group) < 3 and random.randint(1, 60) == 1:
                side = random.choice(["left", "right"])
                ex = (camera_x - 150) if side == "left" else (camera_x + self.screen_width + 150)
                self.enemy_group.add(GreyGargoyleFlyer(ex, random.randint(200, 480), self.bird_sheet_img, 0.31,
                                                       forced_direction=1 if side == "left" else -1))

        current_bg_index = int(player_x // self.bg_w)

        if current_bg_index > self.last_spawned_bg_index and current_bg_index < self.max_backgrounds - 1:
            t_bg = current_bg_index + 1
            p_start, p_end = t_bg * self.bg_w, (t_bg + 1) * self.bg_w - 100

            num_enemies = random.randint(2, 3)
            segment_width = (p_end - p_start) // num_enemies

            for i in range(num_enemies):
                e_start = p_start + (i * segment_width)
                e_end = e_start + segment_width
                spawn_x = random.randint(e_start + 110, e_end - 110)

                spawn_choice = random.randint(1, 3)
                if spawn_choice == 1:
                    self.helldog_group.add(
                        Helldog(spawn_x, self.y_ground, e_start, e_end, self.hd_walk_r, self.hd_walk_l, self.hd_atk_r,
                                self.hd_atk_l))
                elif spawn_choice == 2:
                    self.pkgrim_group.add(
                        Pkgrim(spawn_x, self.y_ground, e_start, e_end, self.pk_walk_r, self.pk_walk_l, self.pk_atk_r,
                               self.pk_atk_l))
                else:
                    self.mau_group.add(
                        Mau(spawn_x, self.y_ground, e_start, e_end, self.mau_walk_r, self.mau_walk_l, self.mau_atk_r,
                            self.mau_atk_l))

            self.last_spawned_bg_index = current_bg_index

        self.enemy_group.update(camera_x, self.screen_width)
        self.helldog_group.update(camera_x, player_x, player_y)
        self.mau_group.update(camera_x, player_x, player_y)
        self.pkgrim_group.update(camera_x, player_x, player_y)

    def draw(self, screen, camera_x):
        super().draw(screen, camera_x)
        for group in [self.helldog_group, self.mau_group, self.pkgrim_group]:
            for enemy in group:
                if -200 < (x := enemy.rect.x - camera_x) < self.screen_width + 200:
                    screen.blit(enemy.image, (x, enemy.rect.top))


class Level_03(Level_01):
    def __init__(self, screen_width, screen_height):
        self.platform_offset_ratio = 0.22
        self.floor_y_offset = 0
        self.plat_min_w = 90
        self.plat_max_w = 200
        self.plat_min_y = 320
        self.plat_max_y = 625
        self.start_plat_widths = [180, 200, 160]
        super().__init__(screen_width, screen_height)

        self.azule_group = pygame.sprite.Group()
        self.titus_group = pygame.sprite.Group()
        self.lionel_group = pygame.sprite.Group()
        self.demented_group = pygame.sprite.Group()

    def load_assets(self):
        full_bg_filenames = []
        for i in range(1, 20):
            if i == 5:
                full_bg_filenames.append("backgrounds/lvl_3_bgs/castle5.PNG")
            else:
                full_bg_filenames.append(f"backgrounds/lvl_3_bgs/castle{i}.png")

        first_raw = pygame.image.load(full_bg_filenames[0]).convert()
        first_trimmed = trim_black_side_borders(first_raw)
        bg_scale_ratio = self.screen_height / first_trimmed.get_height()
        self.bg_w = int(first_trimmed.get_width() * bg_scale_ratio) - 1

        self.bg_list = [pygame.transform.smoothscale(trim_black_side_borders(pygame.image.load(f).convert()),
                                                     (self.bg_w, self.screen_height)) for f in full_bg_filenames]
        self.max_backgrounds = len(full_bg_filenames)

        floor_img = pygame.image.load("mats/platforms/level 3 plats/lvl3_floor.png").convert_alpha()
        self.target_floor_h = 200
        floor_scale_ratio = self.target_floor_h / floor_img.get_height()
        self.floor_w = int(floor_img.get_width() * floor_scale_ratio) - 1
        self.floor_img = pygame.transform.smoothscale(floor_img, (self.floor_w, self.target_floor_h))
        self.floor_flip_img = pygame.transform.flip(self.floor_img, True, False)

        self.platform_image = pygame.image.load("mats/platforms/level 1 plats/plat31c.png").convert_alpha()

        # Load custom Level 3 platforms
        try:
            p1_raw = pygame.image.load("mats/platforms/level 3 plats/lvl_3_plat1.png").convert_alpha()
            p2_raw = pygame.image.load("mats/platforms/level 3 plats/lvl_3_plat2.png").convert_alpha()
            p3_raw = pygame.image.load("mats/platforms/level 3 plats/lvl_3_plat3.png").convert_alpha()

            self.platform_images = [
                trim_transparent_borders(p1_raw),
                trim_transparent_borders(p2_raw),
                trim_transparent_borders(p3_raw)
            ]
        except pygame.error as e:
            print(f"Error loading Level 3 platforms: {e}")
            self.platform_images = [self.platform_image]

        self.bird_sheet_img = pygame.image.load(
            "spritesheets/enemies/lvl_1_enemies/gargoyle_grey_fly_ss.png").convert_alpha()

        # Load Azule's frames
        enemy_scale = 0.55
        self.azule_walk_r, self.azule_walk_l = load_enemy_frames("spritesheets/enemies/lvl_3_enemies/azule_walk_ss.png",
                                                                 8, enemy_scale)
        self.azule_atk_r, self.azule_atk_l = load_enemy_frames("spritesheets/enemies/lvl_3_enemies/azule_attack_ss.png",
                                                               12, enemy_scale)

        # Load Titus's frames
        titus_scale = 0.60
        self.titus_walk_r, self.titus_walk_l = load_enemy_frames("spritesheets/enemies/lvl_3_enemies/titus_walk_ss.png",
                                                                 8, titus_scale)
        self.titus_atk_r, self.titus_atk_l = load_enemy_frames("spritesheets/enemies/lvl_3_enemies/titus_attack_ss.png",
                                                               16, titus_scale)

        # Load Lionel's frames
        lionel_scale = 0.55
        self.lionel_walk_r, self.lionel_walk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_3_enemies/lionel_walk_ss.png", 8, lionel_scale)
        self.lionel_atk_r, self.lionel_atk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_3_enemies/lionel_attack_ss.png", 9, lionel_scale)

        # Load Demented's frames
        demented_scale = 0.55
        self.dem_walk_r, self.dem_walk_l = load_enemy_frames("spritesheets/enemies/lvl_3_enemies/demented_walk_ss.png",
                                                             8, demented_scale)
        self.dem_idle_r, self.dem_idle_l = load_enemy_frames("spritesheets/enemies/lvl_3_enemies/demented_idle_ss.png",
                                                             9, demented_scale)
        self.dem_atk_r, self.dem_atk_l = load_enemy_frames("spritesheets/enemies/lvl_3_enemies/demented_attack_ss.png",
                                                           10, demented_scale)

    def reset(self):
        super().reset()
        self.azule_group.empty()
        self.titus_group.empty()
        self.lionel_group.empty()
        self.demented_group.empty()

    def update(self, dt, camera_x, player_x, player_y, is_banner_active=False):
        for platform in list(self.platform_group):
            if platform.rect.right < camera_x - 4000:
                platform.kill()

        if camera_x + self.screen_width < self.level_end_x - 500:
            if len(self.platform_group) < 40:
                last_p = max(self.platform_group, key=lambda p: p.rect.x, default=None)
                p_x = (last_p.rect.right + random.randint(120, 290)) if last_p else (camera_x + self.screen_width + 100)
                chosen_plat_img = random.choice(self.platform_images)
                self.platform_group.add(
                    Platform(p_x, random.randint(self.plat_min_y, self.plat_max_y),
                             random.randint(self.plat_min_w, self.plat_max_w), chosen_plat_img,
                             self.platform_offset_ratio))

            if not is_banner_active and len(self.enemy_group) < 3 and random.randint(1, 60) == 1:
                side = random.choice(["left", "right"])
                ex = (camera_x - 150) if side == "left" else (camera_x + self.screen_width + 150)
                self.enemy_group.add(GreyGargoyleFlyer(ex, random.randint(200, 480), self.bird_sheet_img, 0.31,
                                                       forced_direction=1 if side == "left" else -1))

        current_bg_index = int(player_x // self.bg_w)

        if current_bg_index > self.last_spawned_bg_index and current_bg_index < self.max_backgrounds - 1:
            t_bg = current_bg_index + 1
            p_start, p_end = t_bg * self.bg_w, (t_bg + 1) * self.bg_w - 100

            num_enemies = random.randint(2, 3)
            segment_width = (p_end - p_start) // num_enemies

            for i in range(num_enemies):
                e_start = p_start + (i * segment_width)
                e_end = e_start + segment_width
                spawn_x = random.randint(e_start + 110, e_end - 110)

                spawn_choice = random.randint(1, 4)
                if spawn_choice == 1:
                    self.azule_group.add(
                        Azule(spawn_x, self.y_ground, e_start, e_end, self.azule_walk_r, self.azule_walk_l,
                              self.azule_atk_r, self.azule_atk_l)
                    )
                elif spawn_choice == 2:
                    self.titus_group.add(
                        Titus(spawn_x, self.y_ground, e_start, e_end, self.titus_walk_r, self.titus_walk_l,
                              self.titus_atk_r, self.titus_atk_l)
                    )
                elif spawn_choice == 3:
                    self.lionel_group.add(
                        Lionel(spawn_x, self.y_ground, e_start, e_end, self.lionel_walk_r, self.lionel_walk_l,
                               self.lionel_atk_r, self.lionel_atk_l)
                    )
                else:
                    self.demented_group.add(
                        Demented(spawn_x, self.y_ground, e_start, e_end, self.dem_walk_r, self.dem_walk_l,
                                 self.dem_idle_r, self.dem_idle_l, self.dem_atk_r, self.dem_atk_l)
                    )

            self.last_spawned_bg_index = current_bg_index

        self.enemy_group.update(camera_x, self.screen_width)
        self.azule_group.update(camera_x, player_x, player_y)
        self.titus_group.update(camera_x, player_x, player_y)
        self.lionel_group.update(camera_x, player_x, player_y)
        self.demented_group.update(camera_x, player_x, player_y)

    def draw(self, screen, camera_x):
        super().draw(screen, camera_x)
        for enemy in self.azule_group:
            if -200 < (x := enemy.rect.x - camera_x) < self.screen_width + 200:
                screen.blit(enemy.image, (x, enemy.rect.top))
        for enemy in self.titus_group:
            if -200 < (x := enemy.rect.x - camera_x) < self.screen_width + 200:
                screen.blit(enemy.image, (x, enemy.rect.top))
        for enemy in self.lionel_group:
            if -200 < (x := enemy.rect.x - camera_x) < self.screen_width + 200:
                screen.blit(enemy.image, (x, enemy.rect.top))
        for enemy in self.demented_group:
            if -200 < (x := enemy.rect.x - camera_x) < self.screen_width + 200:
                screen.blit(enemy.image, (x, enemy.rect.top))


class Level_04(Level_01):
    def __init__(self, screen_width, screen_height):
        self.platform_offset_ratio = 0.40
        self.floor_y_offset = 0
        self.plat_min_w = 90
        self.plat_max_w = 200
        self.plat_min_y = 320
        self.plat_max_y = 625
        self.start_plat_widths = [180, 200, 160]
        super().__init__(screen_width, screen_height)

        # Initialize the 6 new Level 4 specific groups
        self.elaine_group = pygame.sprite.Group()
        self.groundskeeper_group = pygame.sprite.Group()
        self.royalhh_group = pygame.sprite.Group()
        self.royalzombie_group = pygame.sprite.Group()
        self.zombie1_group = pygame.sprite.Group()
        self.zombie2_group = pygame.sprite.Group()

    def load_assets(self):
        # 1. Start background
        full_bg_filenames = ["backgrounds/lvl_4_bgs/gy_start.PNG"]

        # 2. Setup the loop section (gy1 through gy10)
        loop_bgs = [
            "backgrounds/lvl_4_bgs/gy1.png",
            "backgrounds/lvl_4_bgs/gy2.png",
            "backgrounds/lvl_4_bgs/gy3.PNG",
            "backgrounds/lvl_4_bgs/gy4.png",
            "backgrounds/lvl_4_bgs/gy5.PNG",
            "backgrounds/lvl_4_bgs/gy6.png",
            "backgrounds/lvl_4_bgs/gy7.png",
            "backgrounds/lvl_4_bgs/gy8.png",
            "backgrounds/lvl_4_bgs/gy9.png",
            "backgrounds/lvl_4_bgs/gy10.png"
        ]

        # 3. Add the loop sequence twice
        full_bg_filenames.extend(loop_bgs)
        full_bg_filenames.extend(loop_bgs)

        # 4. End background
        full_bg_filenames.append("backgrounds/lvl_4_bgs/gy_last.png")

        first_raw = pygame.image.load(full_bg_filenames[0]).convert()
        first_trimmed = trim_black_side_borders(first_raw)
        bg_scale_ratio = self.screen_height / first_trimmed.get_height()
        self.bg_w = int(first_trimmed.get_width() * bg_scale_ratio) - 1

        self.bg_list = [pygame.transform.smoothscale(trim_black_side_borders(pygame.image.load(f).convert()),
                                                     (self.bg_w, self.screen_height)) for f in full_bg_filenames]
        self.max_backgrounds = len(full_bg_filenames)

        # Load Custom Level 4 Floor
        raw_floor = pygame.image.load("mats/platforms/level 4 plats/lvl4_floor.png").convert_alpha()
        trimmed_floor = trim_transparent_borders(raw_floor)

        self.target_floor_h = 200
        floor_scale_ratio = self.target_floor_h / trimmed_floor.get_height()
        self.floor_w = int(trimmed_floor.get_width() * floor_scale_ratio) - 1
        self.floor_img = pygame.transform.smoothscale(trimmed_floor, (self.floor_w, self.target_floor_h))
        self.floor_flip_img = pygame.transform.flip(self.floor_img, True, False)

        self.platform_image = pygame.image.load("mats/platforms/level 1 plats/plat31c.png").convert_alpha()

        # Load custom Level 4 platforms (excluding skull plat 2)
        self.platform_images = []
        try:
            for i in [4, 5, 6]:
                plat_raw = pygame.image.load(f"mats/platforms/level 4 plats/lvl_4_plat{i}.png").convert_alpha()
                self.platform_images.append(trim_transparent_borders(plat_raw))
        except pygame.error as e:
            print(f"Error loading Level 4 platforms: {e}")
            if not self.platform_images:
                self.platform_images = [self.platform_image]

        # Load universal flyers
        self.bird_sheet_img = pygame.image.load(
            "spritesheets/enemies/lvl_1_enemies/gargoyle_grey_fly_ss.png").convert_alpha()

        # --- CUSTOM SCALES FOR EACH ENEMY ---
        elaine_scale = 0.60
        gk_scale = 0.65  # Increased to make the Groundskeeper bigger
        rhh_scale = 0.55  # Decreased to make the Royal Hound smaller
        rz_scale = 0.60
        z1_scale = 0.60
        z2_scale = 0.60

        self.elaine_walk_r, self.elaine_walk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_4_enemies/elaine_walk_ss.png", 8, elaine_scale)
        self.elaine_atk_r, self.elaine_atk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_4_enemies/elaine_attack_ss.png", 10, elaine_scale)
        self.gk_walk_r, self.gk_walk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_4_enemies/groundskeeper_walk_ss.png", 8, gk_scale)
        self.gk_idle_r, self.gk_idle_l = load_enemy_frames(
            "spritesheets/enemies/lvl_4_enemies/groundskeeper_idle_ss.png", 6, gk_scale)
        self.gk_atk_r, self.gk_atk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_4_enemies/groundskeeper_attack_ss.png", 8, gk_scale)
        self.rhh_walk_r, self.rhh_walk_l = load_enemy_frames("spritesheets/enemies/lvl_4_enemies/royalhh_walk_ss.png",
                                                             12, rhh_scale)
        self.rhh_atk_r, self.rhh_atk_l = load_enemy_frames("spritesheets/enemies/lvl_4_enemies/royalhh_attack_ss.png",
                                                           10, rhh_scale)
        self.rz_walk_r, self.rz_walk_l = load_enemy_frames("spritesheets/enemies/lvl_4_enemies/royalzombie_walk_ss.png",
                                                           8, rz_scale)
        self.rz_atk_r, self.rz_atk_l = load_enemy_frames("spritesheets/enemies/lvl_4_enemies/royalzombie_attack_ss.png",
                                                         11, rz_scale)
        self.z1_walk_r, self.z1_walk_l = load_enemy_frames("spritesheets/enemies/lvl_4_enemies/zombie1_walk_ss.png", 8,
                                                           z1_scale)
        self.z1_atk_r, self.z1_atk_l = load_enemy_frames("spritesheets/enemies/lvl_4_enemies/zombie1_attack_ss.png", 12,
                                                         z1_scale)
        self.z2_walk_r, self.z2_walk_l = load_enemy_frames("spritesheets/enemies/lvl_4_enemies/zombie2_walk_ss.png", 8,
                                                           z2_scale)
        self.z2_atk_r, self.z2_atk_l = load_enemy_frames("spritesheets/enemies/lvl_4_enemies/zombie2_attack_ss.png", 13,
                                                         z2_scale)

    def reset(self):
        super().reset()
        self.elaine_group.empty()
        self.groundskeeper_group.empty()
        self.royalhh_group.empty()
        self.royalzombie_group.empty()
        self.zombie1_group.empty()
        self.zombie2_group.empty()

    def update(self, dt, camera_x, player_x, player_y, is_banner_active=False):
        for platform in list(self.platform_group):
            if platform.rect.right < camera_x - 4000:
                platform.kill()

        if camera_x + self.screen_width < self.level_end_x - 500:
            if len(self.platform_group) < 40:
                last_p = max(self.platform_group, key=lambda p: p.rect.x, default=None)
                p_x = (last_p.rect.right + random.randint(120, 290)) if last_p else (camera_x + self.screen_width + 100)
                chosen_plat_img = random.choice(self.platform_images)
                self.platform_group.add(
                    Platform(p_x, random.randint(self.plat_min_y, self.plat_max_y),
                             random.randint(self.plat_min_w, self.plat_max_w), chosen_plat_img,
                             self.platform_offset_ratio))

            if not is_banner_active and len(self.enemy_group) < 3 and random.randint(1, 60) == 1:
                side = random.choice(["left", "right"])
                ex = (camera_x - 150) if side == "left" else (camera_x + self.screen_width + 150)
                self.enemy_group.add(GreyGargoyleFlyer(ex, random.randint(200, 480), self.bird_sheet_img, 0.31,
                                                       forced_direction=1 if side == "left" else -1))

        current_bg_index = int(player_x // self.bg_w)

        if current_bg_index > self.last_spawned_bg_index and current_bg_index < self.max_backgrounds - 1:
            t_bg = current_bg_index + 1
            p_start, p_end = t_bg * self.bg_w, (t_bg + 1) * self.bg_w - 100

            num_enemies = random.randint(2, 3)
            segment_width = (p_end - p_start) // num_enemies

            for i in range(num_enemies):
                e_start = p_start + (i * segment_width)
                e_end = e_start + segment_width
                spawn_x = random.randint(e_start + 110, e_end - 110)

                spawn_choice = random.randint(1, 6)
                if spawn_choice == 1:
                    self.elaine_group.add(
                        Elaine(spawn_x, self.y_ground, e_start, e_end, self.elaine_walk_r, self.elaine_walk_l,
                               self.elaine_atk_r, self.elaine_atk_l))
                elif spawn_choice == 2:
                    self.groundskeeper_group.add(
                        Groundskeeper(spawn_x, self.y_ground, e_start, e_end, self.gk_walk_r, self.gk_walk_l,
                                      self.gk_idle_r, self.gk_idle_l, self.gk_atk_r, self.gk_atk_l))
                elif spawn_choice == 3:
                    self.royalhh_group.add(
                        RoyalHH(spawn_x, self.y_ground, e_start, e_end, self.rhh_walk_r, self.rhh_walk_l,
                                self.rhh_atk_r, self.rhh_atk_l))
                elif spawn_choice == 4:
                    self.royalzombie_group.add(
                        RoyalZombie(spawn_x, self.y_ground, e_start, e_end, self.rz_walk_r, self.rz_walk_l,
                                    self.rz_atk_r, self.rz_atk_l))
                elif spawn_choice == 5:
                    self.zombie1_group.add(
                        Zombie1(spawn_x, self.y_ground, e_start, e_end, self.z1_walk_r, self.z1_walk_l, self.z1_atk_r,
                                self.z1_atk_l))
                else:
                    self.zombie2_group.add(
                        Zombie2(spawn_x, self.y_ground, e_start, e_end, self.z2_walk_r, self.z2_walk_l, self.z2_atk_r,
                                self.z2_atk_l))

            self.last_spawned_bg_index = current_bg_index

        self.enemy_group.update(camera_x, self.screen_width)
        self.elaine_group.update(camera_x, player_x, player_y)
        self.groundskeeper_group.update(camera_x, player_x, player_y)
        self.royalhh_group.update(camera_x, player_x, player_y)
        self.royalzombie_group.update(camera_x, player_x, player_y)
        self.zombie1_group.update(camera_x, player_x, player_y)
        self.zombie2_group.update(camera_x, player_x, player_y)

    def draw(self, screen, camera_x):
        super().draw(screen, camera_x)
        for group in [self.elaine_group, self.groundskeeper_group, self.royalhh_group, self.royalzombie_group,
                      self.zombie1_group, self.zombie2_group]:
            for enemy in group:
                if -200 < (x := enemy.rect.x - camera_x) < self.screen_width + 200:
                    screen.blit(enemy.image, (x, enemy.rect.top))


# --- NEW LEVEL 5 CLASS ---
class Level_05(Level_01):
    def __init__(self, screen_width, screen_height):
        self.platform_offset_ratio = 0.22
        self.floor_y_offset = 0
        self.plat_min_w = 90
        self.plat_max_w = 200
        self.plat_min_y = 320
        self.plat_max_y = 625
        self.start_plat_widths = [180, 200, 160]
        super().__init__(screen_width, screen_height)

        # Level 5 Specific Enemy Groups
        self.priestly_group = pygame.sprite.Group()
        self.realmwalker_group = pygame.sprite.Group()
        self.pursuer_group = pygame.sprite.Group()
        self.braid_group = pygame.sprite.Group()
        self.deadlight_group = pygame.sprite.Group()

    def load_assets(self):
        # 1. Setup the 16 background images
        full_bg_filenames = [f"backgrounds/lvl_5_bgs/backg{i}.png" for i in range(1, 17)]

        first_raw = pygame.image.load(full_bg_filenames[0]).convert()
        first_trimmed = trim_black_side_borders(first_raw)
        bg_scale_ratio = self.screen_height / first_trimmed.get_height()
        self.bg_w = int(first_trimmed.get_width() * bg_scale_ratio) - 1

        self.bg_list = [pygame.transform.smoothscale(trim_black_side_borders(pygame.image.load(f).convert()),
                                                     (self.bg_w, self.screen_height)) for f in full_bg_filenames]
        self.max_backgrounds = len(full_bg_filenames)

        # Load Custom Level 5 Floor
        raw_floor = pygame.image.load("mats/platforms/level 5 plats/lvl5_floor.png").convert_alpha()
        trimmed_floor = trim_transparent_borders(raw_floor)

        self.target_floor_h = 200
        floor_scale_ratio = self.target_floor_h / trimmed_floor.get_height()
        self.floor_w = int(trimmed_floor.get_width() * floor_scale_ratio) - 1
        self.floor_img = pygame.transform.smoothscale(trimmed_floor, (self.floor_w, self.target_floor_h))
        self.floor_flip_img = pygame.transform.flip(self.floor_img, True, False)

        self.platform_image = pygame.image.load("mats/platforms/level 1 plats/plat31c.png").convert_alpha()

        # Load custom Level 5 platforms
        self.platform_images = []
        try:
            for i in range(1, 4):
                plat_raw = pygame.image.load(f"mats/platforms/level 5 plats/lvl_5_p{i}.png").convert_alpha()
                self.platform_images.append(trim_transparent_borders(plat_raw))
        except pygame.error as e:
            print(f"Error loading Level 5 platforms: {e}")
            if not self.platform_images:
                self.platform_images = [self.platform_image]

        # Load universal flyers
        self.bird_sheet_img = pygame.image.load(
            "spritesheets/enemies/lvl_1_enemies/gargoyle_grey_fly_ss.png").convert_alpha()

        # --- ENEMY SCALES & FRAMES ---
        scale = 0.65
        braid_scale = 0.70
        self.priestly_walk_r, self.priestly_walk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_5_enemies/priestly_walk_ss.png", 8, scale)
        self.priestly_atk_r, self.priestly_atk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_5_enemies/priestly_attack_ss.png", 11, scale)

        self.realmwalker_walk_r, self.realmwalker_walk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_5_enemies/realmwalker_walk_ss.png", 8, scale)
        self.realmwalker_atk_r, self.realmwalker_atk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_5_enemies/realmwalker_attack_ss.png", 10, scale)

        self.pursuer_walk_r, self.pursuer_walk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_5_enemies/pursuer_walk_ss.png", 8, scale)
        self.pursuer_atk_r, self.pursuer_atk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_5_enemies/pursuer_attack_ss.png", 12, scale)

        self.braid_walk_r, self.braid_walk_l = load_enemy_frames("spritesheets/enemies/lvl_5_enemies/braid_walk_ss.png",
                                                                 8, braid_scale)
        self.braid_atk_r, self.braid_atk_l = load_enemy_frames("spritesheets/enemies/lvl_5_enemies/braid_attack_ss.png",
                                                               10, braid_scale)

        self.deadlight_walk_r, self.deadlight_walk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_5_enemies/deadlight_walk_ss.png", 8, scale)
        self.deadlight_atk_r, self.deadlight_atk_l = load_enemy_frames(
            "spritesheets/enemies/lvl_5_enemies/deadlight_attack_ss.png", 10, scale)

    def reset(self):
        super().reset()
        self.priestly_group.empty()
        self.realmwalker_group.empty()
        self.pursuer_group.empty()
        self.braid_group.empty()
        self.deadlight_group.empty()

    def update(self, dt, camera_x, player_x, player_y, is_banner_active=False):
        for platform in list(self.platform_group):
            if platform.rect.right < camera_x - 4000:
                platform.kill()

        if camera_x + self.screen_width < self.level_end_x - 500:
            if len(self.platform_group) < 40:
                last_p = max(self.platform_group, key=lambda p: p.rect.x, default=None)
                p_x = (last_p.rect.right + random.randint(120, 290)) if last_p else (camera_x + self.screen_width + 100)
                chosen_plat_img = random.choice(self.platform_images)
                self.platform_group.add(
                    Platform(p_x, random.randint(self.plat_min_y, self.plat_max_y),
                             random.randint(self.plat_min_w, self.plat_max_w), chosen_plat_img,
                             self.platform_offset_ratio))

            if not is_banner_active and len(self.enemy_group) < 3 and random.randint(1, 60) == 1:
                side = random.choice(["left", "right"])
                ex = (camera_x - 150) if side == "left" else (camera_x + self.screen_width + 150)
                self.enemy_group.add(GreyGargoyleFlyer(ex, random.randint(200, 480), self.bird_sheet_img, 0.31,
                                                       forced_direction=1 if side == "left" else -1))

        current_bg_index = int(player_x // self.bg_w)

        if current_bg_index > self.last_spawned_bg_index and current_bg_index < self.max_backgrounds - 1:
            t_bg = current_bg_index + 1
            p_start, p_end = t_bg * self.bg_w, (t_bg + 1) * self.bg_w - 100

            num_enemies = random.randint(2, 3)
            segment_width = (p_end - p_start) // num_enemies

            for i in range(num_enemies):
                e_start = p_start + (i * segment_width)
                e_end = e_start + segment_width
                spawn_x = random.randint(e_start + 110, e_end - 110)

                spawn_choice = random.randint(1, 5)
                if spawn_choice == 1:
                    self.priestly_group.add(
                        Priestly(spawn_x, self.y_ground, e_start, e_end, self.priestly_walk_r, self.priestly_walk_l,
                                 self.priestly_atk_r, self.priestly_atk_l))
                elif spawn_choice == 2:
                    self.realmwalker_group.add(
                        Realmwalker(spawn_x, self.y_ground, e_start, e_end, self.realmwalker_walk_r,
                                    self.realmwalker_walk_l, self.realmwalker_atk_r, self.realmwalker_atk_l))
                elif spawn_choice == 3:
                    self.pursuer_group.add(
                        Pursuer(spawn_x, self.y_ground, e_start, e_end, self.pursuer_walk_r, self.pursuer_walk_l,
                                self.pursuer_atk_r, self.pursuer_atk_l))
                elif spawn_choice == 4:
                    self.braid_group.add(
                        Braid(spawn_x, self.y_ground, e_start, e_end, self.braid_walk_r, self.braid_walk_l,
                              self.braid_atk_r, self.braid_atk_l))
                else:
                    self.deadlight_group.add(Deadlight(spawn_x, self.y_ground, e_start, e_end, self.deadlight_walk_r,
                                                       self.deadlight_walk_l, self.deadlight_atk_r,
                                                       self.deadlight_atk_l))

            self.last_spawned_bg_index = current_bg_index

        self.enemy_group.update(camera_x, self.screen_width)
        self.priestly_group.update(camera_x, player_x, player_y)
        self.realmwalker_group.update(camera_x, player_x, player_y)
        self.pursuer_group.update(camera_x, player_x, player_y)
        self.braid_group.update(camera_x, player_x, player_y)
        self.deadlight_group.update(camera_x, player_x, player_y)

    def draw(self, screen, camera_x):
        super().draw(screen, camera_x)
        for group in [self.priestly_group, self.realmwalker_group, self.pursuer_group, self.braid_group,
                      self.deadlight_group]:
            for enemy in group:
                if -200 < (x := enemy.rect.x - camera_x) < self.screen_width + 200:
                    screen.blit(enemy.image, (x, enemy.rect.top))


# --- NEW LEVEL 6 CLASS ---
class Level_06(Level_01):
    def __init__(self, screen_width, screen_height):
        self.platform_offset_ratio = 0.22
        self.floor_y_offset = 0
        self.plat_min_w = 90
        self.plat_max_w = 200
        self.plat_min_y = 320
        self.plat_max_y = 625
        self.start_plat_widths = [180, 200, 160]
        super().__init__(screen_width, screen_height)

        self.victoria_group = pygame.sprite.Group()
        self.kali_group = pygame.sprite.Group()
        self.kimoura_group = pygame.sprite.Group()
        self.cassie_group = pygame.sprite.Group()
        self.silas_group = pygame.sprite.Group()
        self.thad_group = pygame.sprite.Group()

    def load_assets(self):
        # 1. Setup the 17 background images
        full_bg_filenames = [f"backgrounds/lvl_6_bgs/{i}_bg6.png" for i in range(1, 18)]

        first_raw = pygame.image.load(full_bg_filenames[0]).convert()
        first_trimmed = trim_black_side_borders(first_raw)
        bg_scale_ratio = self.screen_height / first_trimmed.get_height()
        self.bg_w = int(first_trimmed.get_width() * bg_scale_ratio) - 1

        self.bg_list = [pygame.transform.smoothscale(trim_black_side_borders(pygame.image.load(f).convert()),
                                                     (self.bg_w, self.screen_height)) for f in full_bg_filenames]
        self.max_backgrounds = len(full_bg_filenames)

        # Load Custom Level 6 Floor
        raw_floor = pygame.image.load("mats/platforms/level 6 plats/lvl6_floor.png").convert_alpha()
        trimmed_floor = trim_transparent_borders(raw_floor)

        self.target_floor_h = 200
        floor_scale_ratio = self.target_floor_h / trimmed_floor.get_height()
        self.floor_w = int(trimmed_floor.get_width() * floor_scale_ratio) - 1
        self.floor_img = pygame.transform.smoothscale(trimmed_floor, (self.floor_w, self.target_floor_h))
        self.floor_flip_img = pygame.transform.flip(self.floor_img, True, False)

        self.platform_image = pygame.image.load("mats/platforms/level 1 plats/plat31c.png").convert_alpha()

        # Load custom Level 6 platforms
        self.platform_images = []
        try:
            for i in range(1, 4):
                plat_raw = pygame.image.load(f"mats/platforms/level 6 plats/lvl_6_p{i}.png").convert_alpha()
                self.platform_images.append(trim_transparent_borders(plat_raw))
        except pygame.error as e:
            print(f"Error loading Level 6 platforms: {e}")
            if not self.platform_images:
                self.platform_images = [self.platform_image]

        # Load universal flyers
        self.bird_sheet_img = pygame.image.load(
            "spritesheets/enemies/lvl_1_enemies/gargoyle_grey_fly_ss.png").convert_alpha()

        # --- ENEMY SCALES & FRAMES ---
        vic_scale = 0.60
        self.vic_walk_r, self.vic_walk_l = load_enemy_frames("spritesheets/enemies/lvl_6_enemies/victoria_walk_ss.png",
                                                             8, vic_scale)
        self.vic_atk_r, self.vic_atk_l = load_enemy_frames("spritesheets/enemies/lvl_6_enemies/victoria_attack_ss.png",
                                                           12, vic_scale)

        self.kali_walk_r, self.kali_walk_l = load_enemy_frames("spritesheets/enemies/lvl_6_enemies/kali_walk_ss.png",
                                                               8, vic_scale)
        self.kali_atk_r, self.kali_atk_l = load_enemy_frames("spritesheets/enemies/lvl_6_enemies/kali_attack_ss.png",
                                                             10, vic_scale)

        self.kimoura_walk_r, self.kimoura_walk_l = load_enemy_frames("spritesheets/enemies/lvl_6_enemies/kimoura_walk_ss.png",
                                                                     8, vic_scale)
        self.kimoura_atk_r, self.kimoura_atk_l = load_enemy_frames("spritesheets/enemies/lvl_6_enemies/kimoura_attack_ss.png",
                                                                   12, vic_scale)

        self.cassie_walk_r, self.cassie_walk_l = load_enemy_frames("spritesheets/enemies/lvl_6_enemies/cassie_walk_ss.png",
                                                                   8, vic_scale)
        self.cassie_atk_r, self.cassie_atk_l = load_enemy_frames("spritesheets/enemies/lvl_6_enemies/cassie_attack_ss.png",
                                                                 12, vic_scale)

        self.silas_walk_r, self.silas_walk_l = load_enemy_frames("spritesheets/enemies/lvl_6_enemies/silas_walk_ss.png",
                                                                 8, vic_scale)
        self.silas_atk_r, self.silas_atk_l = load_enemy_frames("spritesheets/enemies/lvl_6_enemies/silas_attack_ss.png",
                                                               12, vic_scale)

        self.thad_walk_r, self.thad_walk_l = load_enemy_frames("spritesheets/enemies/lvl_6_enemies/thad_walk_ss.png",
                                                               8, vic_scale)
        self.thad_atk_r, self.thad_atk_l = load_enemy_frames("spritesheets/enemies/lvl_6_enemies/thad_attack_ss.png",
                                                             12, vic_scale)

    def reset(self):
        super().reset()
        self.victoria_group.empty()
        self.kali_group.empty()
        self.kimoura_group.empty()
        self.cassie_group.empty()
        self.silas_group.empty()
        self.thad_group.empty()

    def update(self, dt, camera_x, player_x, player_y, is_banner_active=False):
        for platform in list(self.platform_group):
            if platform.rect.right < camera_x - 4000:
                platform.kill()

        if camera_x + self.screen_width < self.level_end_x - 500:
            if len(self.platform_group) < 40:
                last_p = max(self.platform_group, key=lambda p: p.rect.x, default=None)
                p_x = (last_p.rect.right + random.randint(120, 290)) if last_p else (camera_x + self.screen_width + 100)
                chosen_plat_img = random.choice(self.platform_images)
                self.platform_group.add(
                    Platform(p_x, random.randint(self.plat_min_y, self.plat_max_y),
                             random.randint(self.plat_min_w, self.plat_max_w), chosen_plat_img,
                             self.platform_offset_ratio))

            if not is_banner_active and len(self.enemy_group) < 3 and random.randint(1, 60) == 1:
                side = random.choice(["left", "right"])
                ex = (camera_x - 150) if side == "left" else (camera_x + self.screen_width + 150)
                self.enemy_group.add(GreyGargoyleFlyer(ex, random.randint(200, 480), self.bird_sheet_img, 0.31,
                                                       forced_direction=1 if side == "left" else -1))

        current_bg_index = int(player_x // self.bg_w)

        if current_bg_index > self.last_spawned_bg_index and current_bg_index < self.max_backgrounds - 1:
            t_bg = current_bg_index + 1
            p_start, p_end = t_bg * self.bg_w, (t_bg + 1) * self.bg_w - 100

            num_enemies = random.randint(2, 3)
            segment_width = (p_end - p_start) // num_enemies

            for i in range(num_enemies):
                e_start = p_start + (i * segment_width)
                e_end = e_start + segment_width
                spawn_x = random.randint(e_start + 110, e_end - 110)

                spawn_choice = random.randint(1, 6)
                if spawn_choice == 1:
                    self.victoria_group.add(
                        Victoria(spawn_x, self.y_ground, e_start, e_end, self.vic_walk_r, self.vic_walk_l, self.vic_atk_r,
                                 self.vic_atk_l))
                elif spawn_choice == 2:
                    self.kali_group.add(
                        Kali(spawn_x, self.y_ground, e_start, e_end, self.kali_walk_r, self.kali_walk_l, self.kali_atk_r,
                             self.kali_atk_l))
                elif spawn_choice == 3:
                    self.kimoura_group.add(
                        Kimoura(spawn_x, self.y_ground, e_start, e_end, self.kimoura_walk_r, self.kimoura_walk_l, self.kimoura_atk_r,
                                self.kimoura_atk_l))
                elif spawn_choice == 4:
                    self.cassie_group.add(
                        Cassie(spawn_x, self.y_ground, e_start, e_end, self.cassie_walk_r, self.cassie_walk_l, self.cassie_atk_r,
                               self.cassie_atk_l))
                elif spawn_choice == 5:
                    self.silas_group.add(
                        Silas(spawn_x, self.y_ground, e_start, e_end, self.silas_walk_r, self.silas_walk_l, self.silas_atk_r,
                              self.silas_atk_l))
                else:
                    self.thad_group.add(
                        Thad(spawn_x, self.y_ground, e_start, e_end, self.thad_walk_r, self.thad_walk_l, self.thad_atk_r,
                             self.thad_atk_l))

            self.last_spawned_bg_index = current_bg_index

        self.enemy_group.update(camera_x, self.screen_width)
        self.victoria_group.update(camera_x, player_x, player_y)
        self.kali_group.update(camera_x, player_x, player_y)
        self.kimoura_group.update(camera_x, player_x, player_y)
        self.cassie_group.update(camera_x, player_x, player_y)
        self.silas_group.update(camera_x, player_x, player_y)
        self.thad_group.update(camera_x, player_x, player_y)

    def draw(self, screen, camera_x):
        super().draw(screen, camera_x)
        for group in [self.victoria_group, self.kali_group, self.kimoura_group, self.cassie_group, self.silas_group, self.thad_group]:
            for enemy in group:
                if -200 < (x := enemy.rect.x - camera_x) < self.screen_width + 200:
                    screen.blit(enemy.image, (x, enemy.rect.top))