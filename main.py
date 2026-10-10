# -main-#

import pygame
import sys
import os
import json
import subprocess

# ==========================================
# FIX FLASHING CMD WINDOW FOR PYVIDPLAYER2
# ==========================================
if os.name == 'nt':
    _original_popen = subprocess.Popen


    def _patched_popen(*args, **kwargs):
        if 'creationflags' not in kwargs:
            kwargs['creationflags'] = 0x08000000  # Forces CREATE_NO_WINDOW
        return _original_popen(*args, **kwargs)


    subprocess.Popen = _patched_popen
# ==========================================

from pygame import mixer, Color
import config

# OOP Imports
from player import Player
from enemies import GreyGargoyleFlyer
from entities import Projectile, Merchant, Companion, CheckpointShrine
from level import Level_01, Level_02, Level_03, Level_04, Level_05, Level_06, Level_07, Level_08, Merchant_Room

# Isolated UI components
from ui import MainMenu, Merchant_UI, PauseMenu, DeathScreen, HUD, draw_text, LevelBanner, CutsceneScreen, \
    GrimoireScreen

# SAVE FILE CREATION #

if getattr(sys, 'frozen', False):
    SAVE_DIR = os.path.join(os.path.dirname(sys.executable), "saves")
else:
    SAVE_DIR = os.path.abspath("saves")

os.makedirs(SAVE_DIR, exist_ok=True)


def save_game(slot, save_name):
    # Check if mid-level checkpoint shrine is currently active
    shrine_active = (current_level.checkpoint_shrine.activated
                     if hasattr(current_level, 'checkpoint_shrine') and current_level.checkpoint_shrine
                     else False)

    data = {
        "save_name": save_name,
        "level": current_state,
        "checkpoint": checkpoint,
        "checkpoint_shrine_activated": shrine_active,
        "rem": rem,
        "health": succi.health,
        "max_health": succi.max_health,

        "player_has_melee": player_has_melee,
        "player_has_purple_magic": player_has_purple_magic,
        "player_has_blue_magic": player_has_blue_magic,
        "player_has_rainbow_dance": player_has_rainbow_dance,
        "player_has_double_jump": player_has_double_jump,
        "player_has_dash": player_has_dash,
        "player_has_wings": player_has_wings,

        # Upgraded Pet Saving
        "owned_pets": owned_pets,
        "active_pet": active_pet,

        # Master Lifetime Stats Persistence
        "life_stats": life_stats,

        "spell_left": succi.spell_left_click,
        "spell_right": succi.spell_right_click,
        "merchant_inventory": global_merchant_sold_out
    }

    with open(f"{SAVE_DIR}/save{slot}.json", "w") as f:
        json.dump(data, f, indent=4)
    print(f"Game saved successfully to slot {slot}!")


def load_game(slot):
    global current_state, checkpoint, rem
    global player_has_melee, player_has_purple_magic, player_has_blue_magic
    global player_has_rainbow_dance, player_has_double_jump, player_has_dash, player_has_wings
    global owned_pets, active_pet, life_stats
    global succi, current_level
    global global_merchant_sold_out

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
    player_has_double_jump = data.get("player_has_double_jump", False)
    player_has_dash = data.get("player_has_dash", False)
    player_has_wings = data.get("player_has_wings", False)

    if "owned_pets" in data:
        owned_pets = data["owned_pets"]
        active_pet = data["active_pet"]
    else:
        owned_pets = ["tinera"] if data.get("player_has_tinera", False) else []
        active_pet = "tinera" if data.get("tinera_active", False) else None

    # Load Lifetime Stats
    if "life_stats" in data:
        life_stats = data["life_stats"]

    global_merchant_sold_out = data["merchant_inventory"]

    if current_state == "LEVEL_8":
        current_level = Level_08(SCREEN_WIDTH, SCREEN_HEIGHT)
    elif current_state == "LEVEL_7":
        current_level = Level_07(SCREEN_WIDTH, SCREEN_HEIGHT)
    elif current_state == "LEVEL_6":
        current_level = Level_06(SCREEN_WIDTH, SCREEN_HEIGHT)
    elif current_state == "LEVEL_5":
        current_level = Level_05(SCREEN_WIDTH, SCREEN_HEIGHT)
    elif current_state == "LEVEL_4":
        current_level = Level_04(SCREEN_WIDTH, SCREEN_HEIGHT)
    elif current_state == "LEVEL_3":
        current_level = Level_03(SCREEN_WIDTH, SCREEN_HEIGHT)
    elif current_state == "LEVEL_2":
        current_level = Level_02(SCREEN_WIDTH, SCREEN_HEIGHT)
    else:
        current_level = Level_01(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Spawn player at checkpoint if it was active when saved
    spawn_x = 400.0
    spawn_y = 400.0 if current_state == "LEVEL_8" else current_level.y_ground
    if data.get("checkpoint_shrine_activated", False) and hasattr(current_level,
                                                                  'checkpoint_shrine') and current_level.checkpoint_shrine:
        current_level.checkpoint_shrine.activated = True
        current_level.checkpoint_shrine.frame_index = 22
        spawn_x = float(current_level.checkpoint_x)
        if current_state == "LEVEL_8":
            spawn_y = 450.0

    succi = Player(spawn_x, spawn_y, animations, config.ANIMATION_SPEEDS,
                   config.ANIMATION_SCALE_CORRECTIONS, jump_fx, cast_fx)

    succi.health = data["health"]
    succi.max_health = data["max_health"]
    succi.spell_left_click = data["spell_left"]
    succi.spell_right_click = data["spell_right"]
    succi.has_double_jump = player_has_double_jump
    succi.has_dash = player_has_dash
    succi.is_flying_level = (current_state == "LEVEL_8")

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
    game_icon = pygame.image.load("mats/ui/succi frame.png").convert_alpha()
    pygame.display.set_icon(game_icon)
except pygame.error:
    pass

clock = pygame.time.Clock()
FPS = 60

try:
    jump_fx = pygame.mixer.Sound("mats/audio/Swoosh.mp3")
    jump_fx.set_volume(0.3)
    death_fx = pygame.mixer.Sound("mats/audio/Pause.mp3")
    death_fx.set_volume(0.6)
    cast_fx = pygame.mixer.Sound("mats/audio/cast.mp3")
    cast_fx.set_volume(0.28)
    explode_fx = pygame.mixer.Sound("mats/audio/explode.mp3")
    explode_fx.set_volume(0.18)
    merchant_voice_fx = pygame.mixer.Sound("mats/audio/merchant entrance.mp3")
    merchant_voice_fx.set_volume(0.6)
    laugh_fx = pygame.mixer.Sound("mats/audio/laugh_bb.mp3")
    laugh_fx.set_volume(0.6)
    departure_fx = pygame.mixer.Sound("mats/audio/merchant_departure.mp3")
    departure_fx.set_volume(0.6)
    merchant_greet_lvl_2_fx = pygame.mixer.Sound("mats/audio/merchant greet lvl 2.mp3")
    merchant_greet_lvl_2_fx.set_volume(0.6)
    merchant_greet_lvl_3_fx = pygame.mixer.Sound("mats/audio/merchant_greet_lvl3.mp3")
    merchant_greet_lvl_3_fx.set_volume(0.6)
    merchant_greet_lvl_4_fx = pygame.mixer.Sound("mats/audio/merchant_greet_lvl4.mp3")
    merchant_greet_lvl_4_fx.set_volume(0.6)
    merchant_greet_lvl_5_fx = pygame.mixer.Sound("mats/audio/merchant_greet_lvl5.mp3")
    merchant_greet_lvl_5_fx.set_volume(0.6)
    merchant_greet_lvl_6_fx = pygame.mixer.Sound("mats/audio/merchant_greet_lvl6.mp3")
    merchant_greet_lvl_6_fx.set_volume(0.6)
    merchant_greet_lvl_7_fx = pygame.mixer.Sound("mats/audio/merchant_greet_lvl7.mp3")
    merchant_greet_lvl_7_fx.set_volume(0.6)

    # --- LEVEL 8 MERCHANT AUDIO ---
    merchant_greet_lvl_8_fx = pygame.mixer.Sound("mats/audio/merchant_greet_lvl8.mp3")
    merchant_greet_lvl_8_fx.set_volume(0.6)

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
    "jump_kick": get_sprites_from_sheet("spritesheets/succi's sheets/S_FLYINGKICK_NB.png"),

    "idle_fly": get_sprites_from_sheet("spritesheets/succi's sheets/S_IDLE_FLY_NB.png"),
    "idle_fly_shot": get_sprites_from_sheet("spritesheets/succi's sheets/S_IDLE_FLY_SHOT_NB.png"),
    "flying": get_sprites_from_sheet("spritesheets/succi's sheets/S_FLYING_NB.png"),
    "fly_shot_reg": get_sprites_from_sheet("spritesheets/succi's sheets/S_FLY_SHOT_REG_NB.png")
}

fireball_img = pygame.image.load("spritesheets/spell sheets/fireball.png").convert_alpha()
explode_img = pygame.image.load("spritesheets/spell sheets/explode_NB.png").convert_alpha()
purple_fireball_img = pygame.image.load("spritesheets/spell sheets/purple_spell.png").convert_alpha()
purple_explode_img = pygame.image.load("spritesheets/spell sheets/purple_ball_explode.png").convert_alpha()

blueball_img = pygame.image.load("spritesheets/spell sheets/blueball_ss.png").convert_alpha()
blue_explode_img = pygame.image.load("spritesheets/spell sheets/blueball_explode_ss.png").convert_alpha()
rainball_img = pygame.image.load("spritesheets/spell sheets/rainball_ss.png").convert_alpha()
rainbow_explode_img = pygame.image.load("spritesheets/spell sheets/rainball_explode_ss.png").convert_alpha()

pet_frames = {}
pet_icons = {}
pet_names = ["tinera", "crowley", "gloom", "losslyn", "opal", "saphy", "trinity", "whisper"]

for p in pet_names:
    try:
        raw_icon = pygame.image.load(f"mats/ui/icon_{p}.png").convert_alpha()
        pet_icons[p] = pygame.transform.smoothscale(raw_icon, (68, 68))
    except pygame.error as e:
        print(f"Error loading icon for {p}: {e}")
        pet_icons[p] = None

    try:
        file_prefix = p.capitalize()
        raw_frames = get_sprites_from_sheet(f"spritesheets/pet sheets/{file_prefix}_ss.png")
        scale_val = 0.20 if p == "tinera" else 0.25
        pet_frames[p] = [
            pygame.transform.smoothscale(f, (int(810 * scale_val), int(1080 * scale_val)))
            for f in raw_frames
        ]
    except pygame.error as e:
        print(f"Error loading pet {p}: {e}")
        pet_frames[p] = []

# ==========================================
# MASTER LIFETIME STATS DOSSIER
# ==========================================
life_stats = {
    "deaths": 0,
    "enemies_killed": 0,
    "gargoyles_killed": 0,
    "damage_dealt": 0,
    "damage_taken": 0,
    "spells_cast": 0,
    "spell_counts": {"normal": 0, "purple": 0, "blue": 0, "rainbow": 0},
    "potions_bought": ["Health Potion"],
    "rem_harvested": 0,
    "rem_spent": 0,
    "total_time_ms": 0
}

# ==========================================
# GAME STATE & UI SETUP
# ==========================================
current_state = "INTRO"
last_completed_level = "LEVEL_1"
checkpoint = 1
game_over, paused = False, False
camera_x = 0.0
rem = 0
is_level_2_merchant = False
is_level_3_merchant = False
is_level_4_merchant = False
is_level_5_merchant = False
is_level_6_merchant = False
is_level_7_merchant = False
is_level_8_merchant = False

current_banner = None

# Grimoire State Flag
grimoire_open = False

global_merchant_sold_out = {
    "Health Potion": False, "Teal Potion": False, "Emerald Potion": False, "Pink Potion": False,
    "Mysterious Potion": False, "Silver Potion": False, "Dash Potion": False, "Wings Potion": False,
    "Purple Potion": False, "Blue Potion": False, "Rainbow Potion": False, "Royal Potion": False,
    "Gold Potion": False
}

player_has_purple_magic = False
player_has_rainbow_dance = False
player_has_melee = False
player_has_blue_magic = False
player_has_double_jump = False
player_has_dash = False
player_has_wings = False

owned_pets = []
active_pet = None
active_companion = None

hud = HUD()
main_menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
pause_menu = PauseMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
death_screen = DeathScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
grimoire_screen = GrimoireScreen(SCREEN_WIDTH, SCREEN_HEIGHT)

intro_screen = CutsceneScreen(SCREEN_WIDTH, SCREEN_HEIGHT, "mats/cut_scenes/intro_cut.mp4")
loading_screen = None
cutscene_screen = None

current_level = Level_01(SCREEN_WIDTH, SCREEN_HEIGHT)
merchant_room = Merchant_Room(SCREEN_WIDTH, SCREEN_HEIGHT)
merchant_npc = None
merchant_ui = None
exiting_merchant = False
exit_timer = 0

succi = Player(400.0, current_level.y_ground, animations, config.ANIMATION_SPEEDS, config.ANIMATION_SCALE_CORRECTIONS,
               jump_fx, cast_fx)
projectile_group = pygame.sprite.Group()

# ==========================================
# MAIN GAME LOOP
# ==========================================
if intro_screen:
    intro_screen.start()
run = True
while run:
    dt_ms = clock.tick(FPS)
    dt = dt_ms / 1000.0
    keys = pygame.key.get_pressed()

    # Accumulate continuous playtime
    life_stats["total_time_ms"] += dt_ms

    mouse_click = False
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            # Grimoire Toggle on 'G'
            if event.key == pygame.K_g:
                if not game_over and current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4", "LEVEL_5", "LEVEL_6",
                                                       "LEVEL_7", "LEVEL_8"]:
                    grimoire_open = not grimoire_open
                    paused = False

            elif event.key == pygame.K_ESCAPE and grimoire_open:
                grimoire_open = False

            elif not grimoire_open:
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
                        if current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4", "LEVEL_5", "LEVEL_6",
                                             "LEVEL_7", "LEVEL_8"]:
                            if not game_over:
                                paused = not paused
                                if not paused:
                                    pause_menu.save_state = None

                    elif event.key == pygame.K_m and current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4",
                                                                       "LEVEL_5", "LEVEL_6", "LEVEL_7", "LEVEL_8"]:
                        succi.x = current_level.door_world_x
                        camera_x = current_level.level_end_x - SCREEN_WIDTH
                    elif event.key == pygame.K_n and current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4",
                                                                       "LEVEL_5", "LEVEL_6", "LEVEL_7", "LEVEL_8",
                                                                       "LEVEL_6_CUTSCENE",
                                                                       "INTRO", "LOADING"]:

                        if current_state == "LEVEL_6_CUTSCENE" and cutscene_screen:
                            cutscene_screen.stop()
                        elif current_state == "INTRO" and intro_screen:
                            intro_screen.stop()
                        elif current_state == "LOADING" and loading_screen:
                            loading_screen.stop()

                        current_state = "LEVEL_8"
                        checkpoint = 8
                        current_level = Level_08(SCREEN_WIDTH, SCREEN_HEIGHT)
                        current_banner = LevelBanner(8, SCREEN_WIDTH)

                        player_has_wings = True
                        succi = Player(400.0, 400.0, animations, config.ANIMATION_SPEEDS,
                                       config.ANIMATION_SCALE_CORRECTIONS,
                                       jump_fx, cast_fx)
                        succi.max_health = 1
                        succi.health = 1
                        succi.has_double_jump = player_has_double_jump
                        succi.has_dash = player_has_dash
                        succi.is_flying_level = True
                        camera_x = 0.0
                        projectile_group.empty()
                        pygame.mixer.music.load(
                            "mats/audio/Beethoven Piano Sonata No. 14 in C-sharp minor, Op. 27, No. 2.mp3")
                        pygame.mixer.music.set_volume(0.23)
                        pygame.mixer.music.play(-1, 0.0)

                    elif event.key == pygame.K_3 and current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4",
                                                                       "LEVEL_5", "LEVEL_6", "LEVEL_7"]:
                        if player_has_melee and not paused and not game_over:
                            succi.trigger_kick()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_click = True

            if not grimoire_open and not game_over and not paused and current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3",
                                                                                        "LEVEL_4",
                                                                                        "LEVEL_5", "LEVEL_6", "LEVEL_7",
                                                                                        "LEVEL_8"]:
                live_k = pygame.key.get_pressed()
                is_moving = live_k[pygame.K_LEFT] or live_k[pygame.K_RIGHT] or live_k[pygame.K_a] or live_k[
                    pygame.K_d] or (
                                    succi.is_flying_level and (
                                    live_k[pygame.K_w] or live_k[pygame.K_s] or live_k[pygame.K_UP] or live_k[
                                pygame.K_DOWN])
                            )
                is_running = live_k[pygame.K_LSHIFT] or live_k[pygame.K_RSHIFT]

                if event.button == 1:
                    succi.trigger_attack(is_running, is_moving)
                    succi.current_spell_type = succi.spell_left_click
                elif event.button == 3:
                    if succi.spell_right_click is not None:
                        succi.trigger_attack(is_running, is_moving)
                        succi.current_spell_type = succi.spell_right_click

            elif event.button == 2:
                if player_has_melee and not succi.is_flying_level and not game_over and not paused and not grimoire_open:
                    succi.trigger_kick()

    # ==========================================================================
    # --- GRIMOIRE INTERACTION DISPATCHER ---
    # ==========================================================================
    if grimoire_open:
        grimoire_screen.update(mouse_pos, mouse_click)

    elif current_state == "INTRO":
        if intro_screen and intro_screen.update(mouse_pos, mouse_click, allow_skip=True):
            current_state = "LOADING"
            intro_screen = None
            if loading_screen is None:
                loading_screen = CutsceneScreen(SCREEN_WIDTH, SCREEN_HEIGHT, "mats/cut_scenes/Loading_screen_cut.mp4")
            loading_screen.start()
            pygame.mixer.music.load("mats/audio/Prelude and Fughetta in D minor, BWV 899 (Pedal-Harpsichord).mp3")
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1, 0.0)

    elif current_state == "LOADING":
        if loading_screen and loading_screen.update(mouse_pos, mouse_click, allow_skip=False):
            loading_screen = None
            current_state = "MAIN_MENU"

    elif current_state == "MAIN_MENU":
        action = main_menu.update(mouse_pos, mouse_click)
        if action == "PLAY":
            current_state = "LEVEL_1"
            current_banner = LevelBanner(1, SCREEN_WIDTH)

            try:
                current_level.reset(reset_checkpoint=True)
            except TypeError:
                current_level.reset()
                if hasattr(current_level, 'checkpoint_shrine') and current_level.checkpoint_shrine:
                    current_level.checkpoint_shrine.activated = False
                    current_level.checkpoint_shrine.frame_index = 0
            succi = Player(400.0, current_level.y_ground, animations, config.ANIMATION_SPEEDS,
                           config.ANIMATION_SCALE_CORRECTIONS,
                           jump_fx, cast_fx)
            rem = 0
            checkpoint = 1
            camera_x = 0.0
            game_over = False
            paused = False

            pygame.mixer.music.load("mats/audio/Phaneroza-_No-Umbra-No-Penumbra.mp3")
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1, 0.0)

        elif type(action) is dict:
            if action.get("action") == "LOAD":
                loaded_name = load_game(action["slot"])
                if loaded_name:
                    lvl_num = int(current_state.split("_")[1])
                    current_banner = LevelBanner(lvl_num, SCREEN_WIDTH)

                    camera_x = max(0.0, min(succi.x - SCREEN_WIDTH * 0.5, current_level.level_end_x - SCREEN_WIDTH))
                    game_over = False
                    paused = False
                    projectile_group.empty()

                    if current_state == "LEVEL_8":
                        pygame.mixer.music.load(
                            "mats/audio/Beethoven Piano Sonata No. 14 in C-sharp minor, Op. 27, No. 2.mp3")
                        pygame.mixer.music.set_volume(0.23)
                    elif current_state == "LEVEL_7":
                        pygame.mixer.music.load("mats/audio/Chopin_-nocturne-in-c-sharp-minor.mp3")
                        pygame.mixer.music.set_volume(0.23)
                    elif current_state == "LEVEL_6":
                        pygame.mixer.music.load("mats/audio/Isaac_Albéniz_Suite_Espanola_Op.47_Leyenda.mp3")
                        pygame.mixer.music.set_volume(0.23)
                    elif current_state == "LEVEL_5":
                        pygame.mixer.music.load("mats/audio/chopin-nocturne-op9-in-b-flat-minor.mp3")
                        pygame.mixer.music.set_volume(0.23)
                    elif current_state == "LEVEL_4":
                        pygame.mixer.music.load("mats/audio/Polonaise in F sharp minor, Op. 44.mp3")
                        pygame.mixer.music.set_volume(0.2)
                    elif current_state == "LEVEL_3":
                        pygame.mixer.music.load("mats/audio/Ballade no. 1 in G minor, Op. 23.mp3")
                        pygame.mixer.music.set_volume(0.23)
                    elif current_state == "LEVEL_2":
                        pygame.mixer.music.load("mats/audio/Toccata and Fugue in Dm, BWV 565.mp3")
                        pygame.mixer.music.set_volume(0.2)
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
                main_menu._load_save_data()

    elif not game_over and not paused and not grimoire_open:
        if current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4", "LEVEL_5", "LEVEL_6", "LEVEL_7", "LEVEL_8"]:
            succi.update(keys, dt, dt_ms, current_level.platform_group, config.ANIMATION_LOOPS)

            if succi.x > current_level.level_end_x - 100:
                succi.x = current_level.level_end_x - 100

            fire_condition = (succi.attacking and not succi.fireball_spawned)
            if succi.is_flying_level:
                fire_trigger = (succi.current_frame in [7, 8])
            else:
                fire_trigger = (succi.current_frame == (8 if succi.current_anim == "attack" else 4))

            if fire_condition and fire_trigger:
                spawn_x = succi.x + (90 if succi.facing_right else -90)

                if succi.is_flying_level:
                    if getattr(succi, 'cast_aim_dir_y', 0.0) < 0:
                        spawn_y = succi.y - 50
                    elif getattr(succi, 'cast_aim_dir_y', 0.0) > 0:
                        spawn_y = succi.y + 10
                    else:
                        spawn_y = succi.y - 25
                else:
                    spawn_y = succi.y - 180

                spell_type = getattr(succi, 'current_spell_type', 'normal')

                # Track Lifetime Spells
                life_stats["spells_cast"] += 1
                if spell_type in life_stats["spell_counts"]:
                    life_stats["spell_counts"][spell_type] += 1

                if spell_type == "purple":
                    active_fireball, active_explode, f_scale, e_scale, e_offset, proj_dmg = purple_fireball_img, purple_explode_img, 0.28, 0.28, 0, 1
                elif spell_type == "blue":
                    active_fireball, active_explode, f_scale, e_scale, e_offset, proj_dmg = blueball_img, blue_explode_img, 0.7, 0.2, 65, 1
                elif spell_type == "rainbow":
                    active_fireball, active_explode, f_scale, e_scale, e_offset, proj_dmg = rainball_img, rainbow_explode_img, 0.7, 0.2, 0, 2
                else:
                    active_fireball, active_explode, f_scale, e_scale, e_offset, proj_dmg = fireball_img, explode_img, 0.28, 0.28, 0, 1

                projectile_group.add(
                    Projectile(spawn_x, spawn_y, 1 if succi.facing_right else -1, active_fireball, active_explode,
                               f_scale, e_scale, e_offset, proj_dmg, dir_y=getattr(succi, 'cast_aim_dir_y', 0.0))
                )
                succi.fireball_spawned = True
                try:
                    cast_fx.play()
                except NameError:
                    pass

            screen_x = succi.x - camera_x
            if screen_x > SCREEN_WIDTH * 0.65:
                camera_x += (screen_x - SCREEN_WIDTH * 0.65)
            elif screen_x < SCREEN_WIDTH * 0.35:
                camera_x -= (SCREEN_WIDTH * 0.35 - screen_x)

            if camera_x > current_level.level_end_x - SCREEN_WIDTH:
                camera_x = current_level.level_end_x - SCREEN_WIDTH
            if camera_x < 0:
                camera_x = 0

            current_level.update(dt, camera_x, succi.x, succi.y, current_banner is not None)
            projectile_group.update(dt, camera_x, SCREEN_WIDTH)

            for proj in projectile_group:
                if proj.state == "fly":
                    enemy_targets = [current_level.enemy_group]
                    if current_state == "LEVEL_1":
                        enemy_targets.extend(
                            [current_level.cecil_group, current_level.margret_group, current_level.lashly_group,
                             current_level.hellguard_group])
                    elif current_state == "LEVEL_2":
                        enemy_targets.extend(
                            [current_level.helldog_group, current_level.mau_group, current_level.pkgrim_group,
                             current_level.castleguard_group])
                    elif current_state == "LEVEL_3":
                        enemy_targets.extend(
                            [current_level.azule_group, current_level.titus_group, current_level.lionel_group,
                             current_level.demented_group])
                    elif current_state == "LEVEL_4":
                        enemy_targets.extend(
                            [current_level.elaine_group, current_level.groundskeeper_group, current_level.royalhh_group,
                             current_level.royalzombie_group, current_level.zombie1_group, current_level.zombie2_group])
                    elif current_state == "LEVEL_5":
                        enemy_targets.extend(
                            [current_level.priestly_group, current_level.realmwalker_group, current_level.pursuer_group,
                             current_level.braid_group, current_level.deadlight_group])
                    elif current_state == "LEVEL_6":
                        enemy_targets.extend(
                            [current_level.victoria_group, current_level.kali_group, current_level.kimoura_group,
                             current_level.cassie_group, current_level.silas_group, current_level.thad_group])
                    elif current_state == "LEVEL_7":
                        enemy_targets.extend(
                            [current_level.molly_group, current_level.skelter_group, current_level.tilde_group,
                             current_level.topaz_group, current_level.volgrim_group, current_level.voss_group])

                    for group in enemy_targets:
                        for target in group:
                            ty = target.rect.top if hasattr(target, 'state') else target.rect.y
                            if proj.mask.overlap(target.mask, (target.rect.x - proj.rect.x, ty - proj.rect.y)):
                                proj.explode()
                                life_stats["damage_dealt"] += proj.damage
                                if hasattr(target, 'take_damage'):
                                    if target.take_damage(proj.damage):
                                        rem += target.rem_value
                                        life_stats["rem_harvested"] += target.rem_value
                                        if isinstance(target, GreyGargoyleFlyer):
                                            life_stats["gargoyles_killed"] += 1
                                        else:
                                            life_stats["enemies_killed"] += 1
                                        target.kill()
                                else:
                                    rem += target.rem_value
                                    life_stats["rem_harvested"] += target.rem_value
                                    if isinstance(target, GreyGargoyleFlyer):
                                        life_stats["gargoyles_killed"] += 1
                                    else:
                                        life_stats["enemies_killed"] += 1
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
                # ==============================================================
                # --- LEVEL 8 GREETING AUDIO INTEGRATION ---
                # ==============================================================
                if is_level_8_merchant:
                    active_merchant_audio = merchant_greet_lvl_8_fx
                elif is_level_7_merchant:
                    active_merchant_audio = merchant_greet_lvl_7_fx
                elif is_level_6_merchant:
                    active_merchant_audio = merchant_greet_lvl_6_fx
                elif is_level_5_merchant:
                    active_merchant_audio = merchant_greet_lvl_5_fx
                elif is_level_4_merchant:
                    active_merchant_audio = merchant_greet_lvl_4_fx
                elif is_level_3_merchant:
                    active_merchant_audio = merchant_greet_lvl_3_fx
                elif is_level_2_merchant:
                    active_merchant_audio = merchant_greet_lvl_2_fx
                else:
                    active_merchant_audio = merchant_voice_fx

                merchant_npc.update(dt_ms, active_merchant_audio)
                if merchant_npc.state == "idle" and merchant_ui is not None:
                    if not exiting_merchant:
                        bought_item = merchant_ui.update(mouse_pos, mouse_click, rem)

                        if bought_item == "EXIT_CLICKED":
                            exiting_merchant = True
                            exit_timer = pygame.time.get_ticks()
                            try:
                                departure_fx.play()
                            except NameError:
                                pass
                        elif bought_item:
                            try:
                                laugh_fx.play()
                            except NameError:
                                pass

                            if bought_item not in ["Teal Potion", "Pink Potion"]:
                                merchant_ui.sold_out[bought_item] = True

                            merchant_ui.selected_item = None

                            if bought_item not in life_stats["potions_bought"]:
                                life_stats["potions_bought"].append(bought_item)

                            if bought_item == "Health Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                succi.max_health = 3
                                succi.health = 3
                            elif bought_item == "Teal Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                succi.health = min(succi.health + 3, succi.max_health)
                            elif bought_item == "Emerald Potion":
                                rem -= 150
                                life_stats["rem_spent"] += 150
                                succi.max_health += 2
                                succi.health = succi.max_health
                            elif bought_item == "Pink Potion":
                                rem -= 100
                                life_stats["rem_spent"] += 100
                                succi.health = min(succi.health + 5, succi.max_health)
                            elif bought_item == "Gold Potion":
                                rem -= 250
                                life_stats["rem_spent"] += 250
                                succi.max_health += 1
                                succi.health = succi.max_health
                            elif bought_item == "Silver Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                player_has_melee = True
                            elif bought_item == "Blue Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                player_has_blue_magic = True
                                if succi.spell_right_click is None:
                                    succi.spell_right_click = "blue"

                            elif bought_item == "Wings Potion":
                                rem -= 200
                                life_stats["rem_spent"] += 200
                                player_has_wings = True

                            elif bought_item == "Purple Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                player_has_purple_magic = True
                                if succi.spell_right_click is None:
                                    succi.spell_right_click = "purple"
                            elif bought_item == "Rainbow Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                player_has_rainbow_dance = True
                                if succi.spell_right_click is None:
                                    succi.spell_right_click = "rainbow"

                            elif bought_item == "Mysterious Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                player_has_double_jump = True
                                succi.has_double_jump = True

                            elif bought_item == "Dash Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                player_has_dash = True
                                succi.has_dash = True
                                succi.dash_charges = getattr(config, 'PLAYER_DASH_MAX_CHARGES', 2)

                            elif bought_item == "Royal Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                if "tinera" not in owned_pets: owned_pets.append("tinera")
                                active_pet = "tinera"
                            elif bought_item == "Crowley Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                if "crowley" not in owned_pets: owned_pets.append("crowley")
                                active_pet = "crowley"
                            elif bought_item == "Gloom Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                if "gloom" not in owned_pets: owned_pets.append("gloom")
                                active_pet = "gloom"
                            elif bought_item == "Losslyn Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                if "losslyn" not in owned_pets: owned_pets.append("losslyn")
                                active_pet = "losslyn"
                            elif bought_item == "Opal Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                if "opal" not in owned_pets: owned_pets.append("opal")
                                active_pet = "opal"
                            elif bought_item == "Saphy Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                if "saphy" not in owned_pets: owned_pets.append("saphy")
                                active_pet = "saphy"
                            elif bought_item == "Trinity Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                if "trinity" not in owned_pets: owned_pets.append("trinity")
                                active_pet = "trinity"
                            elif bought_item == "Whisper Potion":
                                rem -= 50
                                life_stats["rem_spent"] += 50
                                if "whisper" not in owned_pets: owned_pets.append("whisper")
                                active_pet = "whisper"

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
                                current_state, current_level, checkpoint = "LEVEL_5", Level_05(SCREEN_WIDTH,
                                                                                               SCREEN_HEIGHT), 5
                            elif last_completed_level == "LEVEL_5":
                                current_state, current_level, checkpoint = "LEVEL_6", Level_06(SCREEN_WIDTH,
                                                                                               SCREEN_HEIGHT), 6
                            elif last_completed_level == "LEVEL_6":
                                current_state, current_level, checkpoint = "LEVEL_6_CUTSCENE"
                                checkpoint = 7
                                if cutscene_screen is None:
                                    cutscene_screen = CutsceneScreen(SCREEN_WIDTH, SCREEN_HEIGHT,
                                                                     "mats/cut_scenes/6a-cut.mp4")

                            elif last_completed_level == "LEVEL_7":
                                if player_has_wings:
                                    current_state, current_level, checkpoint = "LEVEL_8", Level_08(SCREEN_WIDTH,
                                                                                                   SCREEN_HEIGHT), 8
                                else:
                                    current_state, current_level, checkpoint = "LEVEL_7", Level_07(SCREEN_WIDTH,
                                                                                                   SCREEN_HEIGHT), 7

                            elif last_completed_level == "LEVEL_8":
                                current_state, current_level, checkpoint = "LEVEL_1", Level_01(SCREEN_WIDTH,
                                                                                               SCREEN_HEIGHT), 1

                            succi.x = 400.0
                            succi.y = 400.0 if current_state == "LEVEL_8" else current_level.y_ground
                            succi.has_double_jump = player_has_double_jump
                            succi.has_dash = player_has_dash
                            succi.is_flying_level = (current_state == "LEVEL_8")
                            camera_x = 0.0
                            exiting_merchant = False
                            merchant_npc = None
                            merchant_ui = None
                            is_level_2_merchant = False
                            is_level_3_merchant = False
                            is_level_4_merchant = False
                            is_level_5_merchant = False
                            is_level_6_merchant = False
                            is_level_7_merchant = False
                            is_level_8_merchant = False

                            if current_state == "LEVEL_6_CUTSCENE":
                                pygame.mixer.music.stop()
                                if cutscene_screen:
                                    cutscene_screen.start()
                            else:
                                lvl_num = int(current_state.split("_")[1])
                                current_banner = LevelBanner(lvl_num, SCREEN_WIDTH)

                                if current_state == "LEVEL_8":
                                    pygame.mixer.music.load(
                                        "mats/audio/Beethoven Piano Sonata No. 14 in C-sharp minor, Op. 27, No. 2.mp3")
                                    pygame.mixer.music.set_volume(0.23)
                                elif current_state == "LEVEL_7":
                                    pygame.mixer.music.load("mats/audio/Chopin_-nocturne-in-c-sharp-minor.mp3")
                                    pygame.mixer.music.set_volume(0.23)
                                elif current_state == "LEVEL_6":
                                    pygame.mixer.music.load("mats/audio/Isaac_Albéniz_Suite_Espanola_Op.47_Leyenda.mp3")
                                    pygame.mixer.music.set_volume(0.23)
                                elif current_state == "LEVEL_5":
                                    pygame.mixer.music.load("mats/audio/chopin-nocturne-op9-in-b-flat-minor.mp3")
                                    pygame.mixer.music.set_volume(0.23)
                                elif current_state == "LEVEL_4":
                                    pygame.mixer.music.load("mats/audio/Polonaise in F sharp minor, Op. 44.mp3")
                                    pygame.mixer.music.set_volume(0.2)
                                elif current_state == "LEVEL_3":
                                    pygame.mixer.music.load("mats/audio/Ballade no. 1 in G minor, Op. 23.mp3")
                                    pygame.mixer.music.set_volume(0.23)
                                elif current_state == "LEVEL_2":
                                    pygame.mixer.music.load("mats/audio/Toccata and Fugue in Dm, BWV 565.mp3")
                                    pygame.mixer.music.set_volume(0.2)
                                else:
                                    pygame.mixer.music.load("mats/audio/Phaneroza-_No-Umbra-No-Penumbra.mp3")
                                    pygame.mixer.music.set_volume(0.2)

                                pygame.mixer.music.play(-1, 0.0)

        elif current_state == "LEVEL_6_CUTSCENE":
            if cutscene_screen and cutscene_screen.update(mouse_pos, mouse_click):
                current_state = "LEVEL_7"
                cutscene_screen = None
                current_level = Level_07(SCREEN_WIDTH, SCREEN_HEIGHT)
                current_banner = LevelBanner(7, SCREEN_WIDTH)

                succi.has_double_jump = player_has_double_jump
                succi.has_dash = player_has_dash
                succi.is_flying_level = False

                pygame.mixer.music.load("mats/audio/Chopin_-nocturne-in-c-sharp-minor.mp3")
                pygame.mixer.music.set_volume(0.23)
                pygame.mixer.music.play(-1, 0.0)

        # ==========================================
        # DRAWING PHASE
        # ==========================================

    if current_state == "INTRO":
        if intro_screen:
            intro_screen.draw(screen, mouse_pos, show_skip=True)

    elif current_state == "LOADING":
        if loading_screen:
            loading_screen.draw(screen, mouse_pos, show_skip=False)

    elif current_state == "MAIN_MENU":
        main_menu.draw(screen, mouse_pos)

    else:
        if not game_over:
            if current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4", "LEVEL_5", "LEVEL_6", "LEVEL_7",
                                 "LEVEL_8"]:
                current_level.draw(screen, camera_x)
                succi_blit_x, succi_blit_y = succi.draw(screen, camera_x)

                if active_pet and active_pet in pet_frames and pet_frames[active_pet]:
                    if active_companion is None or getattr(active_companion, 'pet_id', None) != active_pet:
                        active_companion = Companion(pet_frames[active_pet])
                        active_companion.pet_id = active_pet

                    stable_screen_x = succi.x - camera_x
                    stable_screen_y = succi.y
                    active_companion.update(stable_screen_x, stable_screen_y, succi.facing_right, succi.is_flying_level)
                    active_companion.draw(screen)

                if abs(succi.x - current_level.door_world_x) < 150:
                    draw_text(screen, "Press 'E' to Enter", font_small, Color("turquoise1"), succi_blit_x + 20,
                              succi_blit_y - 80)
                    if keys[pygame.K_e]:
                        last_completed_level = current_state
                        is_level_2_merchant = (last_completed_level == "LEVEL_2")
                        is_level_3_merchant = (last_completed_level == "LEVEL_3")
                        is_level_4_merchant = (last_completed_level == "LEVEL_4")
                        is_level_5_merchant = (last_completed_level == "LEVEL_5")
                        is_level_6_merchant = (last_completed_level == "LEVEL_6")
                        is_level_7_merchant = (last_completed_level == "LEVEL_7")
                        is_level_8_merchant = (last_completed_level == "LEVEL_8")
                        current_state = "MERCHANT"
                        pygame.mixer.music.stop()

                        current_banner = None

                        # ==============================================================
                        # --- LEVEL 8 MERCHANT SPRITE SHEET (10 COLS x 8 ROWS) ---
                        # ==============================================================
                        if is_level_8_merchant:
                            merchant_npc = Merchant(SCREEN_WIDTH, SCREEN_HEIGHT,
                                                    "spritesheets/merchants sheets/merchant_lvl_8.png", columns=10,
                                                    rows=8, target_duration=9500)
                        elif is_level_7_merchant:
                            merchant_npc = Merchant(SCREEN_WIDTH, SCREEN_HEIGHT,
                                                    "spritesheets/merchants sheets/merchant_lvl_7.png", columns=10,
                                                    rows=8, target_duration=9500)
                        elif is_level_6_merchant:
                            merchant_npc = Merchant(SCREEN_WIDTH, SCREEN_HEIGHT,
                                                    "spritesheets/merchants sheets/merchant_lvl_6.png", columns=10,
                                                    rows=8, target_duration=9500)
                        elif is_level_5_merchant:
                            merchant_npc = Merchant(SCREEN_WIDTH, SCREEN_HEIGHT,
                                                    "spritesheets/merchants sheets/merchant_lvl_5.png", columns=10,
                                                    rows=8, target_duration=9500)
                        elif is_level_4_merchant:
                            merchant_npc = Merchant(SCREEN_WIDTH, SCREEN_HEIGHT,
                                                    "spritesheets/merchants sheets/merchant_lvl_4.png", columns=10,
                                                    rows=8, target_duration=9590)
                        elif is_level_3_merchant:
                            merchant_npc = Merchant(SCREEN_WIDTH, SCREEN_HEIGHT,
                                                    "spritesheets/merchants sheets/merchant_lvl_3.png", columns=10,
                                                    rows=8, target_duration=9590)
                        elif is_level_2_merchant:
                            merchant_npc = Merchant(SCREEN_WIDTH, SCREEN_HEIGHT,
                                                    "spritesheets/merchants sheets/merchant_lvl2_sheet.png", columns=10,
                                                    rows=7, target_duration=11650)
                        else:
                            merchant_npc = Merchant(SCREEN_WIDTH, SCREEN_HEIGHT,
                                                    "spritesheets/merchants sheets/merchant_lvl1_sheet.png", columns=10,
                                                    rows=6, target_duration=9590)

                        merchant_ui = Merchant_UI(SCREEN_WIDTH, SCREEN_HEIGHT, global_merchant_sold_out)
                        succi.x = 400.0
                        succi.is_flying_level = False

                for proj in projectile_group:
                    if -200 < (px := proj.rect.x - camera_x) < SCREEN_WIDTH + 200:
                        screen.blit(proj.image, (px, proj.rect.y))

                enemy_groups_to_check = [current_level.enemy_group]
                if current_state == "LEVEL_1":
                    enemy_groups_to_check.extend(
                        [current_level.cecil_group, current_level.margret_group, current_level.lashly_group,
                         current_level.hellguard_group])
                elif current_state == "LEVEL_2":
                    enemy_groups_to_check.extend(
                        [current_level.helldog_group, current_level.mau_group, current_level.pkgrim_group,
                         current_level.castleguard_group])
                elif current_state == "LEVEL_3":
                    enemy_groups_to_check.extend(
                        [current_level.azule_group, current_level.titus_group, current_level.lionel_group,
                         current_level.demented_group])
                elif current_state == "LEVEL_4":
                    enemy_groups_to_check.extend(
                        [current_level.elaine_group, current_level.groundskeeper_group, current_level.royalhh_group,
                         current_level.royalzombie_group, current_level.zombie1_group, current_level.zombie2_group])
                elif current_state == "LEVEL_5":
                    enemy_groups_to_check.extend(
                        [current_level.priestly_group, current_level.realmwalker_group, current_level.pursuer_group,
                         current_level.braid_group, current_level.deadlight_group])
                elif current_state == "LEVEL_6":
                    enemy_groups_to_check.extend(
                        [current_level.victoria_group, current_level.kali_group, current_level.kimoura_group,
                         current_level.cassie_group, current_level.silas_group, current_level.thad_group])
                elif current_state == "LEVEL_7":
                    enemy_groups_to_check.extend(
                        [current_level.molly_group, current_level.skelter_group, current_level.tilde_group,
                         current_level.topaz_group, current_level.volgrim_group, current_level.voss_group])

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
                                        life_stats["damage_dealt"] += 1

                                        if hasattr(target, 'take_damage'):
                                            if target.take_damage():
                                                rem += target.rem_value
                                                life_stats["rem_harvested"] += target.rem_value
                                                if isinstance(target, GreyGargoyleFlyer):
                                                    life_stats["gargoyles_killed"] += 1
                                                else:
                                                    life_stats["enemies_killed"] += 1
                                                target.kill()
                                        else:
                                            rem += target.rem_value
                                            life_stats["rem_harvested"] += target.rem_value
                                            if isinstance(target, GreyGargoyleFlyer):
                                                life_stats["gargoyles_killed"] += 1
                                            else:
                                                life_stats["enemies_killed"] += 1
                                            target.kill()

                                        try:
                                            explode_fx.play()
                                        except NameError:
                                            pass

                                else:
                                    # Damage taken tracking
                                    life_stats["damage_taken"] += 1
                                    if succi.take_damage():
                                        life_stats["deaths"] += 1
                                        game_over = True
                                        try:
                                            death_fx.play()
                                        except NameError:
                                            pass

            elif current_state == "MERCHANT":
                if merchant_npc and merchant_npc.state == "intro":
                    merchant_npc.draw(screen)
                elif merchant_npc and merchant_npc.state == "idle" and merchant_ui:
                    merchant_ui.draw(screen, mouse_pos, rem)

            elif current_state == "LEVEL_6_CUTSCENE":
                if cutscene_screen:
                    cutscene_screen.draw(screen, mouse_pos, show_skip=True)

            if current_state != "LEVEL_6_CUTSCENE":
                hud.draw(screen, SCREEN_WIDTH, succi.health, succi.max_health, rem, succi.spell_left_click,
                         succi.spell_right_click)

            if current_state in ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4", "LEVEL_5", "LEVEL_6", "LEVEL_7",
                                 "LEVEL_8"]:
                if current_banner:
                    is_banner_active = current_banner.update_and_draw(screen)
                    if not is_banner_active:
                        current_banner = None

            if paused:
                owned_spells = ["normal"]
                if player_has_purple_magic:
                    owned_spells.append("purple")
                if player_has_blue_magic:
                    owned_spells.append("blue")
                if player_has_rainbow_dance:
                    owned_spells.append("rainbow")

                action = pause_menu.update(mouse_pos, mouse_click, owned_spells, owned_pets, active_pet)

                if action:
                    if action["action"] == "EQUIP":
                        if action["slot"] == "left":
                            succi.spell_left_click = action["spell"]
                        elif action["slot"] == "right":
                            succi.spell_right_click = action["spell"]
                    elif action["action"] == "EQUIP_PET":
                        active_pet = action["pet"]
                    elif action["action"] == "UNEQUIP_PET":
                        active_pet = None
                    elif action["action"] == "TOGGLE_TINERA":
                        if active_pet == "tinera":
                            active_pet = None
                        elif "tinera" in owned_pets:
                            active_pet = "tinera"

                pause_menu.draw(screen, owned_spells, mouse_pos, owned_pets, active_pet, pet_icons,
                                life_stats=life_stats)

            # Draw Standalone Grimoire Overlay when 'G' is active
            if grimoire_open:
                grimoire_screen.draw(screen, mouse_pos)

        else:
            # Check if mid-level checkpoint shrine is currently activated
            checkpoint_active = (current_level.checkpoint_shrine.activated
                                 if hasattr(current_level, 'checkpoint_shrine') and current_level.checkpoint_shrine
                                 else False)

            death_screen.draw(screen, current_state, checkpoint_active)

            restart_action = None
            respawn_at_checkpoint = False

            if pygame.key.get_pressed()[pygame.K_SPACE]:
                restart_action = int(current_state.split("_")[1])
                respawn_at_checkpoint = checkpoint_active
            elif checkpoint_active and pygame.key.get_pressed()[pygame.K_1]:
                # Press '1' to restart level from the very beginning
                restart_action = int(current_state.split("_")[1])
                respawn_at_checkpoint = False

            if restart_action is not None:
                game_over, paused, camera_x, rem = False, False, 0.0, 0
                old_max_health = succi.max_health if hasattr(succi, 'max_health') else 1

                old_left_spell = getattr(succi, 'spell_left_click', 'normal')
                old_right_spell = getattr(succi, 'spell_right_click', None)

                old_owned_pets = list(owned_pets)
                old_active_pet = active_pet
                old_has_double_jump = player_has_double_jump
                old_has_dash = player_has_dash
                old_has_wings = player_has_wings

                # Reset level state
                try:
                    current_level.reset(reset_checkpoint=not respawn_at_checkpoint)
                except TypeError:
                    current_level.reset()
                    if not respawn_at_checkpoint and hasattr(current_level,
                                                             'checkpoint_shrine') and current_level.checkpoint_shrine:
                        current_level.checkpoint_shrine.activated = False
                        current_level.checkpoint_shrine.frame_index = 0
                merchant_npc, merchant_ui = None, None

                # Determine spawn position
                if respawn_at_checkpoint:
                    spawn_x = float(current_level.checkpoint_x)
                    spawn_y = 450.0 if current_state == "LEVEL_8" else current_level.y_ground
                    camera_x = max(0.0, min(spawn_x - SCREEN_WIDTH * 0.5, current_level.level_end_x - SCREEN_WIDTH))
                else:
                    spawn_x = 400.0
                    spawn_y = 400.0 if current_state == "LEVEL_8" else current_level.y_ground
                    camera_x = 0.0

                current_banner = LevelBanner(restart_action, SCREEN_WIDTH)

                succi = Player(spawn_x, spawn_y, animations,
                               config.ANIMATION_SPEEDS,
                               config.ANIMATION_SCALE_CORRECTIONS,
                               jump_fx, cast_fx)
                succi.max_health = old_max_health
                succi.health = old_max_health

                succi.spell_left_click = old_left_spell
                succi.spell_right_click = old_right_spell

                succi.has_double_jump = old_has_double_jump
                succi.has_dash = old_has_dash
                player_has_wings = old_has_wings
                succi.is_flying_level = (current_state == "LEVEL_8")

                owned_pets = old_owned_pets
                active_pet = old_active_pet
                active_companion = None

                projectile_group.empty()

                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1, 0.0)

    pygame.display.update()

mixer.quit()
pygame.quit()
sys.exit()