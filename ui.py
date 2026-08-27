import pygame
import config

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

            # INCREASED: Scaled up to 280x58 so it's much more readable
            self.rems_hud_img = pygame.transform.smoothscale(
                pygame.image.load("mats/ui/rems_hud.png").convert_alpha(), (300, 60))

            self.spells_hud_img = pygame.transform.smoothscale(
                pygame.image.load("mats/ui/succi_spells_hud.png").convert_alpha(), (200, 138))

            # INCREASED: Scaled up to 38x54 to actually fill the cell window
            self.health_cell_img = pygame.transform.smoothscale(
                pygame.image.load("mats/ui/health_cell.png").convert_alpha(), (36, 44))

        except pygame.error as e:
            print(f"Error loading new Gothic HUD frames: {e}")
            self.succi_hud_img = self.rems_hud_img = self.spells_hud_img = self.health_cell_img = None

    def draw(self, screen, screen_width, health, max_health, rem, left_spell, right_spell):
        # --- DRAW SUCCI HEALTH HUD ---
        if self.succi_hud_img:
            hud_x, hud_y = 10, 10
            screen.blit(self.succi_hud_img, (hud_x, hud_y))

            # --- DRAW GREEN HEALTH CELLS ---
            if self.health_cell_img:
                # FIXED: Shifted left to slot 1, shifted up to fit, and widened the gap between cells
                cell_start_x = hud_x + 151
                cell_start_y = hud_y + 51
                cell_spacing = 44

                for i in range(health):
                    if i < max_health:
                        current_cell_x = cell_start_x + (i * cell_spacing)
                        screen.blit(self.health_cell_img, (current_cell_x, cell_start_y))

            # --- DRAW REMS HUD ---
            if self.rems_hud_img:
                # FIXED: Manually pushed to the right so it aligns under the health track
                rem_x = hud_x + 130
                rem_y = hud_y + 110
                screen.blit(self.rems_hud_img, (rem_x, rem_y))

                # FIXED: Centered the text inside the black void of the new larger REM frame
                draw_text(screen, f"{rem}", self.font_rem, LIGHT_GRAY, rem_x + 95, rem_y + 10)

        # --- DRAW SPELLS HUD ---
        if self.spells_hud_img:
            spells_x = screen_width - self.spells_hud_img.get_width() - 10
            spells_y = 10
            screen.blit(self.spells_hud_img, (spells_x, spells_y))

            left_icon_center = (spells_x + 73, spells_y + 68)
            right_icon_center = (spells_x + 123, spells_y + 68)

            # Left Click Box
            if left_spell == "normal" and self.icon_pink:
                screen.blit(self.icon_pink, self.icon_pink.get_rect(center=left_icon_center))
            elif left_spell == "purple" and self.icon_purple:
                screen.blit(self.icon_purple, self.icon_purple.get_rect(center=left_icon_center))
            elif left_spell == "blue" and self.icon_blue:
                screen.blit(self.icon_blue, self.icon_blue.get_rect(center=left_icon_center))
            elif left_spell == "rainbow" and self.icon_rainbow:
                screen.blit(self.icon_rainbow, self.icon_rainbow.get_rect(center=left_icon_center))

            # Right Click Box
            if right_spell == "normal" and self.icon_pink:
                screen.blit(self.icon_pink, self.icon_pink.get_rect(center=right_icon_center))
            elif right_spell == "purple" and self.icon_purple:
                screen.blit(self.icon_purple, self.icon_purple.get_rect(center=right_icon_center))
            elif right_spell == "blue" and self.icon_blue:
                screen.blit(self.icon_blue, self.icon_blue.get_rect(center=right_icon_center))
            elif right_spell == "rainbow" and self.icon_rainbow:
                screen.blit(self.icon_rainbow, self.icon_rainbow.get_rect(center=right_icon_center))


class PauseMenu:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.font_big = pygame.font.SysFont("Lucida Sans", 48)
        self.font_med = pygame.font.SysFont("Lucida Sans", 32)
        self.font_small = pygame.font.SysFont("Lucida Sans", 20)

        try:
            pause_bg_raw = pygame.image.load("mats/ui/pause1.png").convert_alpha()
            # Scaled WAY up so the mirrors are massive (edges will hang off screen)
            self.bg = pygame.transform.smoothscale(pause_bg_raw, (1050, 1100))
        except pygame.error:
            self.bg = None

        # --- LOAD UI ICONS (Forced to 55x55 to fit the Inventory boxes) ---
        try:
            self.icon_pink = pygame.transform.smoothscale(pygame.image.load("mats/ui/icon_pink.png").convert_alpha(),
                                                          (55, 55))
            self.icon_purple = pygame.transform.smoothscale(
                pygame.image.load("mats/ui/icon_purple.png").convert_alpha(), (55, 55))
            self.icon_blue = pygame.transform.smoothscale(pygame.image.load("mats/ui/icon_blue.png").convert_alpha(),
                                                          (55, 55))
            self.icon_rainbow = pygame.transform.smoothscale(
                pygame.image.load("mats/ui/icon_rainbow.png").convert_alpha(), (55, 55))
        except pygame.error:
            self.icon_pink = self.icon_purple = self.icon_blue = self.icon_rainbow = None

        # Pushed the centers further out so they don't overlap in the middle
        self.left_cx = self.w // 2 - 350
        self.right_cx = self.w // 2 + 350

        # Build a 3x3 Inventory Grid mathematically centered in the Left Mirror
        self.grid_rects = []
        start_x = self.left_cx - 115
        start_y = self.h // 2 + 40
        for row in range(3):
            for col in range(3):
                self.grid_rects.append(pygame.Rect(start_x + col * 90, start_y + row * 90, 70, 70))

        # Pop-up Menu Logic
        self.selected_spell = None
        self.popup_active = False
        self.popup_rect_left = pygame.Rect(0, 0, 120, 35)
        self.popup_rect_right = pygame.Rect(0, 0, 120, 35)

    def update(self, mouse_pos, mouse_click, owned_spells):
        result = None
        if mouse_click:
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
                        break
        return result

    def draw(self, screen, owned_spells, mouse_pos):
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        if self.bg:
            # Shifted Y down slightly so the mirror centers perfectly vertically
            left_rect = self.bg.get_rect(center=(self.left_cx, self.h // 2 + 50))
            screen.blit(self.bg, left_rect)

            right_rect = self.bg.get_rect(center=(self.right_cx, self.h // 2 + 50))
            screen.blit(self.bg, right_rect)

        center_x = self.w // 2

        # --- GLOBAL HEADERS (Top Center) ---
        draw_text(screen, "GAME PAUSED", self.font_big, pygame.Color("turquoise1"), center_x - 165, 40)
        draw_text(screen, "Press 'P' or 'ESC' to Resume", self.font_small, PINK, center_x - 135, 95)

        # --- LEFT TOMBSTONE: INVENTORY ---
        draw_text(screen, "INVENTORY", self.font_med, PINK, self.left_cx - 75, self.h // 2 - 10)

        for i, rect in enumerate(self.grid_rects):
            pygame.draw.rect(screen, LIGHT_GRAY, rect, 2, border_radius=5)

            if i < len(owned_spells):
                spell = owned_spells[i]

                # BLIT THE REAL ICONS INSTEAD OF DRAWING CIRCLES
                if spell == "normal" and self.icon_pink:
                    screen.blit(self.icon_pink, self.icon_pink.get_rect(center=rect.center))
                elif spell == "purple" and self.icon_purple:
                    screen.blit(self.icon_purple, self.icon_purple.get_rect(center=rect.center))
                elif spell == "blue" and self.icon_blue:
                    screen.blit(self.icon_blue, self.icon_blue.get_rect(center=rect.center))
                elif spell == "rainbow" and self.icon_rainbow:
                    screen.blit(self.icon_rainbow, self.icon_rainbow.get_rect(center=rect.center))

                if rect.collidepoint(mouse_pos) and not self.popup_active:
                    pygame.draw.rect(screen, WHITE, rect, 3, border_radius=5)

        # --- RIGHT TOMBSTONE: CONTROLS ---
        draw_text(screen, "CONTROLS", self.font_med, PINK, self.right_cx - 70, self.h // 2 - 10)

        ctrl_y = self.h // 2 + 40
        ctrl_x = self.right_cx - 130

        draw_text(screen, "WASD / Arrows : Move & Duck", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y)
        draw_text(screen, "Shift      : Run", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y + 30)
        draw_text(screen, "Space      : Jump", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y + 60)
        draw_text(screen, "Left Click : Use Left Spell", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y + 90)
        draw_text(screen, "Right Click: Use Right Spell", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y + 120)
        draw_text(screen, "3 / MMB    : Melee Kick", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y + 150)
        draw_text(screen, "E Key      : Enter/Exit", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y + 180)
        draw_text(screen, "P / ESC    : Pause", self.font_small, pygame.Color("blue1"), ctrl_x, ctrl_y + 210)

        # --- POP-UP EQUIP MENU ---
        if self.popup_active:
            pygame.draw.rect(screen, BLACK, self.popup_rect_left)
            col_l = PINK if self.popup_rect_left.collidepoint(mouse_pos) else WHITE
            pygame.draw.rect(screen, col_l, self.popup_rect_left, 2)
            draw_text(screen, "Equip Left", self.font_small, col_l, self.popup_rect_left.x + 10,
                      self.popup_rect_left.y + 8)

            pygame.draw.rect(screen, BLACK, self.popup_rect_right)
            col_r = PINK if self.popup_rect_right.collidepoint(mouse_pos) else WHITE
            pygame.draw.rect(screen, col_r, self.popup_rect_right, 2)
            draw_text(screen, "Equip Right", self.font_small, col_r, self.popup_rect_right.x + 5,
                      self.popup_rect_right.y + 8)


class DeathScreen:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.font_big = pygame.font.SysFont("Lucida Sans", 48)
        self.font_small = pygame.font.SysFont("Lucida Sans", 20)
        try:
            self.bg = pygame.transform.smoothscale(pygame.image.load("mats/ui/death_screen.png").convert_alpha(),
                                                   (w, h))
            death_overlay_raw = pygame.image.load("mats/ui/death overlay.png").convert_alpha()
            self.overlay = pygame.transform.smoothscale(death_overlay_raw, (1100, 1150))
        except pygame.error:
            self.bg = pygame.Surface((w, h))
            self.overlay = None

    def draw_centered_scaled_text(self, screen, text, font, color, center_x, y_pos, scale):
        raw_text = font.render(text, True, color)
        scaled_w = int(raw_text.get_width() * scale)
        scaled_h = int(raw_text.get_height() * scale)
        scaled_text = pygame.transform.smoothscale(raw_text, (scaled_w, scaled_h))
        text_rect = scaled_text.get_rect(center=(center_x + 20, y_pos))
        screen.blit(scaled_text, text_rect)

    def draw(self, screen, current_state, checkpoint):
        screen.blit(self.bg, (0, 0))
        if self.overlay:
            do_rect = self.overlay.get_rect(center=(self.w // 2, self.h // 2 + 50))
            screen.blit(self.overlay, do_rect)

        center_x = self.w // 2
        start_y = self.h // 2 - 35
        line_w = 155
        line_left = center_x - line_w
        line_right = center_x + line_w + 40
        line_color = pygame.Color("plum1")
        line_thickness = 6

        pygame.draw.line(screen, line_color, (line_left, start_y - 45), (line_right, start_y - 45), line_thickness)
        self.draw_centered_scaled_text(screen, "YOUR SOUL HAS BEEN LOST!!", self.font_big, pygame.Color("turquoise1"),
                                       center_x, start_y, 0.50)

        pygame.draw.line(screen, line_color, (line_left, start_y + 45), (line_right, start_y + 45), line_thickness)
        self.draw_centered_scaled_text(screen, f"DIED ON: {current_state.replace('_', ' ')}", self.font_big,
                                       pygame.Color("turquoise1"), center_x, start_y + 95, 0.45)

        pygame.draw.line(screen, line_color, (line_left, start_y + 145), (line_right, start_y + 145), line_thickness)

        if checkpoint in [2, 3, 4]:
            self.draw_centered_scaled_text(screen, f"PRESS SPACE TO RETRY LEVEL {checkpoint}", self.font_small,
                                           pygame.Color("turquoise1"), center_x, start_y + 185, 1.0)
            self.draw_centered_scaled_text(screen, "PRESS '1' TO RESTART AT LEVEL 1", self.font_small, LIGHT_GRAY,
                                           center_x, start_y + 215, 0.8)
        else:
            self.draw_centered_scaled_text(screen, "PRESS SPACE TO TRY AGAIN", self.font_small,
                                           pygame.Color("turquoise1"), center_x, start_y + 200, 1.2)

        pygame.draw.line(screen, line_color, (line_left, start_y + 255), (line_right, start_y + 255), line_thickness)


class MainMenu:
    def __init__(self, w, h):
        try:
            self.bg = pygame.transform.smoothscale(pygame.image.load("mats/ui/start_bg.png").convert(), (w, h))

            raw_play = pygame.image.load("mats/ui/play.png").convert_alpha()
            raw_controls = pygame.image.load("mats/ui/controls.png").convert_alpha()
            raw_load = pygame.image.load("mats/ui/load.png").convert_alpha()

            self.play_b = pygame.transform.smoothscale(raw_play, (260, 140))
            self.ctrl_b = pygame.transform.smoothscale(raw_controls, (260, 140))
            self.load_b = pygame.transform.smoothscale(raw_load, (190, 190))

            self.play_h = pygame.transform.smoothscale(raw_play, (286, 154))
            self.ctrl_h = pygame.transform.smoothscale(raw_controls, (286, 154))
            self.load_h = pygame.transform.smoothscale(raw_load, (209, 209))

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
                self.sub_menu = None
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
            text = self.font_title.render("Save Slots (JSON Logic Coming Soon!)", True, PINK)
            screen.blit(text, text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50)))
            sub = self.font_text.render("Click anywhere to return", True, LIGHT_GRAY)
            screen.blit(sub, sub.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 20)))

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

            # --- NEW: LOAD EXIT HUD ---
            try:
                # Note: Make sure the file is a .png so the background is transparent!
                self.exit_hud_img = pygame.transform.smoothscale(
                    pygame.image.load("mats/ui/exit_hud.png").convert_alpha(), (330, 100))
            except pygame.error as e:
                print(f"Error loading exit HUD: {e}")
                self.exit_hud_img = None

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
             "cost": 50, "color": (220, 220, 220)},
            {"id": "Wings Potion", "img": self.wings_p, "title": "Wings Potion",
             "desc": ["Unlocks the ability to Fly."], "cost": 200, "color": (255, 200, 50)},
            {"id": "Purple Potion", "img": self.purple_p, "title": "Purple Potion",
             "desc": ["Unlocks Purple Fireball."], "cost": 50, "color": (180, 50, 255)},
            {"id": "Blue Potion", "img": self.mana_p, "title": "Blue Potion", "desc": ["Magic mysteries await..."],
             "cost": 50, "color": (50, 50, 255)},
            {"id": "Rainbow Potion", "img": self.rainbow_p, "title": "Rainbow Potion",
             "desc": ["Unlocks ultimate secrets."], "cost": 50, "color": (255, 100, 255)},
            {"id": "Royal Potion", "img": self.royal_p, "title": "Royal Potion", "desc": ["Summons a loyal companion."],
             "cost": 50, "color": (255, 180, 50)},
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
            text_x = 270
            screen.blit(
                self.font_title.render(self.selected_item_data["title"], True, self.selected_item_data["color"]),
                (text_x, 155))

            y_offset = 205
            for line in self.selected_item_data["desc"]:
                screen.blit(self.font_desc.render(line, True, (190, 200, 200)), (text_x, y_offset))
                y_offset += 25

            screen.blit(self.font_title.render(f"COST: {self.selected_item_data['cost']} REM", True, PINK),
                        (text_x, y_offset + 10))

        # --- DRAW THE NEW EXIT HUD ---
        if self.exit_hud_img:
            # TUNE THESE: 950 puts it right between Percy's sign and the Spell HUD. 25 matches the top of the Spell HUD.
            screen.blit(self.exit_hud_img, (940, 25))