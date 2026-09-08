#-entities-#

import pygame
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

class Projectile(pygame.sprite.Sprite):
    # --- ADDED exp_offset=0 HERE ---
    def __init__(self, x, y, direction, fireball_img, explode_img, fly_scale=0.45, exp_scale=0.45, exp_offset=0, damage=1):
        super().__init__()
        self.direction, self.speed, self.state = direction, 800.0, "fly"
        self.frame_index, self.update_time = 0, pygame.time.get_ticks()

        # Save the offset and damage to use later
        self.exp_offset = exp_offset
        self.damage = damage

        fw, fh = fireball_img.get_width() // 6, fireball_img.get_height()
        self.fly_frames = [pygame.transform.flip(
            pygame.transform.smoothscale(fireball_img.subsurface((i * fw, 0, fw, fh)),
                                         (int(fw * fly_scale), int(fh * fly_scale))), direction == -1, False) for i in
            range(6)]

        ew, eh = explode_img.get_width() // 8, explode_img.get_height()
        self.exp_frames = [pygame.transform.flip(
            pygame.transform.smoothscale(explode_img.subsurface((i * ew, 0, ew, eh)),
                                         (int(ew * exp_scale), int(eh * exp_scale))),
            direction == -1, False) for i in range(8)]

        self.image = self.fly_frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt, camera_x, screen_width):
        if pygame.time.get_ticks() - self.update_time > (50 if self.state == "fly" else 40):
            self.update_time, self.frame_index = pygame.time.get_ticks(), self.frame_index + 1

            old_center = self.rect.center

            if self.state == "fly":
                self.frame_index %= len(self.fly_frames)
                self.image = self.fly_frames[self.frame_index]
            else:
                if self.frame_index >= len(self.exp_frames):
                    self.kill()
                    return
                self.image = self.exp_frames[self.frame_index]

            self.rect = self.image.get_rect(center=old_center)

        if self.state == "fly":
            self.rect.x += self.direction * self.speed * dt
            if getattr(self, "last_image", None) != self.image:
                self.mask = pygame.mask.from_surface(self.image)
                self.last_image = self.image

            if self.rect.right < camera_x - 500 or self.rect.left > camera_x + screen_width + 500:
                self.kill()

    def explode(self):
        if self.state != "explode":
            self.state, self.frame_index, self.update_time = "explode", 0, pygame.time.get_ticks()

            # --- USE THE CUSTOM OFFSET HERE ---
            self.rect.x += self.direction * self.exp_offset


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
    def __init__(self, screen_width, screen_height, sheet_filename, columns=7, rows=4, target_duration=9600):
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


class Companion(pygame.sprite.Sprite):
    def __init__(self, frames, anim_speed=70):
        super().__init__()
        self.frames = frames
        self.anim_speed = anim_speed
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()

        # Set initial image and rect
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()

    def update(self, target_x, target_y, target_facing_right):
        # 1. Handle Animation
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.anim_speed:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.last_update = current_time

        self.image = self.frames[self.frame_index]

        # 2. Handle Direction Flipping
        if not target_facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        # 3. Handle Following Position
        # target_y is now anchored to Succi's feet, so we use a larger negative number to push Tinera UP to shoulder height.
        offset_x = -90 if target_facing_right else 90
        offset_y = -265

        self.rect.centerx = target_x + offset_x
        self.rect.centery = target_y + offset_y

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)