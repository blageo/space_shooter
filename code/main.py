import pygame
from os.path import join
from random import randint, uniform


# classes
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(
            join("..", "images", "player.png")
        ).convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 300

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction = (
            self.direction.normalize() if self.direction else self.direction
        )
        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()

        self.laser_timer()


class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(
            center=(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT))
        )


class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos)

    def update(self, dt):
        self.rect.centery -= 400 * dt

        if self.rect.bottom < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = 200

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt

        if self.rect.top > WINDOW_HEIGHT:
            self.kill()
            return


def collisions():
    global running

    # check collision
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True)
    if collision_sprites:
        running = False

    for l_sprite in laser_sprites:
        collided_meteors = pygame.sprite.spritecollide(l_sprite, meteor_sprites, True)
        if collided_meteors:
            l_sprite.kill()


# general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
running = True
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# import
meteor_surf = pygame.image.load(join("..", "images", "meteor.png")).convert_alpha()
laser_surf = pygame.image.load(join("..", "images", "laser.png")).convert_alpha()
laser_rect = laser_surf.get_frect(bottomleft=(20, WINDOW_HEIGHT - 20))
font = pygame.font.Font(None, 20)
text_surface = font.render("Rendered text", True, "red")

# sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

star_surf = pygame.image.load(join("..", "images", "star.png")).convert_alpha()
for i in range(20):
    Star(all_sprites, star_surf)
player = Player(all_sprites)

# custom events -> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

# main game loop
while running:
    dt = clock.tick() / 1000
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(
                meteor_surf,
                (x, y),
                (all_sprites, meteor_sprites),
            )

    # update
    all_sprites.update(dt)
    collisions()

    # draw game
    display_surface.fill("black")
    all_sprites.draw(display_surface)
    display_surface.blit(text_surface, ((WINDOW_WIDTH / 2), 0))
    pygame.display.update()

pygame.quit()
