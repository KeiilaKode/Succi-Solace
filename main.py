# --- main.py ---#
import pygame
import sys
import os
from pygame import mixer, Color

# OOP Imports
from player import Player
from entities import Projectile, Merchant, Merchant_UI
from level import Level_01, Level_02, Level_03, Level_04, Merchant_Room

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

# ==========================================
# INITIALIZATION & AUDIO
# ==========================================
mixer.init()
pygame.init()

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Succi Solace")

try:
    game_icon = pygame.image.load("mats/pink design.png").convert_alpha()
    pygame.display.set_icon(game_icon)
except pygame.error:
    pass

clock = pygame.time.Clock()
FPS = 60

try:

    pygame.mixer.music.load("mats/Prelude and Fughetta in D minor, BWV 899 (Pedal-Harpsichord).mp3")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1, 0.0)  # Start playing immediately on the main menu

    jump_fx = pygame.mixer.Sound("mats/Swoosh.mp3")
    jump_fx.set_volume(0.3)
    death_fx = pygame.mixer.Sound("mats/Pause.mp3")
    death_fx.set_volume(0.6)
    cast_fx = pygame.mixer.Sound("mats/cast.mp3")
    cast_fx.set_volume(0.4)
    explode_fx = pygame.mixer.Sound("mats/explode.mp3")
    explode_fx.set_volume(0.2)

    merchant_voice_fx = pygame.mixer.Sound("mats/merchant entrance.mp3")
    merchant_voice_fx.set_volume(0.6)

    laugh_fx = pygame.mixer.Sound("mats/laugh_bb.mp3")
    laugh_fx.set_volume(0.6)

    departure_fx = pygame.mixer.Sound("mats/merchant_departure.mp3")
    departure_fx.set_volume(0.6)

    merchant_greet_lvl_2_fx = pygame.mixer.Sound("mats/merchant greet lvl 2.mp3")
    merchant_greet_lvl_2_fx.set_volume(0.6)

except pygame.error as e:
    print(f"Audio Load Warning: {e}")

# ==========================================
# UI & PLAYER ASSET LOADING
# ==========================================
WHITE, BLACK, PINK, LIGHT_GRAY = (255, 255, 255), (0, 0, 0), (253, 117, 234), (180, 180, 180)
font_small = pygame.font.SysFont("Lucida Sans", 20)
font_big = pygame.font.SysFont("Lucida Sans", 48)


def get_sprites_from_sheet(filename, approx_width=810, target_h=1080):
    sheet = pygame.image.load(filename).convert_alpha()
    sw, sh = sheet.get_size()
    if sh == target_h - 1:
        padded = pygame.Surface((sw, target_h), pygame.SRCALPHA)
        padded.fill((0, 0, 0, 0))
        padded.blit(sheet, (0, 0))
        sheet, sh = padded, target_h
    num_frames = max(1, round(sw / approx_width))
    fw = sw // num_frames
    return [pygame.transform.smoothscale(sheet.subsurface((i * fw, 0, fw, sh)), (fw, target_h)) for i in
            range(num_frames)]


animations = {
    "idle": get_sprites_from_sheet("spritsheets/S_IDLE_NB.png"),
    "walk": get_sprites_from_sheet("spritsheets/S_WALK_NB.png"),
    "run": get_sprites_from_sheet("spritsheets/S_RUN_NB.png"),
    "jump": get_sprites_from_sheet("spritsheets/S_JUMP_NB.png"),
    "run_jump": get_sprites_from_sheet("spritsheets/S_RUN_JUMP_NB.png"),
    "duck": get_sprites_from_sheet("spritsheets/S_DUCK_NB.png"),
    "attack": get_sprites_from_sheet("spritsheets/S_ATTACK_NB.png"),
    "run_attack": get_sprites_from_sheet("spritsheets/S_RUNSHOT_NB.png")
}
animation_speeds = {"idle": 175, "walk": 130, "run": 75, "jump": 80, "run_jump": 50, "duck": 50, "attack": 90,
                    "run_attack": 75}
animation_loops = {"idle": True, "walk": True, "run": True, "jump": False, "run_jump": False, "duck": False,
                   "attack": False, "run_attack": False}
animation_scale_corrections = {"idle": 1.0, "walk": 1.08, "run": 1.08, "jump": 1.0, "run_jump": 1.08, "duck": 1.0,
                               "attack": 2.8, "run_attack": 1.08}

fireball_img = pygame.image.load("spritsheets/fireball.png").convert_alpha()
explode_img = pygame.image.load("spritsheets/explode_NB.png").convert_alpha()

purple_fireball_img = pygame.image.load("spritsheets/purple_spell.png").convert_alpha()
purple_explode_img = pygame.image.load("spritsheets/purple_ball_explode.png").convert_alpha()

end_image = pygame.transform.smoothscale(pygame.image.load("backgrounds/death_screen.png").convert_alpha(),
                                         (SCREEN_WIDTH, SCREEN_HEIGHT))

# --- Pause Menu Tombstone ---
try:
    pause_bg_raw = pygame.image.load("backgrounds/pause1.png").convert_alpha()
    pause_bg = pygame.transform.smoothscale(pause_bg_raw, (1200, 1150))
except pygame.error:
    pause_bg = None

# --- Death Screen Overlay ---
try:
    death_overlay_raw = pygame.image.load("backgrounds/death overlay.png").convert_alpha()
    death_overlay = pygame.transform.smoothscale(death_overlay_raw, (1100, 1150))
except pygame.error:
    death_overlay = None


def draw_text(text, font, text_col, x, y): screen.blit(font.render(text, True, text_col), (x, y))


def draw_panel(rem):
    pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, 30))
    pygame.draw.line(screen, PINK, (0, 30), (SCREEN_WIDTH, 30), 3)
    draw_text(f"REM: {rem}", font_small, WHITE, 10, 5)


def draw_health_bar(health, max_health):
    if max_health > 1:
        pygame.draw.rect(screen, LIGHT_GRAY, (10, 35, 150, 20), 2)
        if health > 0:
            segment_w = 146 // max_health
            for i in range(health):
                pygame.draw.rect(screen, (50, 255, 50), (12 + i * segment_w, 37, segment_w - 2, 16))


# ==========================================
# MAIN MENU CLASS
# ==========================================
class MainMenu:
    def __init__(self, w, h):
        try:
            self.bg = pygame.transform.smoothscale(pygame.image.load("backgrounds/start_bg.png").convert(), (w, h))

            raw_play = pygame.image.load("mats/play.png").convert_alpha()
            raw_controls = pygame.image.load("mats/controls.png").convert_alpha()
            raw_load = pygame.image.load("mats/load.png").convert_alpha()

            # Base Sizes
            self.play_b = pygame.transform.smoothscale(raw_play, (260, 140))
            self.ctrl_b = pygame.transform.smoothscale(raw_controls, (260, 140))
            self.load_b = pygame.transform.smoothscale(raw_load, (190, 190))

            # Hover Sizes (+10% scaling)
            self.play_h = pygame.transform.smoothscale(raw_play, (286, 154))
            self.ctrl_h = pygame.transform.smoothscale(raw_controls, (286, 154))
            self.load_h = pygame.transform.smoothscale(raw_load, (209, 209))

            # Positions aligning with the tombstones
            self.play_rect = self.play_b.get_rect(center=(685, h // 2 + 80))
            self.ctrl_rect = self.ctrl_b.get_rect(center=(185, h // 2 + 180))
            self.load_rect = self.load_b.get_rect(center=(1190, h // 2 + 180))

        except pygame.error as e:
            print(f"Menu Asset Error: {e}")
            self.bg = pygame.Surface((w, h))

        self.sub_menu = None
        self.font_title = pygame.font.SysFont("Lucida Sans", 48)
        self.font_text = pygame.font.SysFont("Lucida Sans", 30)

    def update(self, mouse_pos, mouse_click):
        if mouse_click:
            if self.sub_menu:
                self.sub_menu = None  # Click anywhere to close sub-menu
            else:
                if self.play_rect.collidepoint(mouse_pos):
                    return "PLAY"
                elif self.ctrl_rect.collidepoint(mouse_pos):
                    self.sub_menu = "CONTROLS"
                elif self.load_rect.collidepoint(mouse_pos):
                    self.sub_menu = "LOAD"
        return None

    def draw(self, screen, mouse_pos):
        screen.blit(self.bg, (0, 0))

        # CONTROLS Button
        if self.ctrl_rect.collidepoint(mouse_pos) and not self.sub_menu:
            screen.blit(self.ctrl_h, self.ctrl_h.get_rect(center=self.ctrl_rect.center))
        else:
            screen.blit(self.ctrl_b, self.ctrl_rect)

        # PLAY Button
        if self.play_rect.collidepoint(mouse_pos) and not self.sub_menu:
            screen.blit(self.play_h, self.play_h.get_rect(center=self.play_rect.center))
        else:
            screen.blit(self.play_b, self.play_rect)

        # LOAD Button
        if self.load_rect.collidepoint(mouse_pos) and not self.sub_menu:
            screen.blit(self.load_h, self.load_h.get_rect(center=self.load_rect.center))
        else:
            screen.blit(self.load_b, self.load_rect)

        # SUB-MENUS OVERLAYS
        if self.sub_menu == "LOAD":
            overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            screen.blit(overlay, (0, 0))
            text = self.font_title.render("Save Slots (JSON Logic Coming Soon!)", True, (253, 117, 234))
            screen.blit(text, text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50)))
            sub = self.font_text.render("Click anywhere to return", True, (180, 180, 180))
            screen.blit(sub, sub.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 20)))

        elif self.sub_menu == "CONTROLS":
            overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            screen.blit(overlay, (0, 0))
            lines = [
                ("CONTROLS", (253, 117, 234)),
                ("WASD / Arrows : Move & Duck", (100, 200, 255)),
                ("Shift : Run", (100, 200, 255)),
                ("Space : Jump", (100, 200, 255)),
                ("Left Mouse : Cast Red Fireball", (100, 200, 255)),
                ("Right Mouse : Cast Purple Magic", (100, 200, 255)),
                ("E Key : Enter / Exit Merchant", (100, 200, 255)),
                ("P / ESC : Pause", (253, 117, 234)),
                ("", (0, 0, 0)),
                ("(Click anywhere to return)", (180, 180, 180))
            ]
            for i, (line, color) in enumerate(lines):
                text = self.font_text.render(line, True, color)
                screen.blit(text,
                            text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 150 + (i * 40))))


# ==========================================
# GAME STATE SETUP
# ==========================================
current_state = "MAIN_MENU"
last_completed_level = "LEVEL_1"
checkpoint = 1
game_over, paused = False, False
camera_x = 0.0
rem = 0
is_level_2_merchant = False

global_merchant_sold_out = {
    "Health Potion": False,
    "Teal Potion": False,
    "Emerald Potion": False,
    "Pink Potion": False,
    "Mysterious Potion": False,
    "Silver Potion": False,
    "Wings Potion": False,
    "Purple Potion": False,
    "Mana Potion": False,
    "Rainbow Potion": False,
    "Royal Potion": False,
    "Gold Potion": False
}

player_has_purple_magic = False
player_has_rainbow_dance = False

main_menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
current_level = Level_01(SCREEN_WIDTH, SCREEN_HEIGHT)
merchant_room = Merchant_Room(SCREEN_WIDTH, SCREEN_HEIGHT)
merchant_npc = None
merchant_ui = None
exiting_merchant = False
exit_timer = 0

succi = Player(400.0, current_level.y_ground, animations, animation_speeds, animation_scale_corrections, jump_fx,
               cast_fx)
projectile_group = pygame.sprite.Group()

# ==========================================
# MAIN GAME LOOP
# ==========================================
run = True
while run:
    dt_ms = clock.tick(FPS)
    dt = dt_ms / 1000.0
    keys = pygame.key.get_pressed()

    mouse_click = False
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                if current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"]:
                    if not game_over: paused = not paused

            # M Key warped to work in ALL Levels
            elif event.key == pygame.K_m and current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"]:
                succi.x = current_level.door_world_x
                camera_x = current_level.level_end_x - SCREEN_WIDTH
            # N Key warped to work in ALL Levels to jump to Level 4
            elif event.key == pygame.K_n and current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"]:
                current_state = "LEVEL_4"
                checkpoint = 4
                current_level = Level_04(SCREEN_WIDTH, SCREEN_HEIGHT)
                succi = Player(400.0, current_level.y_ground, animations, animation_speeds, animation_scale_corrections,
                               jump_fx, cast_fx)
                succi.max_health = 3
                succi.health = 3
                camera_x = 0.0
                projectile_group.empty()

                # Level 4 Music
                pygame.mixer.music.load("mats/Polonaise in F sharp minor, Op. 44.mp3")
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1, 0.0)

        # Handle Mouse Down Events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_click = True  # Allows menu/merchant interaction

            # --- MOUSE CLICK COMBAT CONTROLS ---
            if not game_over and not paused and current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"]:
                is_moving = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_a] or keys[pygame.K_d]
                is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

                if event.button == 1:  # Left Click: Standard Fireball
                    succi.trigger_attack(is_running, is_moving)
                    succi.current_spell_type = "normal"

                elif event.button == 3:  # Right Click: Purple Spell (Only if purchased)
                    if player_has_purple_magic:
                        succi.trigger_attack(is_running, is_moving)
                        succi.current_spell_type = "purple"

    if current_state == "MAIN_MENU":
        action = main_menu.update(mouse_pos, mouse_click)
        if action == "PLAY":
            current_state = "LEVEL_1"
            current_level.reset()
            succi = Player(400.0, current_level.y_ground, animations, animation_speeds, animation_scale_corrections,
                           jump_fx, cast_fx)
            rem = 0
            checkpoint = 1
            camera_x = 0.0
            game_over = False
            paused = False

            # Switch to the Level 1 music when entering the game
            pygame.mixer.music.load("mats/Phaneroza-_No-Umbra-No-Penumbra.mp3")
            pygame.mixer.music.play(-1, 0.0)

    elif not game_over and not paused:

        if current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"]:
            succi.update(keys, dt, dt_ms, current_level.platform_group, animation_loops)

            if succi.x > current_level.level_end_x - 100:
                succi.x = current_level.level_end_x - 100

            if (succi.attacking and
                    succi.current_frame == (8 if succi.current_anim == "attack" else 4) and
                    not succi.fireball_spawned):
                spawn_x = succi.x + (90 if succi.facing_right else -90)

                # Check the assigned spell type to spawn the correct projectile
                is_purple = getattr(succi, 'current_spell_type', 'normal') == "purple"
                active_fireball = purple_fireball_img if is_purple else fireball_img
                active_explode = purple_explode_img if is_purple else explode_img

                projectile_group.add(
                    Projectile(spawn_x, succi.y - 180, 1 if succi.facing_right else -1,
                               active_fireball, active_explode, 0.28))
                succi.fireball_spawned = True
                try:
                    cast_fx.play()
                except NameError:
                    pass

            screen_x = succi.x - camera_x
            if screen_x > SCREEN_WIDTH * 0.75:
                camera_x += (screen_x - SCREEN_WIDTH * 0.75)
            elif screen_x < SCREEN_WIDTH * 0.25:
                camera_x -= (SCREEN_WIDTH * 0.25 - screen_x)

            if camera_x > current_level.level_end_x - SCREEN_WIDTH:
                camera_x = current_level.level_end_x - SCREEN_WIDTH
            if camera_x < 0: camera_x = 0

            current_level.update(dt, camera_x, succi.x, succi.y)
            projectile_group.update(dt, camera_x, SCREEN_WIDTH)

            for proj in projectile_group:
                if proj.state == "fly":
                    enemy_targets = [current_level.enemy_group]
                    if current_state == "LEVEL_1":
                        enemy_targets.extend([current_level.demon_group, current_level.skeleton_group])
                    elif current_state == "LEVEL_2":
                        enemy_targets.extend(
                            [current_level.helldog_group, current_level.mau_group, current_level.pkgrim_group])
                    elif current_state == "LEVEL_3":
                        enemy_targets.extend([
                            current_level.azule_group,
                            current_level.titus_group,
                            current_level.lionel_group,
                            current_level.demented_group
                        ])
                    elif current_state == "LEVEL_4":
                        # UPDATED TO TARGET ALL 6 NEW ENEMIES
                        enemy_targets.extend([
                            current_level.elaine_group,
                            current_level.groundskeeper_group,
                            current_level.royalhh_group,
                            current_level.royalzombie_group,
                            current_level.zombie1_group,
                            current_level.zombie2_group
                        ])

                    for group in enemy_targets:
                        for target in group:
                            ty = target.rect.top if hasattr(target, 'state') else target.rect.y
                            if proj.mask.overlap(target.mask, (target.rect.x - proj.rect.x, ty - proj.rect.y)):
                                proj.explode()
                                if hasattr(target, 'take_damage'):
                                    if target.take_damage():
                                        rem += target.rem_value
                                        target.kill()
                                else:
                                    rem += target.rem_value
                                    target.kill()
                                try:
                                    explode_fx.play()
                                except NameError:
                                    pass
                                break
                        if proj.state != "fly": break

        elif current_state == "MERCHANT":
            if merchant_npc:
                active_merchant_audio = merchant_greet_lvl_2_fx if is_level_2_merchant else merchant_voice_fx
                merchant_npc.update(dt_ms, active_merchant_audio)
                if merchant_npc.state == "idle" and merchant_ui is not None:
                    if not exiting_merchant:
                        bought_item = merchant_ui.update(mouse_pos, mouse_click, rem)
                        if bought_item:
                            try:
                                laugh_fx.play()
                            except NameError:
                                pass

                            merchant_ui.sold_out[bought_item] = True
                            merchant_ui.selected_item = None

                        if bought_item == "Health Potion":
                            rem -= 50
                            succi.max_health = 3
                            succi.health = 3
                        elif bought_item == "Mana Potion":
                            rem -= 75
                        elif bought_item == "Wings Potion":
                            rem -= 150
                        elif bought_item == "Purple Potion":
                            rem -= 75
                            player_has_purple_magic = True
                        elif bought_item == "Rainbow Potion":
                            rem -= 100
                            player_has_rainbow_dance = True

                        if keys[pygame.K_e]:
                            exiting_merchant = True
                            exit_timer = pygame.time.get_ticks()
                            try:
                                departure_fx.play()
                            except NameError:
                                pass

                    if exiting_merchant:
                        if pygame.time.get_ticks() - exit_timer > 8000:
                            # Level Transition Logic
                            if last_completed_level == "LEVEL_1":
                                current_state = "LEVEL_2"
                                current_level = Level_02(SCREEN_WIDTH, SCREEN_HEIGHT)
                                checkpoint = 2
                            elif last_completed_level == "LEVEL_2":
                                current_state = "LEVEL_3"
                                current_level = Level_03(SCREEN_WIDTH, SCREEN_HEIGHT)
                                checkpoint = 3
                            elif last_completed_level == "LEVEL_3":
                                current_state = "LEVEL_4"
                                current_level = Level_04(SCREEN_WIDTH, SCREEN_HEIGHT)
                                checkpoint = 4
                            elif last_completed_level == "LEVEL_4":
                                current_state = "LEVEL_1"
                                current_level = Level_01(SCREEN_WIDTH, SCREEN_HEIGHT)
                                checkpoint = 1

                            succi.x = 400.0
                            camera_x = 0.0
                            exiting_merchant = False
                            merchant_npc = None
                            merchant_ui = None

                            if current_state == "LEVEL_4":
                                pygame.mixer.music.load("mats/Polonaise in F sharp minor, Op. 44.mp3")
                            elif current_state == "LEVEL_3":
                                pygame.mixer.music.load("mats/Ballade no. 1 in G minor, Op. 23.mp3")
                            elif current_state == "LEVEL_2":
                                pygame.mixer.music.load("mats/Toccata and Fugue in Dm, BWV 565.mp3")
                            else:
                                pygame.mixer.music.load("mats/Phaneroza-_No-Umbra-No-Penumbra.mp3")

                            pygame.mixer.music.set_volume(0.2)
                            pygame.mixer.music.play(-1, 0.0)

    # ==========================================
    # DRAWING PHASE
    # ==========================================
    if current_state == "MAIN_MENU":
        main_menu.draw(screen, mouse_pos)

    else:
        if not game_over:
            if current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"]:
                current_level.draw(screen, camera_x)
                succi_blit_x, succi_blit_y = succi.draw(screen, camera_x)
                if abs(succi.x - current_level.door_world_x) < 150:
                    draw_text("Press 'E' to Enter", font_small, Color("turquoise1"), succi_blit_x + 20,
                              succi_blit_y - 80)

                for proj in projectile_group:
                    if -200 < (px := proj.rect.x - camera_x) < SCREEN_WIDTH + 200: screen.blit(proj.image,
                                                                                               (px, proj.rect.y))

                enemy_groups_to_check = [current_level.enemy_group]
                if current_state == "LEVEL_1":
                    enemy_groups_to_check.extend([current_level.demon_group, current_level.skeleton_group])
                elif current_state == "LEVEL_2":
                    enemy_groups_to_check.extend(
                        [current_level.helldog_group, current_level.mau_group, current_level.pkgrim_group])
                elif current_state == "LEVEL_3":
                    enemy_groups_to_check.extend([
                        current_level.azule_group,
                        current_level.titus_group,
                        current_level.lionel_group,
                        current_level.demented_group
                    ])
                elif current_state == "LEVEL_4":
                    # UPDATED TO CHECK COLLISION WITH ALL 6 NEW ENEMIES
                    enemy_groups_to_check.extend([
                        current_level.elaine_group,
                        current_level.groundskeeper_group,
                        current_level.royalhh_group,
                        current_level.royalzombie_group,
                        current_level.zombie1_group,
                        current_level.zombie2_group
                    ])

                for group in enemy_groups_to_check:
                    for target in group:
                        tx = target.rect.x - camera_x
                        if -200 < tx < SCREEN_WIDTH + 200:
                            ty = target.rect.top if hasattr(target, 'state') else target.rect.y
                            if target.mask.overlap(succi.mask, (succi_blit_x - tx, succi_blit_y - ty)):
                                if succi.take_damage():
                                    game_over = True
                                    try:
                                        death_fx.play()
                                    except NameError:
                                        pass

                # --- Localized Merchant Door Check ---
                if abs(succi.x - current_level.door_world_x) < 150:
                    if keys[pygame.K_e]:
                        last_completed_level = current_state
                        is_level_2_merchant = (current_state in ["LEVEL_2", "LEVEL_3", "LEVEL_4"])
                        current_state = "MERCHANT"
                        pygame.mixer.music.stop()

                        if is_level_2_merchant:
                            merchant_npc = Merchant(SCREEN_WIDTH, SCREEN_HEIGHT,
                                                    "spritsheets/merchant_lvl2_sheet.png",
                                                    columns=10, rows=7, target_duration=12200)
                        else:
                            merchant_npc = Merchant(SCREEN_WIDTH, SCREEN_HEIGHT,
                                                    "spritsheets/merchant_lvl1_sheet.png",
                                                    columns=10, rows=6)

                        merchant_ui = Merchant_UI(SCREEN_WIDTH, SCREEN_HEIGHT, global_merchant_sold_out)
                        succi.x = 400.0

            elif current_state == "MERCHANT":
                if merchant_npc and merchant_npc.state == "intro":
                    merchant_npc.draw(screen)
                elif merchant_npc and merchant_npc.state == "idle" and merchant_ui:
                    merchant_ui.draw(screen, mouse_pos, rem)
                    if not exiting_merchant:
                        draw_text("Press 'E' to Leave", font_big, Color("turquoise1"), 1000, 25)
                    else:
                        draw_text("Good Luck...", font_big, Color("turquoise1"), 1000, 25)

            draw_panel(rem)
            draw_health_bar(succi.health, succi.max_health)

            # Pause Menu
            if paused:
                # Draw the dark transparent background
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 100))
                screen.blit(overlay, (0, 0))

                # --- 1. IMAGE PLACEMENT ---
                if pause_bg:
                    pb_rect = pause_bg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
                    screen.blit(pause_bg, pb_rect)

                # --- 2. TEXT PLACEMENT ---
                start_y = SCREEN_HEIGHT // 2 + 30
                text_x = SCREEN_WIDTH // 2 + 15

                draw_text("GAME PAUSED", font_big, Color("turquoise1"), text_x - 165, start_y)
                draw_text("Press 'P' or 'ESC' to Resume", font_small, LIGHT_GRAY, text_x - 145, start_y + 55)

                ctrl_y = start_y + 115
                ctrl_x = text_x - 130

                draw_text("CONTROLS:", font_small, PINK, text_x - 60, ctrl_y)
                draw_text("WASD / Arrows : Move & Duck", font_small, Color("blue1"), ctrl_x, ctrl_y + 35)
                draw_text("Shift      : Run", font_small, Color("blue1"), ctrl_x, ctrl_y + 60)
                draw_text("Space      : Jump", font_small, Color("blue1"), ctrl_x, ctrl_y + 85)
                draw_text("Left Click : Cast Fireball", font_small, Color("blue1"), ctrl_x, ctrl_y + 110)
                draw_text("E Key      : Enter/Exit", font_small, Color("blue1"), ctrl_x, ctrl_y + 135)
                draw_text("P / ESC    : Pause", font_small, PINK, ctrl_x, ctrl_y + 160)

        # Death screen
        else:
            # 1. Draw the purple graveyard background
            screen.blit(end_image, (0, 0))

            # 2. Draw the Gargoyle Tombstone overlay slightly shifted down
            if death_overlay:
                do_rect = death_overlay.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
                screen.blit(death_overlay, do_rect)

            # 3. Center the text and restore pink lines inside the tombstone
            center_x = SCREEN_WIDTH // 2
            start_y = SCREEN_HEIGHT // 2 - 35  # Shifted down slightly for perfect vertical centering

            # Reduced line width (from 175 to 155) to tuck them safely away from the edges
            line_w = 155
            line_left = center_x - line_w
            line_right = center_x + line_w + 40
            line_color = Color("plum1")
            line_thickness = 6


            # Helper function to automatically center and scale text perfectly

            def draw_centered_scaled_text(text, font, color, y_pos, scale):
                raw_text = font.render(text, True, color)
                scaled_w = int(raw_text.get_width() * scale)
                scaled_h = int(raw_text.get_height() * scale)
                scaled_text = pygame.transform.smoothscale(raw_text, (scaled_w, scaled_h))
                text_rect = scaled_text.get_rect(center=(center_x + 20, y_pos))
                screen.blit(scaled_text, text_rect)


            # Top Line
            pygame.draw.line(screen, line_color, (line_left, start_y - 45), (line_right, start_y - 45), line_thickness)

            # Title (Scaled down to 0.45 so it fits cleanly inside the lines)
            draw_centered_scaled_text("YOUR SOUL HAS BEEN LOST!!", font_big, Color("turquoise1"), start_y, 0.50)

            # Middle Line 1
            pygame.draw.line(screen, line_color, (line_left, start_y + 45), (line_right, start_y + 45), line_thickness)

            # Replaced Score with Level Reached placeholder
            draw_centered_scaled_text(f"DIED ON: {current_state.replace('_', ' ')}", font_big, Color("turquoise1"),
                                      start_y + 95, 0.45)

            # Middle Line 2
            pygame.draw.line(screen, line_color, (line_left, start_y + 145), (line_right, start_y + 145),
                             line_thickness)

            # Level Retry Subtext Logic (Scaled to stay inside the borders and centered)
            if checkpoint == 4:
                draw_centered_scaled_text("PRESS SPACE TO RETRY LEVEL 4", font_small, Color("turquoise1"),
                                          start_y + 185,
                                          1.0)
                draw_centered_scaled_text("PRESS '1' TO RESTART AT LEVEL 1", font_small, LIGHT_GRAY, start_y + 215, 0.8)
            elif checkpoint == 3:
                draw_centered_scaled_text("PRESS SPACE TO RETRY LEVEL 3", font_small, Color("turquoise1"),
                                          start_y + 185,
                                          1.0)
                draw_centered_scaled_text("PRESS '1' TO RESTART AT LEVEL 1", font_small, LIGHT_GRAY, start_y + 215, 0.8)
            elif checkpoint == 2:
                draw_centered_scaled_text("PRESS SPACE TO RETRY LEVEL 2", font_small, Color("turquoise1"),
                                          start_y + 185,
                                          1.0)
                draw_centered_scaled_text("PRESS '1' TO RESTART AT LEVEL 1", font_small, LIGHT_GRAY, start_y + 215, 0.8)
            else:
                # Single line centered perfectly between mid-line 2 and bottom line
                draw_centered_scaled_text("PRESS SPACE TO TRY AGAIN", font_small, Color("turquoise1"), start_y + 200,
                                          1.2)
            # Bottom Line
            pygame.draw.line(screen, line_color, (line_left, start_y + 255), (line_right, start_y + 255),
                             line_thickness)

            restart_action = None

            if pygame.key.get_pressed()[pygame.K_SPACE]:
                restart_action = checkpoint

            elif checkpoint in [2, 3, 4] and pygame.key.get_pressed()[pygame.K_1]:
                restart_action = 1
                checkpoint = 1

            if restart_action is not None:
                game_over, paused, camera_x, rem = False, False, 0.0, 0
                old_max_health = succi.max_health if hasattr(succi, 'max_health') else 1

                if restart_action == 4:
                    current_state = "LEVEL_4"
                    current_level = Level_04(SCREEN_WIDTH, SCREEN_HEIGHT)
                elif restart_action == 3:
                    current_state = "LEVEL_3"
                    current_level = Level_03(SCREEN_WIDTH, SCREEN_HEIGHT)
                elif restart_action == 2:
                    current_state = "LEVEL_2"
                    current_level = Level_02(SCREEN_WIDTH, SCREEN_HEIGHT)
                else:
                    if current_state != "LEVEL_1":
                        pygame.mixer.music.load("mats/Phaneroza-_No-Umbra-No-Penumbra.mp3")
                        pygame.mixer.music.set_volume(0.2)
                        pygame.mixer.music.play(-1, 0.0)

                    current_state = "LEVEL_1"
                    current_level = Level_01(SCREEN_WIDTH, SCREEN_HEIGHT)
                    old_max_health = 1

                current_level.reset()
                merchant_npc = None
                merchant_ui = None
                succi = Player(400.0, current_level.y_ground, animations, animation_speeds, animation_scale_corrections,
                               jump_fx, cast_fx)

                succi.max_health = old_max_health
                succi.health = old_max_health
                projectile_group.empty()

                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1, 0.0)

    pygame.display.update()

mixer.quit()
pygame.quit()
sys.exit()