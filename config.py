# config.py
# Global settings & magic numbers for Succi Solace #

# --- PLAYER PHYSICS --- #
PLAYER_SPEED_WALK = 180.0
PLAYER_SPEED_RUN = 320.0
PLAYER_JUMP_IMPULSE = -800.0
PLAYER_GRAVITY = 1500.0

# --- PLAYER STATS --- #
PLAYER_STARTING_HEALTH = 1
PLAYER_INVULNERABLE_DURATION = 1000  # in milliseconds

# --- PLAYER RENDERING --- #
PLAYER_BASE_SCALE = 0.25
PLAYER_ATTACK_Y_OFFSET = 230
PLAYER_ATTACK_X_SHIFT = 200
DEFAULT_ANIM_DELAY = 120

# --- PLAYER ANIMATION STATES, SPEEDS AND SIZES --- #
ANIMATION_SPEEDS = {"idle": 175, "walk": 130, "run": 75, "jump": 80, "run_jump": 50, "duck": 50, "attack": 90,
                    "run_attack": 75, "kick": 60, "jump_kick": 55}

ANIMATION_LOOPS = {"idle": True, "walk": True, "run": True, "jump": False, "run_jump": False, "duck": False,
                   "attack": False, "run_attack": False, "kick": False, "jump_kick": False}

ANIMATION_SCALE_CORRECTIONS = {"idle": 1.0, "walk": 1.08, "run": 1.08, "jump": 1.1, "run_jump": 1.1, "duck": 1.0,
                               "attack": 2.8, "run_attack": 1.08, "kick": 2.6, "jump_kick": 2.4}