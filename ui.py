# -ui-#

# -ui-#

# -ui-#

import pygame
import os
import json
import sys
import config
from pyvidplayer2 import Video

# Standard UI Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (253, 117, 234)
LIGHT_GRAY = (180, 180, 180)


def draw_text(screen, text, font, text_col, x, y):
    screen.blit(font.render(text, True, text_col), (x, y))


class HUD:
    def __init__(self):
        self.font_small = pygame.font.SysFont("Lucida Sans", 20)
        self.font_tiny = pygame.font.SysFont("Lucida Sans", 14)
        self.font_rem = pygame.font.SysFont("Lucida Sans", 24, bold=True)

        # --- LOAD UI ICONS ---
        try:
            self.icon_pink = pygame.transform.smoothscale(pygame.image.load("mats/ui/icon_pink.png").convert_alpha(),
                                                          (48, 48))
            self.icon_purple = pygame.transform.smoothscale(
                pygame.image.load("mats/ui/icon_purple.png").convert_alpha(), (46, 46))
            self.icon_blue = pygame.transform.smoothscale(pygame.image.load("mats/ui/icon_blue.png").convert_alpha(),
                                                          (47, 47))
            self.icon_rainbow = pygame.transform.smoothscale(
                pygame.image.load("mats/ui/icon_rainbow.png").convert_alpha(), (47, 47))
        except pygame.error as e:
            print(f"Error loading HUD icons: {e}")
            self.icon_pink = self.icon_purple = self.icon_blue = self.icon_rainbow = None

        # --- LOAD & SCALE NEW GOTHIC HUD ELEMENTS ---
        try:
            self.succi_hud_img = pygame.transform.smoothscale(
                pygame.image.load("mats/ui/succi_hud.png").convert_alpha(), (450, 150))

            self.rems_hud_img = pygame.transform.smoothscale(
                pygame.image.load("mats/ui/rems_hud.png").convert_alpha(), (300, 60))

            self.spells_hud_img = pygame.transform.smoothscale(
                pygame.image.load("mats/ui/succi_spells_hud.png").convert_alpha(), (200, 138))

            self.health_cell_img = pygame.transform.smoothscale(
                pygame.image.load("mats/ui/health_cell.png").convert_alpha(), (36, 44))

        except pygame.error as e:
            print(f"Error loading new Gothic HUD frames: {e}")
            self.succi_hud_img = self.rems_hud_img = self.spells_hud_img = self.health_cell_img = None

    def draw(self, screen, screen_width, health, max_health, rem, left_spell, right_spell):
        if self.succi_hud_img:
            hud_x, hud_y = 10, 10
            screen.blit(self.succi_hud_img, (hud_x, hud_y))

            if self.health_cell_img:
                cell_start_x = hud_x + 151
                cell_start_y = hud_y + 51
                cell_spacing = 44

                for i in range(health):
                    if i < max_health:
                        current_cell_x = cell_start_x + (i * cell_spacing)
                        screen.blit(self.health_cell_img, (current_cell_x, cell_start_y))

            if self.rems_hud_img:
                rem_x = hud_x + 130
                rem_y = hud_y + 110
                screen.blit(self.rems_hud_img, (rem_x, rem_y))
                draw_text(screen, f"{rem}", self.font_rem, LIGHT_GRAY, rem_x + 95, rem_y + 10)

        if self.spells_hud_img:
            spells_x = screen_width - self.spells_hud_img.get_width() - 10
            spells_y = 10
            screen.blit(self.spells_hud_img, (spells_x, spells_y))

            left_icon_center = (spells_x + 73, spells_y + 68)
            right_icon_center = (spells_x + 123, spells_y + 68)

            if left_spell == "normal" and self.icon_pink:
                screen.blit(self.icon_pink, self.icon_pink.get_rect(center=left_icon_center))
            elif left_spell == "purple" and self.icon_purple:
                screen.blit(self.icon_purple, self.icon_purple.get_rect(center=left_icon_center))
            elif left_spell == "blue" and self.icon_blue:
                screen.blit(self.icon_blue, self.icon_blue.get_rect(center=left_icon_center))
            elif left_spell == "rainbow" and self.icon_rainbow:
                screen.blit(self.icon_rainbow, self.icon_rainbow.get_rect(center=left_icon_center))

            if right_spell == "normal" and self.icon_pink:
                screen.blit(self.icon_pink, self.icon_pink.get_rect(center=right_icon_center))
            elif right_spell == "purple" and self.icon_purple:
                screen.blit(self.icon_purple, self.icon_purple.get_rect(center=right_icon_center))
            elif right_spell == "blue" and self.icon_blue:
                screen.blit(self.icon_blue, self.icon_blue.get_rect(center=right_icon_center))
            elif right_spell == "rainbow" and self.icon_rainbow:
                screen.blit(self.icon_rainbow, self.icon_rainbow.get_rect(center=right_icon_center))


class LevelBanner:
    def __init__(self, level_num, screen_width):
        self.duration = 3500  # Total display time in milliseconds (3.5 seconds)
        self.start_time = pygame.time.get_ticks()

        try:
            img_path = f"mats/ui/level_huds/level {level_num} hud.png"
            raw_img = pygame.image.load(img_path).convert_alpha()
            # Scaled to your exact preferred size
            self.image = pygame.transform.smoothscale(raw_img, (1225, 448))
        except pygame.error as e:
            print(f"Error loading level banner for level {level_num}: {e}")
            self.image = pygame.Surface((1225, 448), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))

        self.rect = self.image.get_rect(center=(screen_width // 2, 230))

    def update_and_draw(self, screen):
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed > self.duration:
            return False  # Banner finished playing

        # Calculate alpha for smooth fade-in and fade-out
        # 0 - 500ms: Fade In
        # 500 - 2500ms: Fully Visible
        # 2500 - 3500ms: Fade Out
        if elapsed < 500:
            alpha = int((elapsed / 500) * 255)
        elif elapsed > 2500:
            alpha = int((1.0 - ((elapsed - 2500) / 1000)) * 255)
        else:
            alpha = 255

        alpha = max(0, min(255, alpha))

        # Apply alpha to a copy of the image for smooth fading
        fade_image = self.image.copy()
        fade_image.set_alpha(alpha)
        screen.blit(fade_image, self.rect)
        return True

    def is_finished(self):
        return pygame.time.get_ticks() - self.start_time > self.duration


# PAUSE MENU #
class PauseMenu:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.font_big = pygame.font.SysFont("Lucida Sans", 48)
        self.font_med = pygame.font.SysFont("Lucida Sans", 32)
        self.font_small = pygame.font.SysFont("Lucida Sans", 20)

        # Load the new unified background image
        try:
            pause_bg_raw = pygame.image.load("mats/ui/pause_screen1.png").convert()
            self.bg = pygame.transform.smoothscale(pause_bg_raw, (self.w, self.h))
        except pygame.error:
            self.bg = None

        # Load and scale the new save button to fit the center frame (Made slightly bigger)
        try:
            raw_save = pygame.image.load("mats/ui/save_hud1.png").convert_alpha()
            self.save_b = pygame.transform.smoothscale(raw_save, (335, 230))
            self.save_h = pygame.transform.smoothscale(raw_save, (366, 245))
        except pygame.error:
            self.save_b = self.save_h = None

        # Calculate centers for the left and right mirrors
        self.left_cx = self.w // 2 - 370
        self.right_cx = self.w // 2 + 370

        if self.save_b:
            # Nestle the save button in the bottom-center hole (Shifted slightly right)
            self.save_rect = self.save_b.get_rect(center=(self.w // 2 + 15, self.h // 2 + 180))
        else:
            self.save_rect = pygame.Rect(self.w // 2 - 167, self.h // 2 + 65, 335, 230)

        try:
            self.icon_pink = pygame.transform.smoothscale(pygame.image.load("mats/ui/icon_pink.png").convert_alpha(), (55, 55))
            self.icon_purple = pygame.transform.smoothscale(pygame.image.load("mats/ui/icon_purple.png").convert_alpha(), (55, 55))
            self.icon_blue = pygame.transform.smoothscale(pygame.image.load("mats/ui/icon_blue.png").convert_alpha(), (55, 55))
            self.icon_rainbow = pygame.transform.smoothscale(pygame.image.load("mats/ui/icon_rainbow.png").convert_alpha(), (55, 55))
            self.icon_tinera = pygame.transform.smoothscale(pygame.image.load("mats/ui/icon_tinera.png").convert_alpha(), (55, 55))
        except pygame.error:
            self.icon_pink = self.icon_purple = self.icon_blue = self.icon_rainbow = self.icon_tinera = None

        # Multi-Slot Save Variables
        self.save_state = None
        self.selected_save_slot = None
        self.save_slots = []
        self.save_input_text = ""

        # Position the inventory grid inside the left mirror (Shifted further left)
        self.grid_rects = []
        start_x = self.left_cx - 200
        start_y = self.h // 2 + 5
        for row in range(3):
            for col in range(3):
                self.grid_rects.append(pygame.Rect(start_x + col * 85, start_y + row * 85, 75, 75))

        self.selected_spell = None
        self.popup_active = False
        self.popup_rect_left = pygame.Rect(0, 0, 120, 35)
        self.popup_rect_right = pygame.Rect(0, 0, 120, 35)

    def _load_save_data(self):
        self.save_slots = []

        if getattr(sys, 'frozen', False):
            save_dir = os.path.join(os.path.dirname(sys.executable), "saves")
        else:
            save_dir = os.path.abspath("saves")

        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)

        y_offset = self.h // 2 - 150
        center_x = self.w // 2

        for i in range(1, 6):
            file_path = os.path.join(save_dir, f"save{i}.json")
            rect = pygame.Rect(center_x - 200, y_offset, 400, 50)

            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        name = data.get("save_name", f"Save {i}")
                except Exception:
                    name = f"Save {i} (Corrupted)"
                self.save_slots.append({"rect": rect, "name": name, "slot": i, "empty": False})
            else:
                self.save_slots.append({"rect": rect, "name": f"Slot {i} - Empty", "slot": i, "empty": True})
            y_offset += 65

    def update(self, mouse_pos, mouse_click, owned_spells, player_has_tinera):
        result = None
        if mouse_click:
            if self.save_state == "TYPE":
                return None

            if self.save_state == "SELECT":
                clicked_inside = False
                for slot in self.save_slots:
                    if slot["rect"].collidepoint(mouse_pos):
                        self.selected_save_slot = slot["slot"]
                        self.save_input_text = f"Save_0{slot['slot']}" if slot["empty"] else slot["name"]
                        self.save_state = "TYPE"
                        clicked_inside = True
                        break
                if not clicked_inside:
                    self.save_state = None
                return None

            if self.save_rect.collidepoint(mouse_pos):
                self._load_save_data()
                self.save_state = "SELECT"
                return None

            if self.popup_active:
                if self.popup_rect_left.collidepoint(mouse_pos):
                    result = {"action": "EQUIP", "slot": "left", "spell": self.selected_spell}
                    self.popup_active = False
                elif self.popup_rect_right.collidepoint(mouse_pos):
                    result = {"action": "EQUIP", "slot": "right", "spell": self.selected_spell}
                    self.popup_active = False
                else:
                    self.popup_active = False
            else:
                for i, spell in enumerate(owned_spells):
                    if i < len(self.grid_rects) and self.grid_rects[i].collidepoint(mouse_pos):
                        self.selected_spell = spell
                        self.popup_active = True
                        self.popup_rect_left.topleft = (mouse_pos[0] + 10, mouse_pos[1] - 20)
                        self.popup_rect_right.topleft = (mouse_pos[0] + 10, mouse_pos[1] + 20)
                        return result

                if player_has_tinera and len(self.grid_rects) > 4 and self.grid_rects[4].collidepoint(mouse_pos):
                    result = {"action": "TOGGLE_TINERA"}
                    return result

        return result

    def draw(self, screen, owned_spells, mouse_pos, player_has_tinera, tinera_active=True, tinera_icon_override=None):
        # 1. Draw the new unified background directly
        if self.bg:
            screen.blit(self.bg, (0, 0))
        else:
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

        center_x = self.w // 2

        # Moved resume instructions to the bottom so it doesn't overlap the new header
        draw_text(screen, "Press 'P' or 'ESC' to Resume", self.font_small, PINK, center_x - 135, self.h - 40)

        # 2. Draw the Save Button
        if self.save_b and self.save_h:
            if self.save_rect.collidepoint(mouse_pos):
                hover_rect = self.save_h.get_rect(center=self.save_rect.center)
                screen.blit(self.save_h, hover_rect)
            else:
                screen.blit(self.save_b, self.save_rect)

        # 3. Draw Inventory Grid
        for i, rect in enumerate(self.grid_rects):
            pygame.draw.rect(screen, LIGHT_GRAY, rect, 2, border_radius=5)

            if i < len(owned_spells):
                spell = owned_spells[i]
                if spell == "normal" and self.icon_pink:
                    screen.blit(self.icon_pink, self.icon_pink.get_rect(center=rect.center))
                elif spell == "purple" and self.icon_purple:
                    screen.blit(self.icon_purple, self.icon_purple.get_rect(center=rect.center))
                elif spell == "blue" and self.icon_blue:
                    screen.blit(self.icon_blue, self.icon_blue.get_rect(center=rect.center))
                elif spell == "rainbow" and self.icon_rainbow:
                    screen.blit(self.icon_rainbow, self.icon_rainbow.get_rect(center=rect.center))

            elif i == 4 and player_has_tinera:
                active_icon = tinera_icon_override if tinera_icon_override else self.icon_tinera
                if active_icon:
                    if not tinera_active:
                        dim_icon = active_icon.copy()
                        dim_icon.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_MULT)
                        screen.blit(dim_icon, dim_icon.get_rect(center=rect.center))
                    else:
                        screen.blit(active_icon, active_icon.get_rect(center=rect.center))

            if rect.collidepoint(mouse_pos) and not self.popup_active:
                pygame.draw.rect(screen, WHITE, rect, 3, border_radius=5)

        # 4. Draw Controls Text (Shifted further right)
        ctrl_y = self.h // 2 + 5
        ctrl_x = self.right_cx - 55

        draw_text(screen, "WASD / Arrows : Move & Duck", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y)
        draw_text(screen, "Shift      : Run", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y + 30)
        draw_text(screen, "Space      : Jump", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y + 60)
        draw_text(screen, "Left Click : Use Left Spell", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y + 90)
        draw_text(screen, "Right Click: Use Right Spell", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y + 120)
        draw_text(screen, "3 / MMB    : Melee Kick", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y + 150)
        draw_text(screen, "E Key      : Enter/Exit", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y + 180)
        draw_text(screen, "P / ESC    : Pause", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y + 210)

        if self.popup_active:
            pygame.draw.rect(screen, BLACK, self.popup_rect_left)
            col_l = PINK if self.popup_rect_left.collidepoint(mouse_pos) else WHITE
            pygame.draw.rect(screen, col_l, self.popup_rect_left, 2)
            draw_text(screen, "Equip Left", self.font_small, col_l, self.popup_rect_left.x + 10, self.popup_rect_left.y + 8)

            pygame.draw.rect(screen, BLACK, self.popup_rect_right)
            col_r = PINK if self.popup_rect_right.collidepoint(mouse_pos) else WHITE
            pygame.draw.rect(screen, col_r, self.popup_rect_right, 2)
            draw_text(screen, "Equip Right", self.font_small, col_r, self.popup_rect_right.x + 5, self.popup_rect_right.y + 8)

        # --- MULTI-SLOT SAVE SCREENS ---
        if self.save_state == "SELECT":
            dark_overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 220))
            screen.blit(dark_overlay, (0, 0))

            draw_text(screen, "SELECT A SAVE SLOT", self.font_big, PINK, center_x - 200, 100)

            for slot in self.save_slots:
                rect = slot["rect"]
                col = PINK if rect.collidepoint(mouse_pos) else LIGHT_GRAY
                pygame.draw.rect(screen, (20, 10, 30), rect, border_radius=8)
                pygame.draw.rect(screen, col, rect, 3, border_radius=8)

                text_surf = self.font_med.render(slot["name"], True, col)
                screen.blit(text_surf, text_surf.get_rect(center=rect.center))

            draw_text(screen, "Click anywhere outside to cancel", self.font_small, LIGHT_GRAY, center_x - 140, self.h - 80)

        elif self.save_state == "TYPE":
            dialog_rect = pygame.Rect(center_x - 250, self.h // 2 - 100, 500, 200)
            pygame.draw.rect(screen, (20, 10, 30), dialog_rect, border_radius=12)
            pygame.draw.rect(screen, PINK, dialog_rect, 3, border_radius=12)

            draw_text(screen, f"SAVE NAME FOR SLOT {self.selected_save_slot}:", self.font_small, WHITE, center_x - 115, dialog_rect.y + 25)

            input_box_rect = pygame.Rect(dialog_rect.x + 40, dialog_rect.y + 65, 420, 50)
            pygame.draw.rect(screen, BLACK, input_box_rect, border_radius=6)
            pygame.draw.rect(screen, LIGHT_GRAY, input_box_rect, 2, border_radius=6)

            draw_text(screen, self.save_input_text + "|", self.font_med, PINK, input_box_rect.x + 15, input_box_rect.y + 8)
            draw_text(screen, "Press ENTER to Save | ESC to Cancel", self.font_small, LIGHT_GRAY, dialog_rect.x + 75, dialog_rect.y + 135)

class DeathScreen:
    def __init__(self, w, h):
        self.w = w
        self.h = h  # 800
        self.font_big = pygame.font.SysFont("Lucida Sans", 48)
        self.font_small = pygame.font.SysFont("Lucida Sans", 20)
        try:
            self.bg = pygame.transform.smoothscale(pygame.image.load("mats/ui/death_screen.png").convert_alpha(),
                                                   (w, h))

            # --- NEW CENTER HUD ---
            # Scale proportionally to match screen height
            center_raw = pygame.image.load("mats/ui/center_death_hud.png").convert_alpha()
            c_raw_w, c_raw_h = center_raw.get_size()
            c_ratio = self.h / c_raw_h
            self.overlay = pygame.transform.smoothscale(center_raw, (int(c_raw_w * c_ratio), self.h))

            # --- LOAD & SCALE THE OUTER FRAMES ---
            frame_raw = pygame.image.load("mats/ui/small window frame.png").convert_alpha()
            f_raw_w, f_raw_h = frame_raw.get_size()
            f_ratio = self.h / f_raw_h
            self.frame_w = int(f_raw_w * f_ratio)
            self.frame_img = pygame.transform.smoothscale(frame_raw, (self.frame_w, self.h))

            # --- LOAD & SCALE SUCCI ---
            succi_raw = pygame.image.load("mats/ui/Succi_alpha.png").convert_alpha()
            s_raw_w, s_raw_h = succi_raw.get_size()
            s_target_h = int(self.h * 0.95)
            s_ratio = s_target_h / s_raw_h
            self.succi_img = pygame.transform.smoothscale(succi_raw, (int(s_raw_w * s_ratio), s_target_h))

            # --- LOAD & SCALE ADELAIDE ---
            adelaide_raw = pygame.image.load("mats/ui/Adelaide_alpha.png").convert_alpha()
            a_raw_w, a_raw_h = adelaide_raw.get_size()
            a_target_h = int(self.h * 0.95)
            a_ratio = a_target_h / a_raw_h
            self.adelaide_img = pygame.transform.smoothscale(adelaide_raw, (int(a_raw_w * a_ratio), a_target_h))

        except pygame.error as e:
            print(f"Error loading DeathScreen assets: {e}")
            self.bg = pygame.Surface((w, h))
            self.overlay = None
            self.frame_img = None
            self.succi_img = None
            self.adelaide_img = None

    def draw_centered_scaled_text(self, screen, text, font, color, center_x, y_pos, scale):
        raw_text = font.render(text, True, color)
        scaled_w = int(raw_text.get_width() * scale)
        scaled_h = int(raw_text.get_height() * scale)
        scaled_text = pygame.transform.smoothscale(raw_text, (scaled_w, scaled_h))
        text_rect = scaled_text.get_rect(center=(center_x, y_pos))
        screen.blit(scaled_text, text_rect)

    def draw(self, screen, current_state, checkpoint):
        # 1. Background
        screen.blit(self.bg, (0, 0))

        # 2. Outer Frames
        if self.frame_img:
            screen.blit(self.frame_img, (0, 0))
            screen.blit(self.frame_img, (self.w - self.frame_w, 0))

        # 3. Characters (Inside their frames)
        if self.succi_img:
            s_rect = self.succi_img.get_rect(midbottom=(self.frame_w // 2, self.h - 15))
            screen.blit(self.succi_img, s_rect)

        if self.adelaide_img:
            a_rect = self.adelaide_img.get_rect(midbottom=(self.w - (self.frame_w // 2), self.h - 15))
            screen.blit(self.adelaide_img, a_rect)

        # 4. Center Tombstone Overlay (Draw ON TOP of characters)
        if self.overlay:
            do_rect = self.overlay.get_rect(center=(self.w // 2, self.h // 2))
            screen.blit(self.overlay, do_rect)

        # 5. Dynamic Text Placements
        center_x = self.w // 2 - 10

        # Tweak this Y value to move "LEVEL X" up or down so it sits right under "DIED ON:"
        level_y_pos = self.h // 2 + 120

        # Tweak this Y value to move the "Restart" text under "PRESS SPACE"
        restart_y_pos = self.h - 160

        # Draw the dynamic Level Name (e.g., "LEVEL 1")
        self.draw_centered_scaled_text(screen, f"{current_state.replace('_', ' ')}", self.font_big,
                                       pygame.Color("turquoise1"), center_x, level_y_pos, 0.45)

        # Draw the dynamic Restart instruction
        if checkpoint in [2, 3, 4, 5, 6, 7]:
            self.draw_centered_scaled_text(screen, "PRESS '1' TO RESTART AT LEVEL 1", self.font_small,
                                           pygame.Color("plum1"), center_x, restart_y_pos, 0.9)


class MainMenu:
    def __init__(self, w, h):
        try:
            self.bg = pygame.transform.smoothscale(pygame.image.load("mats/ui/start_screen_2.png").convert(), (w, h))

            raw_play = pygame.image.load("mats/ui/play1.png").convert_alpha()
            raw_controls = pygame.image.load("mats/ui/controls1.png").convert_alpha()
            raw_load = pygame.image.load("mats/ui/load1.png").convert_alpha()

            # --- 1. BUTTON SIZING (Adjust width, height here) ---
            # Scaled up to fill the dark inner frames naturally
            self.play_b = pygame.transform.smoothscale(raw_play, (400, 240))
            self.ctrl_b = pygame.transform.smoothscale(raw_controls, (330, 180))
            self.load_b = pygame.transform.smoothscale(raw_load, (270, 270))

            # 10% hover scaling
            self.play_h = pygame.transform.smoothscale(raw_play, (int(400 * 1.10), int(240 * 1.10)))
            self.ctrl_h = pygame.transform.smoothscale(raw_controls, (int(330 * 1.10), int(180 * 1.10)))
            self.load_h = pygame.transform.smoothscale(raw_load, (int(270 * 1.10), int(270 * 1.10)))

            # --- 2. BUTTON POSITIONING (Adjust X, Y centers here) ---
            # CONTROLS: Left window (centered around x=200, moved up into the opening)
            self.ctrl_rect = self.ctrl_b.get_rect(center=(223, h // 2 + 140))

            # PLAY: Center archway (centered horizontally, raised to rest under the arch crest)
            self.play_rect = self.play_b.get_rect(center=(w // 2 + 3, h // 2 + 130))

            # LOAD: Right window (centered around x=w - 200, positioned inside the frame)
            self.load_rect = self.load_b.get_rect(center=(w - 220, h // 2 + 140))

        except pygame.error as e:
            print(f"Menu Asset Error: {e}")
            self.bg = pygame.Surface((w, h))

        self.sub_menu = None
        self.font_title = pygame.font.SysFont("Lucida Sans", 48)
        self.font_text = pygame.font.SysFont("Lucida Sans", 30)
        self.font_small = pygame.font.SysFont("Lucida Sans", 16)
        self.save_slots = []

    def _load_save_data(self):
        self.save_slots = []

        # Get the absolute path for saves regardless of temporary folders
        if getattr(sys, 'frozen', False):
            save_dir = os.path.join(os.path.dirname(sys.executable), "saves")
        else:
            save_dir = os.path.abspath("saves")

        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)

        y_offset = self.bg.get_height() // 2 - 150
        center_x = self.bg.get_width() // 2

        for i in range(1, 6):
            file_path = os.path.join(save_dir, f"save{i}.json")
            rect = pygame.Rect(center_x - 200, y_offset, 400, 50)
            del_rect = pygame.Rect(center_x + 140, y_offset + 10, 50, 30)

            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        name = data.get("save_name", f"Save {i}")
                except Exception:
                    name = f"Save {i} (Corrupt)"
                self.save_slots.append({"rect": rect, "del_rect": del_rect, "name": name, "slot": i, "empty": False})
            else:
                self.save_slots.append(
                    {"rect": rect, "del_rect": None, "name": f"Slot {i} - Empty", "slot": i, "empty": True})
            y_offset += 65

    def update(self, mouse_pos, mouse_click):
        if mouse_click:
            if self.sub_menu == "LOAD":
                for slot in self.save_slots:
                    if not slot["empty"] and slot["del_rect"] and slot["del_rect"].collidepoint(mouse_pos):
                        return {"action": "DELETE", "slot": slot["slot"]}
                    elif slot["rect"].collidepoint(mouse_pos) and not slot["empty"]:
                        self.sub_menu = None
                        return {"action": "LOAD", "slot": slot["slot"]}

                # Close if clicked outside
                if not any(slot["rect"].collidepoint(mouse_pos) for slot in self.save_slots):
                    self.sub_menu = None
                return None
            elif self.sub_menu == "CONTROLS":
                self.sub_menu = None
                return None
            else:
                if self.play_rect.collidepoint(mouse_pos):
                    return "PLAY"
                elif self.ctrl_rect.collidepoint(mouse_pos):
                    self.sub_menu = "CONTROLS"
                elif self.load_rect.collidepoint(mouse_pos):
                    self.sub_menu = "LOAD"
                    self._load_save_data()
        return None

    def draw(self, screen, mouse_pos):
        screen.blit(self.bg, (0, 0))

        if self.ctrl_rect.collidepoint(mouse_pos) and not self.sub_menu:
            screen.blit(self.ctrl_h, self.ctrl_h.get_rect(center=self.ctrl_rect.center))
        else:
            screen.blit(self.ctrl_b, self.ctrl_rect)

        if self.play_rect.collidepoint(mouse_pos) and not self.sub_menu:
            screen.blit(self.play_h, self.play_h.get_rect(center=self.play_rect.center))
        else:
            screen.blit(self.play_b, self.play_rect)

        if self.load_rect.collidepoint(mouse_pos) and not self.sub_menu:
            screen.blit(self.load_h, self.load_h.get_rect(center=self.load_rect.center))
        else:
            screen.blit(self.load_b, self.load_rect)

        if self.sub_menu == "LOAD":
            overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            screen.blit(overlay, (0, 0))

            draw_text(screen, "LOAD GAME", self.font_title, PINK, screen.get_width() // 2 - 130, 80)

            for slot in self.save_slots:
                rect = slot["rect"]
                col = PINK if rect.collidepoint(mouse_pos) else LIGHT_GRAY

                pygame.draw.rect(screen, (20, 10, 30), rect, border_radius=8)
                pygame.draw.rect(screen, col, rect, 3, border_radius=8)

                text_surf = self.font_text.render(slot["name"], True, col)
                screen.blit(text_surf, text_surf.get_rect(center=rect.center))

                # Draw Delete [ DEL ] Button for Populated Slots
                if not slot["empty"] and slot["del_rect"]:
                    d_rect = slot["del_rect"]
                    d_col = (255, 50, 50) if d_rect.collidepoint(mouse_pos) else (150, 50, 50)
                    pygame.draw.rect(screen, d_col, d_rect, border_radius=4)
                    draw_text(screen, "DEL", self.font_small, WHITE, d_rect.x + 5, d_rect.y + 4)

            sub = self.font_text.render("Click outside slots to return", True, LIGHT_GRAY)
            screen.blit(sub, sub.get_rect(center=(screen.get_width() // 2, screen.get_height() - 60)))

        elif self.sub_menu == "CONTROLS":
            overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            screen.blit(overlay, (0, 0))
            lines = [
                ("CONTROLS", PINK),
                ("WASD / Arrows : Move & Duck", (100, 200, 255)),
                ("Shift : Run", (100, 200, 255)),
                ("Space : Jump", (100, 200, 255)),
                ("Left Mouse : Cast Red Fireball", (100, 200, 255)),
                ("Right Mouse : Cast Purple Magic", (100, 200, 255)),
                ("3 / MMB : Melee Kick", (100, 200, 255)),
                ("E Key : Enter / Exit Merchant", (100, 200, 255)),
                ("P / ESC : Pause", PINK),
                ("", BLACK),
                ("(Click anywhere to return)", LIGHT_GRAY)
            ]

            for i, (line, color) in enumerate(lines):
                text = self.font_text.render(line, True, color)
                screen.blit(text,
                            text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 150 + (i * 40))))


class Merchant_UI:
    def __init__(self, screen_width, screen_height, sold_out_ref):
        try:
            self.sold_out = sold_out_ref
            raw_bg = pygame.image.load("mats/ui/M_inventory_empty.png").convert()
            self.bg = pygame.transform.smoothscale(raw_bg, (screen_width, screen_height))

            try:
                raw_exit = pygame.image.load("mats/ui/exit_hud.png").convert_alpha()
                self.exit_hud_img = pygame.transform.smoothscale(raw_exit, (390, 140))
                # Create the hover effect image (10% larger)
                self.exit_hud_hover = pygame.transform.smoothscale(raw_exit, (int(390 * 1.10), int(140 * 1.10)))
                # Set up the collision rectangle based on your specific screen coordinates
                self.exit_rect = self.exit_hud_img.get_rect(topleft=(880, 5))
            except pygame.error as e:
                print(f"Error loading exit HUD: {e}")
                self.exit_hud_img = None
                self.exit_hud_hover = None
                self.exit_rect = None

            self.health_p = pygame.transform.smoothscale(pygame.image.load("mats/ui/health_p.png").convert_alpha(),
                                                         (110, 150))
            self.mana_p = pygame.transform.smoothscale(pygame.image.load("mats/ui/mana_p.png").convert_alpha(),
                                                       (110, 150))
            self.purple_p = pygame.transform.smoothscale(pygame.image.load("mats/ui/purple_p.png").convert_alpha(),
                                                         (110, 150))
            self.rainbow_p = pygame.transform.smoothscale(
                pygame.image.load("mats/ui/secret_potion.png").convert_alpha(), (110, 150))

            wings_raw = pygame.image.load("mats/ui/wings_p_ss.png").convert_alpha()
            ww, wh = wings_raw.get_size()
            self.wings_p = pygame.transform.smoothscale(wings_raw.subsurface((0, int(wh * 0.15), ww, int(wh * 0.70))),
                                                        (110, 150))

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

            raw_left = pygame.image.load("mats/ui/left.png").convert_alpha()
            raw_right = pygame.image.load("mats/ui/right.png").convert_alpha()
            arrow_w, arrow_h = 245, 120
            self.left_arrow_img = pygame.transform.smoothscale(raw_left, (arrow_w, arrow_h))
            self.right_arrow_img = pygame.transform.smoothscale(raw_right, (arrow_w, arrow_h))
            hover_w, hover_h = int(arrow_w * 1.10), int(arrow_h * 1.10)
            self.left_arrow_hover = pygame.transform.smoothscale(raw_left, (hover_w, hover_h))
            self.right_arrow_hover = pygame.transform.smoothscale(raw_right, (hover_w, hover_h))
        except pygame.error as e:
            print(f"Error loading UI: {e}")
            import sys;
            sys.exit()

        self.grid_rects = [
            pygame.Rect(680, 165, 130, 130), pygame.Rect(890, 165, 130, 130), pygame.Rect(1100, 165, 130, 130),
            pygame.Rect(680, 360, 130, 130), pygame.Rect(890, 360, 130, 130), pygame.Rect(1100, 360, 130, 130),
            pygame.Rect(680, 555, 130, 130), pygame.Rect(890, 555, 130, 130), pygame.Rect(1100, 555, 130, 130)
        ]
        self.buy_rect = pygame.Rect(270, 650, 210, 65)
        self.left_arrow_rect = self.left_arrow_img.get_rect(midright=(self.buy_rect.left - 15, self.buy_rect.centery))
        self.right_arrow_rect = self.right_arrow_img.get_rect(midleft=(self.buy_rect.right + 15, self.buy_rect.centery))

        self.inventory = [
            {"id": "Health Potion", "img": self.health_p, "title": "Base Health", "desc": ["Unlocks +3 Max Health."],
             "cost": 50, "color": (50, 255, 50)},
            {"id": "Teal Potion", "img": self.teal_p, "title": "Minor Heal", "desc": ["Restores up to 3 Health."],
             "cost": 60, "color": (50, 200, 255)},
            {"id": "Emerald Potion", "img": self.emerald_p, "title": "Advanced Health", "desc": ["Adds +2 Max Health."],
             "cost": 150, "color": (100, 255, 100)},
            {"id": "Pink Potion", "img": self.pink_p, "title": "Major Heal", "desc": ["Restores up to 5 Health."],
             "cost": 100, "color": (255, 100, 200)},
            {"id": "Mysterious Potion", "img": self.mysterious_p, "title": "Mysterious Potion",
             "desc": ["Unlocks Double Jump."], "cost": 200, "color": (150, 50, 255)},
            {"id": "Silver Potion", "img": self.silver_p, "title": "Silver Potion", "desc": ["Unlocks Melee Attack."],
             "cost": 50, "color": (220, 220, 220)},
            {"id": "Wings Potion", "img": self.wings_p, "title": "Wings Potion", "desc": ["Unlocks her Wings."],
             "cost": 200, "color": (255, 200, 50)},
            {"id": "Purple Potion", "img": self.purple_p, "title": "Purple Potion", "desc": ["Unlocks Void-ball."],
             "cost": 50, "color": (180, 50, 255)},
            {"id": "Blue Potion", "img": self.mana_p, "title": "Blue Potion", "desc": ["Unlocks Sapphire-ball"],
             "cost": 50, "color": (50, 50, 255)},
            {"id": "Rainbow Potion", "img": self.rainbow_p, "title": "Rainbow Potion", "desc": ["Unlocks Rain-ball."],
             "cost": 50, "color": (255, 100, 255)},
            {"id": "Royal Potion", "img": self.royal_p, "title": "Royal Potion", "desc": ["Summons companion..."],
             "cost": 50, "color": (255, 180, 50)},
            {"id": "Gold Potion", "img": self.gold_p, "title": "Gold Potion", "desc": ["Adds +1 Max Health."],
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

            # --- NEW EXIT LOGIC TRIGGER ---
            if getattr(self, 'exit_rect', None) and self.exit_rect.collidepoint(mouse_pos):
                return "EXIT_CLICKED"

            if self.right_arrow_rect.collidepoint(mouse_pos) and self.current_page < self.max_pages - 1:
                self.current_page += 1
                self.selected_item_data = None
            elif self.left_arrow_rect.collidepoint(mouse_pos) and self.current_page > 0:
                self.current_page -= 1
                self.selected_item_data = None
            elif self.buy_rect.collidepoint(mouse_pos) and self.selected_item_data:
                item_id = self.selected_item_data["id"]
                if rem >= self.selected_item_data["cost"] and not self.sold_out.get(item_id, False):
                    bought_item = item_id
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

        for i, item in enumerate(page_items):
            if not self.sold_out.get(item["id"], False):
                slot = self.grid_rects[i]
                screen.blit(item["img"], (slot.x + 10, slot.y - 10))
                if slot.collidepoint(mouse_pos) or (
                        self.selected_item_data and self.selected_item_data["id"] == item["id"]):
                    pygame.draw.rect(screen, WHITE, slot, 3)

        if self.current_page > 0:
            if self.left_arrow_rect.collidepoint(mouse_pos):
                hover_rect = self.left_arrow_hover.get_rect(center=self.left_arrow_rect.center)
                screen.blit(self.left_arrow_hover, hover_rect)
            else:
                screen.blit(self.left_arrow_img, self.left_arrow_rect)

        if self.current_page < self.max_pages - 1:
            if self.right_arrow_rect.collidepoint(mouse_pos):
                hover_rect = self.right_arrow_hover.get_rect(center=self.right_arrow_rect.center)
                screen.blit(self.right_arrow_hover, hover_rect)
            else:
                screen.blit(self.right_arrow_img, self.right_arrow_rect)

        if self.buy_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (255, 50, 50), self.buy_rect, 3, border_radius=8)

        screen.blit(self.font_rem.render(str(rem), True, PINK), (280, 570))

        if self.selected_item_data and not self.sold_out.get(self.selected_item_data["id"], False):
            text_x = 240
            screen.blit(
                self.font_title.render(self.selected_item_data["title"], True, self.selected_item_data["color"]),
                (text_x, 180))
            y_offset = 230
            for line in self.selected_item_data["desc"]:
                screen.blit(self.font_desc.render(line, True, (190, 200, 200)), (text_x, y_offset))
                y_offset += 25
            screen.blit(self.font_title.render(f"COST: {self.selected_item_data['cost']} REM", True, PINK),
                        (text_x, y_offset + 10))

        # --- UPDATED EXIT HUD DRAWING ---
        if self.exit_hud_img and getattr(self, 'exit_rect', None):
            if self.exit_rect.collidepoint(mouse_pos):
                # Draw the hovered version centered over the standard rect
                hover_rect = self.exit_hud_hover.get_rect(center=self.exit_rect.center)
                screen.blit(self.exit_hud_hover, hover_rect)
            else:
                # Draw the standard version
                screen.blit(self.exit_hud_img, self.exit_rect)


class CutsceneScreen:
    def __init__(self, screen_width, screen_height, video_path):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.vid = Video(video_path)
        self.vid.resize((screen_width, screen_height))
        self.vid.pause()

        # Load custom skip button maintaining natural proportions (~1.7:1)
        try:
            raw_skip = pygame.image.load("mats/ui/skip_button666.png").convert_alpha()
            # Standard un-flattened size
            self.skip_img = pygame.transform.smoothscale(raw_skip, (280, 220))
            # 10% larger for hover effect
            self.skip_img_hover = pygame.transform.smoothscale(raw_skip, (int(280 * 1.10), int(220 * 1.10)))
        except pygame.error as e:
            print(f"Error loading skip button: {e}")
            self.skip_img = None
            self.skip_img_hover = None

        # Positioned right over the corner watermark (centered at x=1260, y=700)
        self.skip_rect = pygame.Rect(0, 0, 280, 220)
        self.skip_rect.center = (self.screen_width - 140, self.screen_height - 110)

    def start(self):
        self.vid.restart()
        self.vid.resume()

    def update(self, mouse_pos, mouse_click, allow_skip=True):
        if allow_skip and mouse_click and self.skip_rect.collidepoint(mouse_pos):
            self.vid.close()
            return True

        if not self.vid.active:
            self.vid.close()
            return True

        return False

    def draw(self, screen, mouse_pos, show_skip=True):
        # Draw current video frame
        self.vid.draw(screen, (0, 0))

        # Draw skip button with hover enlargement
        if show_skip and self.skip_img:
            if self.skip_rect.collidepoint(mouse_pos) and self.skip_img_hover:
                hover_rect = self.skip_img_hover.get_rect(center=self.skip_rect.center)
                screen.blit(self.skip_img_hover, hover_rect.topleft)
            else:
                screen.blit(self.skip_img, self.skip_rect.topleft)
        elif show_skip and not self.skip_img:
            pygame.draw.rect(screen, (100, 100, 100), self.skip_rect, border_radius=8)

    def stop(self):
        self.vid.close()