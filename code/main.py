from settings import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Rectangle Evasion')
        self.clock = pygame.time.Clock()
        self.game_time = 0
        self.running = True

        # sounds
        self.game_music = pygame.mixer.Sound(join('audio', '8-Bit-Indigestion.mp3'))
        self.game_music.set_volume(0.5)
        self.game_music.play(loops=-1)
        self.damage_sound = pygame.mixer.Sound(join('audio', 'damage.wav'))
        self.death_sound = pygame.mixer.Sound(join('audio', 'death-sound.mp3'))
        self.record_sound = pygame.mixer.Sound(join('audio', 'new_record_sound.wav'))
        self.ability_sound = pygame.mixer.Sound(join('audio', 'ability.wav'))

# player
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        self.images = {
            (1, 'right'): pygame.image.load(join('images', 'player1-right.png')).convert_alpha(),
            (1, 'left'):  pygame.image.load(join('images', 'player1-left.png')).convert_alpha(),
            (2, 'right'): pygame.image.load(join('images', 'player2-right.png')).convert_alpha(),
            (2, 'left'):  pygame.image.load(join('images', 'player2-left.png')).convert_alpha(),
        }
        super().__init__(groups)
        self.image = pygame.image.load(join('images','player2-right.png')).convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2()
        self.facing = 'right'
        self.speed = 250
        self.can_collide = True
        self.cooldown = 10
        self.activation_time = -10
        self.glow = pygame.Surface((80,80), pygame.SRCALPHA)
        pygame.draw.circle(self.glow, (0,100,255,100), (40,40), 40, width=5)

    def update_sprite(self):
        key = (stats['health'], self.facing)
        self.image = self.images[key]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.size = self.image.get_size()

    def activate_ability(self):
        ability_sound.play()
        self.activation_time = pygame.time.get_ticks() // 1000
        stats['ability'] = False
        self.can_collide = False

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += dt * self.speed * self.direction

        recent_keys = pygame.key.get_just_pressed()
        if self.game_time - self.activation_time >= self.cooldown:
            stats['ability'] = True
            if recent_keys[pygame.K_SPACE]:
                self.activate_ability()
        if self.game_time - self.activation_time >= 1:
            self.can_collide = True

        # blur while invincible
        self.image.set_alpha(100) if not self.can_collide else self.image.set_alpha(255)
            

        # adjust sprite when facing a side
        if keys[pygame.K_RIGHT]:
            self.facing = 'right'
        elif keys[pygame.K_LEFT]:
            self.facing = 'left'

        self.update_sprite()

        # keep inside window
        self.rect.clamp_ip(pygame.Rect(-10, -10, WINDOW_WIDTH+20, WINDOW_HEIGHT+20))


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, groups, speed):
        super().__init__(groups)
        self.width = choice((150, 200, 250, 300))
        filename = f"obstacle_{self.width}.png"
        self.image = pygame.image.load(join('images', filename)).convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH + self.width, randint(0, WINDOW_HEIGHT)))
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = pygame.Vector2(-1,0)
        self.speed = speed

    def update(self, dt):
        global stats
        self.rect.centerx -= self.speed * dt
        if self.rect.right < 0:
            stats['score'] += 1
            if stats['score'] == stats['record'] + 1:
                record_sound.play()
            self.kill()

def collisions():
    if pygame.sprite.spritecollide(player, obstacle_sprites, True, pygame.sprite.collide_mask):    
        return True
    return False

# sprite groups
all_sprites = pygame.sprite.Group()
obstacle_sprites = pygame.sprite.Group()
player = Player(all_sprites)

# load record
try:
    with open(join('data', 'score.txt')) as f:
        stats['record'] = json.load(f)
except FileNotFoundError:
    pass

# costom events
obstacle_event = pygame.event.custom_type()
pygame.time.set_timer(obstacle_event, 500)
    
# game loop
while self.running:
    dt = self.clock.tick(60) / 1000
    self.game_time = pygame.time.get_ticks() // 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            self.running = False 
        elif event.type == obstacle_event:
            if self.game_time < 20:
                Obstacle(groups=(all_sprites, obstacle_sprites), speed=250)
            elif 20 <= self.game_time < 40:
                Obstacle(groups=(all_sprites, obstacle_sprites), speed=350)
            else:
                Obstacle(groups=(all_sprites, obstacle_sprites), speed=450)

    all_sprites.update(dt)

    if collisions() and player.can_collide:
        stats['health'] -= 1
        if stats['health'] >= 1:
            pygame.draw.circle(player.glow, (255,0,0,100), (40,40), 40, width=5)
            player.speed += 100
            damage_sound.play()
        else:
            death_sound.play()
            player.kill()
            self.running = False

    # background color after time
    if self.game_time < 20:
        self.screen.fill('white')
    elif 20 <= self.game_time < 40:
        self.screen.fill('cyan')
    else:
        self.screen.fill('green')

    # draw
    all_sprites.draw(self.screen)
    
    stats_text = font1.render(f"Lives: {stats['health']}\nScore: {stats['score']}\nRecord: {stats['record']}", True, "black")
    self.screen.blit(stats_text, (20,20))

    # ability ready
    if stats['ability']:
        self.screen.blit(player.glow, player.rect.move(-5,-5))

    pygame.display.update()

# save
if stats['score'] > stats['record']:
    stats['record'] = stats['score']
with open(join('data', 'score.txt'), 'w') as f:
    json.dump(stats['record'], f)

# Game-over screen
game_music.fadeout(3000)
for i in range(1,11):
    pygame.draw.rect(self.screen,'black',((0,0),(130 * i,WINDOW_HEIGHT)))
    pygame.display.update()
    sleep(0.25)
game_over_message = font2.render("Game Over!", True, "red")
game_over_rect = game_over_message.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
self.screen.blit(game_over_message, game_over_rect)
pygame.display.update()
sleep(3)

# close
print(stats['score'])
pygame.quit()
exit()

if __name__ == '__main__':
    game = Game()
    game.run()