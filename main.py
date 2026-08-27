import pygame
import sys
import os
import json
from pygame import mixer, Color
import config

# OOP Imports
from player import Player
from entities import Projectile, Merchant, Companion
from level import Level_01, Level_02, Level_03, Level_04, Merchant_Room

# Isolated UI components
from ui import MainMenu, Merchant_UI, PauseMenu, DeathScreen, HUD, draw_text

# SAVE FILE CREATION #

if getattr(sys, 'frozen', False):
    # When packaged as an .exe, save exactly where the .exe is located
    SAVE_DIR = os.path.join(os.path.dirname(sys.executable), "saves")
else:
    # When running in PyCharm
    SAVE_DIR = os.path.abspath("saves")

os.makedirs(SAVE_DIR, exist_ok=True)


def save_game(slot, save_name):
    data = {
        "save_name": save_name,
        "level": current_state,
        "checkpoint": checkpoint,
        "rem": rem,
        "health": succi.health,
        "max_health": succi.max_health,

        "player_has_melee": player_has_melee,
        "player_has_purple_magic": player_has_purple_magic,
        "player_has_blue_magic": player_has_blue_magic,
        "player_has_rainbow_dance": player_has_rainbow_dance,
        "player_has_tinera": player_has_tinera,
        "tinera_active": tinera_active,

        "spell_left": succi.spell_left_click,
        "spell_right": succi.spell_right_click
    }

    with open(f"{SAVE_DIR}/save{slot}.json", "w") as f:
        json.dump(data, f, indent=4)
    print(f"Game saved successfully to slot {slot}!")


def load_game(slot):
    global current_state, checkpoint, rem
    global player_has_melee, player_has_purple_magic, player_has_blue_magic
    global player_has_rainbow_dance, player_has_tinera, tinera_active
    global succi, current_level

    try:
        with open(f"{SAVE_DIR}/save{slot}.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"No save file found in slot {slot}.")
        return None

    current_state = data["level"]
    checkpoint = data["checkpoint"]
    rem = data["rem"]

    player_has_melee = data["player_has_melee"]
    player_has_purple_magic = data["player_has_purple_magic"]
    player_has_blue_magic = data["player_has_blue_magic"]
    player_has_rainbow_dance = data["player_has_rainbow_dance"]
    player_has_tinera = data["player_has_tinera"]
    tinera_active = data["tinera_active"]

    if current_state == "LEVEL_4":
        current_level = Level_04(SCREEN_WIDTH, SCREEN_HEIGHT)
    elif current_state == "LEVEL_3":
        current_level = Level_03(SCREEN_WIDTH, SCREEN_HEIGHT)
    elif current_state == "LEVEL_2":
        current_level = Level_02(SCREEN_WIDTH, SCREEN_HEIGHT)
    else:
        current_level = Level_01(SCREEN_WIDTH, SCREEN_HEIGHT)

    succi = Player(400.0, current_level.y_ground, animations, animation_speeds,
                   animation_scale_corrections, jump_fx, cast_fx)

    succi.health = data["health"]
    succi.max_health = data["max_health"]
    succi.spell_left_click = data["spell_left"]
    succi.spell_right_click = data["spell_right"]

    return data["save_name"]


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
    game_icon = pygame.image.load("mats/ui/pink design.png").convert_alpha()
    pygame.display.set_icon(game_icon)
except pygame.error:
    pass

clock = pygame.time.Clock()
FPS = 60

try:
    pygame.mixer.music.load("mats/audio/Prelude and Fughetta in D minor, BWV 899 (Pedal-Harpsichord).mp3")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1, 0.0)

    jump_fx = pygame.mixer.Sound("mats/audio/Swoosh.mp3")
    jump_fx.set_volume(0.3)
    death_fx = pygame.mixer.Sound("mats/audio/Pause.mp3")
    death_fx.set_volume(0.6)
    cast_fx = pygame.mixer.Sound("mats/audio/cast.mp3")
    cast_fx.set_volume(0.4)
    explode_fx = pygame.mixer.Sound("mats/audio/explode.mp3")
    explode_fx.set_volume(0.2)

    merchant_voice_fx = pygame.mixer.Sound("mats/audio/merchant entrance.mp3")
    merchant_voice_fx.set_volume(0.6)
    laugh_fx = pygame.mixer.Sound("mats/audio/laugh_bb.mp3")
    laugh_fx.set_volume(0.6)
    departure_fx = pygame.mixer.Sound("mats/audio/merchant_departure.mp3")
    departure_fx.set_volume(0.6)
    merchant_greet_lvl_2_fx = pygame.mixer.Sound("mats/audio/merchant greet lvl 2.mp3")
    merchant_greet_lvl_2_fx.set_volume(0.6)

except pygame.error as e:
    print(f"Audio Load Warning: {e}")

# ==========================================
# PLAYER & COMPANION ASSET LOADING
# ==========================================
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
    "idle": get_sprites_from_sheet("spritesheets/succi's sheets/S_IDLE_NB.png"),
    "walk": get_sprites_from_sheet("spritesheets/succi's sheets/S_WALK_NB.png"),
    "run": get_sprites_from_sheet("spritesheets/succi's sheets/S_RUN_NB.png"),
    "jump": get_sprites_from_sheet("spritesheets/succi's sheets/S_JUMP_NB.png"),
    "run_jump": get_sprites_from_sheet("spritesheets/succi's sheets/S_RUN_JUMP_NB.png"),
    "duck": get_sprites_from_sheet("spritesheets/succi's sheets/S_DUCK_NB.png"),
    "attack": get_sprites_from_sheet("spritesheets/succi's sheets/S_ATTACK_NB.png"),
    "run_attack": get_sprites_from_sheet("spritesheets/succi's sheets/S_RUNSHOT_NB.png"),
    "kick": get_sprites_from_sheet("spritesheets/succi's sheets/S_KICK_NB.png"),
    "jump_kick": get_sprites_from_sheet("spritesheets/succi's sheets/S_FLYINGKICK_NB.png")
}

animation_speeds = {"idle": 175, "walk": 130, "run": 75, "jump": 80, "run_jump": 50, "duck": 50, "attack": 90,
                    "run_attack": 75, "kick": 60, "jump_kick": 55}
animation_loops = {"idle": True, "walk": True, "run": True, "jump": False, "run_jump": False, "duck": False,
                   "attack": False, "run_attack": False, "kick": False, "jump_kick": False}
animation_scale_corrections = {"idle": 1.0, "walk": 1.08, "run": 1.08, "jump": 1.1, "run_jump": 1.1, "duck": 1.0,
                               "attack": 2.8, "run_attack": 1.08, "kick": 2.6, "jump_kick": 2.4}

fireball_img = pygame.image.load("spritesheets/spell sheets/fireball.png").convert_alpha()
explode_img = pygame.image.load("spritesheets/spell sheets/explode_NB.png").convert_alpha()
purple_fireball_img = pygame.image.load("spritesheets/spell sheets/purple_spell.png").convert_alpha()
purple_explode_img = pygame.image.load("spritesheets/spell sheets/purple_ball_explode.png").convert_alpha()

blueball_img = pygame.image.load("spritesheets/spell sheets/blueball_ss.png").convert_alpha()
blue_explode_img = pygame.image.load("spritesheets/spell sheets/blueball_explode_ss.png").convert_alpha()
rainball_img = pygame.image.load("spritesheets/spell sheets/rainball_ss.png").convert_alpha()
rainbow_explode_img = pygame.image.load("spritesheets/spell sheets/rainball_explode_ss.png").convert_alpha()

try:
    raw_tinera_icon = pygame.image.load("mats/ui/icon_tinera.png").convert_alpha()
    tinera_icon = pygame.transform.smoothscale(raw_tinera_icon, (55, 55))
except pygame.error:
    tinera_icon = None

try:
    raw_tinera_frames = get_sprites_from_sheet("spritesheets/pet sheets/Tinera_ss.png")
    tinera_frames = [pygame.transform.smoothscale(f, (int(810 * 0.15), int(1080 * 0.15))) for f in raw_tinera_frames]
except pygame.error as e:
    print(f"Error loading Tinera companion: {e}")
    tinera_frames = []

# ==========================================
# GAME STATE & UI SETUP
# ==========================================
current_state = "MAIN_MENU"
last_completed_level = "LEVEL_1"
checkpoint = 1
game_over, paused = False, False
camera_x = 0.0
rem = 0
is_level_2_merchant = False

global_merchant_sold_out = {
    "Health Potion": False, "Teal Potion": False, "Emerald Potion": False, "Pink Potion": False,
    "Mysterious Potion": False, "Silver Potion": False, "Wings Potion": False, "Purple Potion": False,
    "Blue Potion": False, "Rainbow Potion": False, "Royal Potion": False, "Gold Potion": False
}

player_has_purple_magic = False
player_has_rainbow_dance = False
player_has_melee = False
player_has_blue_magic = False
player_has_tinera = False
tinera_active = True

hud = HUD()
main_menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
pause_menu = PauseMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
death_screen = DeathScreen(SCREEN_WIDTH, SCREEN_HEIGHT)

current_level = Level_01(SCREEN_WIDTH, SCREEN_HEIGHT)
merchant_room = Merchant_Room(SCREEN_WIDTH, SCREEN_HEIGHT)
merchant_npc = None
merchant_ui = None
exiting_merchant = False
exit_timer = 0

succi = Player(400.0, current_level.y_ground, animations, animation_speeds, animation_scale_corrections, jump_fx,
               cast_fx)
tinera_companion = Companion(tinera_frames) if tinera_frames else None
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
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            # --- TYPING CUSTOM SAVE NAME LOGIC ---
            if paused and pause_menu.save_state == "TYPE":
                if event.key == pygame.K_RETURN:
                    custom_name = pause_menu.save_input_text.strip() or f"Save_0{pause_menu.selected_save_slot}"
                    save_game(pause_menu.selected_save_slot, custom_name)
                    pause_menu.save_state = None
                elif event.key == pygame.K_ESCAPE:
                    pause_menu.save_state = None
                elif event.key == pygame.K_BACKSPACE:
                    pause_menu.save_input_text = pause_menu.save_input_text[:-1]
                else:
                    if len(pause_menu.save_input_text) < 20:
                        pause_menu.save_input_text += event.unicode
            else:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    if current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"]:
                        if not game_over:
                            paused = not paused
                            if not paused:
                                pause_menu.save_state = None  # Reset state when unpausing

                elif event.key == pygame.K_m and current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"]:
                    succi.x = current_level.door_world_x
                    camera_x = current_level.level_end_x - SCREEN_WIDTH
                elif event.key == pygame.K_n and current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"]:
                    current_state = "LEVEL_4"
                    checkpoint = 4
                    current_level = Level_04(SCREEN_WIDTH, SCREEN_HEIGHT)
                    succi = Player(400.0, current_level.y_ground, animations, animation_speeds,
                                   animation_scale_corrections,
                                   jump_fx, cast_fx)
                    succi.max_health = 3
                    succi.health = 3
                    camera_x = 0.0
                    projectile_group.empty()
                    pygame.mixer.music.load("mats/audio/Polonaise in F sharp minor, Op. 44.mp3")
                    pygame.mixer.music.set_volume(0.2)
                    pygame.mixer.music.play(-1, 0.0)

                elif event.key == pygame.K_3 and current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"]:
                    if player_has_melee and not paused and not game_over:
                        succi.trigger_kick()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_click = True

            if not game_over and not paused and current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"]:
                is_moving = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_a] or keys[pygame.K_d]
                is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

                if event.button == 1:
                    succi.trigger_attack(is_running, is_moving)
                    succi.current_spell_type = succi.spell_left_click

                elif event.button == 3:
                    if succi.spell_right_click is not None:
                        succi.trigger_attack(is_running, is_moving)
                        succi.current_spell_type = succi.spell_right_click

                elif event.button == 2:
                    if player_has_melee:
                        succi.trigger_kick()

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

            pygame.mixer.music.load("mats/audio/Phaneroza-_No-Umbra-No-Penumbra.mp3")
            pygame.mixer.music.play(-1, 0.0)

        elif type(action) is dict:
            if action.get("action") == "LOAD":
                loaded_name = load_game(action["slot"])
                if loaded_name:
                    camera_x = 0.0
                    game_over = False
                    paused = False
                    projectile_group.empty()

                    if current_state == "LEVEL_4":
                        pygame.mixer.music.load("mats/audio/Polonaise in F sharp minor, Op. 44.mp3")
                    elif current_state == "LEVEL_3":
                        pygame.mixer.music.load("mats/audio/Ballade no. 1 in G minor, Op. 23.mp3")
                    elif current_state == "LEVEL_2":
                        pygame.mixer.music.load("mats/audio/Toccata and Fugue in Dm, BWV 565.mp3")
                    else:
                        pygame.mixer.music.load("mats/audio/Phaneroza-_No-Umbra-No-Penumbra.mp3")

                    pygame.mixer.music.set_volume(0.2)
                    pygame.mixer.music.play(-1, 0.0)

            elif action.get("action") == "DELETE":
                try:
                    os.remove(f"{SAVE_DIR}/save{action['slot']}.json")
                    print(f"Deleted save slot {action['slot']}.")
                except FileNotFoundError:
                    pass
                main_menu._load_save_data()  # Refresh UI slots

    elif not game_over and not paused:
        if current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"]:
            succi.update(keys, dt, dt_ms, current_level.platform_group, animation_loops)

            if succi.x > current_level.level_end_x - 100:
                succi.x = current_level.level_end_x - 100

            if (succi.attacking and
                    succi.current_frame == (8 if succi.current_anim == "attack" else 4) and
                    not succi.fireball_spawned):

                spawn_x = succi.x + (90 if succi.facing_right else -90)
                spell_type = getattr(succi, 'current_spell_type', 'normal')

                if spell_type == "purple":
                    active_fireball, active_explode, f_scale, e_scale, e_offset = purple_fireball_img, purple_explode_img, 0.28, 0.28, 0
                elif spell_type == "blue":
                    active_fireball, active_explode, f_scale, e_scale, e_offset = blueball_img, blue_explode_img, 0.7, 0.2, 65
                elif spell_type == "rainbow":
                    active_fireball, active_explode, f_scale, e_scale, e_offset = rainball_img, rainbow_explode_img, 0.7, 0.2, 0
                else:
                    active_fireball, active_explode, f_scale, e_scale, e_offset = fireball_img, explode_img, 0.28, 0.28, 0

                projectile_group.add(
                    Projectile(spawn_x, succi.y - 180, 1 if succi.facing_right else -1, active_fireball, active_explode,
                               f_scale, e_scale, e_offset)
                )
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
            if camera_x < 0:
                camera_x = 0

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
                        enemy_targets.extend(
                            [current_level.azule_group, current_level.titus_group, current_level.lionel_group,
                             current_level.demented_group])
                    elif current_state == "LEVEL_4":
                        enemy_targets.extend(
                            [current_level.elaine_group, current_level.groundskeeper_group, current_level.royalhh_group,
                             current_level.royalzombie_group, current_level.zombie1_group, current_level.zombie2_group])

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
                        if proj.state != "fly":
                            break

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

                            if bought_item not in ["Teal Potion", "Pink Potion"]:
                                merchant_ui.sold_out[bought_item] = True

                            merchant_ui.selected_item = None

                        if bought_item == "Health Potion":
                            rem -= 50
                            succi.max_health = 3
                            succi.health = 3

                        elif bought_item == "Teal Potion":
                            rem -= 50
                            succi.health = min(succi.health + 3, succi.max_health)

                        elif bought_item == "Emerald Potion":
                            rem -= 150
                            succi.max_health += 2
                            succi.health = succi.max_health

                        elif bought_item == "Pink Potion":
                            rem -= 100
                            succi.health = min(succi.health + 5, succi.max_health)

                        elif bought_item == "Gold Potion":
                            rem -= 250
                            succi.max_health += 1
                            succi.health = succi.max_health

                        elif bought_item == "Silver Potion":
                            rem -= 50
                            player_has_melee = True

                        elif bought_item == "Blue Potion":
                            rem -= 50
                            player_has_blue_magic = True
                            if succi.spell_right_click is None:
                                succi.spell_right_click = "blue"

                        elif bought_item == "Wings Potion":
                            rem -= 150

                        elif bought_item == "Purple Potion":
                            rem -= 50
                            player_has_purple_magic = True
                            if succi.spell_right_click is None:
                                succi.spell_right_click = "purple"

                        elif bought_item == "Rainbow Potion":
                            rem -= 50
                            player_has_rainbow_dance = True
                            if succi.spell_right_click is None:
                                succi.spell_right_click = "rainbow"

                        elif bought_item == "Royal Potion":
                            rem -= 50
                            player_has_tinera = True
                            tinera_active = True

                        if keys[pygame.K_e]:
                            exiting_merchant = True
                            exit_timer = pygame.time.get_ticks()
                            try:
                                departure_fx.play()
                            except NameError:
                                pass

                    if exiting_merchant:
                        if pygame.time.get_ticks() - exit_timer > 8000:
                            if last_completed_level == "LEVEL_1":
                                current_state, current_level, checkpoint = "LEVEL_2", Level_02(SCREEN_WIDTH,
                                                                                               SCREEN_HEIGHT), 2
                            elif last_completed_level == "LEVEL_2":
                                current_state, current_level, checkpoint = "LEVEL_3", Level_03(SCREEN_WIDTH,
                                                                                               SCREEN_HEIGHT), 3
                            elif last_completed_level == "LEVEL_3":
                                current_state, current_level, checkpoint = "LEVEL_4", Level_04(SCREEN_WIDTH,
                                                                                               SCREEN_HEIGHT), 4
                            elif last_completed_level == "LEVEL_4":
                                current_state, current_level, checkpoint = "LEVEL_1", Level_01(SCREEN_WIDTH,
                                                                                               SCREEN_HEIGHT), 1

                            succi.x = 400.0
                            camera_x = 0.0
                            exiting_merchant = False
                            merchant_npc = None
                            merchant_ui = None

                            if current_state == "LEVEL_4":
                                pygame.mixer.music.load("mats/audio/Polonaise in F sharp minor, Op. 44.mp3")
                            elif current_state == "LEVEL_3":
                                pygame.mixer.music.load("mats/audio/Ballade no. 1 in G minor, Op. 23.mp3")
                            elif current_state == "LEVEL_2":
                                pygame.mixer.music.load("mats/audio/Toccata and Fugue in Dm, BWV 565.mp3")
                            else:
                                pygame.mixer.music.load("mats/audio/Phaneroza-_No-Umbra-No-Penumbra.mp3")

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

                if player_has_tinera and tinera_active and tinera_companion:
                    stable_screen_x = succi.x - camera_x
                    stable_screen_y = succi.y
                    tinera_companion.update(stable_screen_x, stable_screen_y, succi.facing_right)
                    tinera_companion.draw(screen)

                if abs(succi.x - current_level.door_world_x) < 150:
                    draw_text(screen, "Press 'E' to Enter", font_small, Color("turquoise1"), succi_blit_x + 20,
                              succi_blit_y - 80)

                for proj in projectile_group:
                    if -200 < (px := proj.rect.x - camera_x) < SCREEN_WIDTH + 200:
                        screen.blit(proj.image, (px, proj.rect.y))

                enemy_groups_to_check = [current_level.enemy_group]
                if current_state == "LEVEL_1":
                    enemy_groups_to_check.extend([current_level.demon_group, current_level.skeleton_group])
                elif current_state == "LEVEL_2":
                    enemy_groups_to_check.extend(
                        [current_level.helldog_group, current_level.mau_group, current_level.pkgrim_group])
                elif current_state == "LEVEL_3":
                    enemy_groups_to_check.extend(
                        [current_level.azule_group, current_level.titus_group, current_level.lionel_group,
                         current_level.demented_group])
                elif current_state == "LEVEL_4":
                    enemy_groups_to_check.extend(
                        [current_level.elaine_group, current_level.groundskeeper_group, current_level.royalhh_group,
                         current_level.royalzombie_group, current_level.zombie1_group, current_level.zombie2_group])

                for group in enemy_groups_to_check:
                    for target in group:
                        tx = target.rect.x - camera_x
                        if -200 < tx < SCREEN_WIDTH + 200:
                            ty = target.rect.top if hasattr(target, 'state') else target.rect.y
                            if target.mask.overlap(succi.mask, (succi_blit_x - tx, succi_blit_y - ty)):

                                is_ground_kicking = succi.current_anim == "kick" and 2 <= succi.current_frame <= 6
                                is_air_kicking = succi.current_anim == "jump_kick" and 3 <= succi.current_frame <= 5
                                is_kicking = is_ground_kicking or is_air_kicking

                                is_in_front = (succi.facing_right and target.rect.centerx > succi.x - 20) or \
                                              (not succi.facing_right and target.rect.centerx < succi.x + 20)

                                if is_kicking and is_in_front:
                                    if target not in succi.enemies_hit:
                                        succi.enemies_hit.append(target)

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

                                else:
                                    if succi.take_damage():
                                        game_over = True
                                        try:
                                            death_fx.play()
                                        except NameError:
                                            pass

                if abs(succi.x - current_level.door_world_x) < 150:
                    if keys[pygame.K_e]:
                        last_completed_level = current_state
                        is_level_2_merchant = (current_state in ["LEVEL_2", "LEVEL_3", "LEVEL_4"])
                        current_state = "MERCHANT"
                        pygame.mixer.music.stop()

                        if is_level_2_merchant:
                            merchant_npc = Merchant(SCREEN_WIDTH, SCREEN_HEIGHT,
                                                    "spritesheets/merchants sheets/merchant_lvl2_sheet.png", columns=10,
                                                    rows=7, target_duration=12200)
                        else:
                            merchant_npc = Merchant(SCREEN_WIDTH, SCREEN_HEIGHT,
                                                    "spritesheets/merchants sheets/merchant_lvl1_sheet.png", columns=10,
                                                    rows=6)

                        merchant_ui = Merchant_UI(SCREEN_WIDTH, SCREEN_HEIGHT, global_merchant_sold_out)
                        succi.x = 400.0

            elif current_state == "MERCHANT":
                if merchant_npc and merchant_npc.state == "intro":
                    merchant_npc.draw(screen)
                elif merchant_npc and merchant_npc.state == "idle" and merchant_ui:
                    merchant_ui.draw(screen, mouse_pos, rem)

            hud.draw(screen, SCREEN_WIDTH, succi.health, succi.max_health, rem, succi.spell_left_click,
                     succi.spell_right_click)

            if paused:
                owned_spells = ["normal"]
                if player_has_purple_magic:
                    owned_spells.append("purple")
                if player_has_blue_magic:
                    owned_spells.append("blue")
                if player_has_rainbow_dance:
                    owned_spells.append("rainbow")

                action = pause_menu.update(mouse_pos, mouse_click, owned_spells, player_has_tinera)

                if action:
                    if action["action"] == "EQUIP":
                        if action["slot"] == "left":
                            succi.spell_left_click = action["spell"]
                        elif action["slot"] == "right":
                            succi.spell_right_click = action["spell"]
                    elif action["action"] == "TOGGLE_TINERA":
                        tinera_active = not tinera_active

                pause_menu.draw(screen, owned_spells, mouse_pos, player_has_tinera, tinera_active, tinera_icon)

        else:
            death_screen.draw(screen, current_state, checkpoint)

            restart_action = None
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                restart_action = checkpoint
            elif checkpoint in [2, 3, 4] and pygame.key.get_pressed()[pygame.K_1]:
                restart_action = 1

            if restart_action is not None:
                game_over, paused, camera_x, rem = False, False, 0.0, 0
                old_max_health = succi.max_health if hasattr(succi, 'max_health') else 1

                old_left_spell = getattr(succi, 'spell_left_click', 'normal')
                old_right_spell = getattr(succi, 'spell_right_click', None)
                old_has_tinera = player_has_tinera
                old_tinera_active = tinera_active

                if restart_action == 4:
                    current_state, current_level = "LEVEL_4", Level_04(SCREEN_WIDTH, SCREEN_HEIGHT)
                elif restart_action == 3:
                    current_state, current_level = "LEVEL_3", Level_03(SCREEN_WIDTH, SCREEN_HEIGHT)
                elif restart_action == 2:
                    current_state, current_level = "LEVEL_2", Level_02(SCREEN_WIDTH, SCREEN_HEIGHT)
                else:
                    if current_state != "LEVEL_1":
                        pygame.mixer.music.load("mats/audio/Phaneroza-_No-Umbra-No-Penumbra.mp3")
                        pygame.mixer.music.set_volume(0.2)
                        pygame.mixer.music.play(-1, 0.0)
                    current_state, current_level, old_max_health = "LEVEL_1", Level_01(SCREEN_WIDTH, SCREEN_HEIGHT), 1

                    old_left_spell = "normal"
                    old_right_spell = None
                    old_has_tinera = False
                    old_tinera_active = False

                current_level.reset()
                merchant_npc, merchant_ui = None, None
                succi = Player(400.0, current_level.y_ground, animations, animation_speeds, animation_scale_corrections,
                               jump_fx, cast_fx)
                succi.max_health = old_max_health
                succi.health = old_max_health

                succi.spell_left_click = old_left_spell
                succi.spell_right_click = old_right_spell
                player_has_tinera = old_has_tinera
                tinera_active = old_tinera_active

                projectile_group.empty()

                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1, 0.0)

    pygame.display.update()

mixer.quit()
pygame.quit()
sys.exit()