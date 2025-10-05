import settings
from settings import *
from sprites import *

class Game:
    def __init__(self):
        # initialization and window
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.init()
        self.running = True
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Shadow Drift')
        icon = pygame.image.load(join('images', 'icon.png')).convert_alpha()
        pygame.display.set_icon(icon)

        # font
        self.font1 = pygame.font.Font(None, 50)
        self.font2 = pygame.font.SysFont('Times New Roman', 200)

        # background animation setup
        self.bg_index = 0
        self.bg_timer = 0
        self.bg_interval = 100
        for key, frames in BACKGROUNDS.items():
            BACKGROUNDS[key] = [frame.convert_alpha() for frame in frames]


        # sounds
        pygame.mixer.music.load(join('audio', '8-Bit-Indigestion.ogg'))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        self.damage_sound = pygame.mixer.Sound(join('audio', 'damage.ogg'))
        self.death_sound = pygame.mixer.Sound(join('audio', 'death-sound.ogg'))
        self.record_sound = pygame.mixer.Sound(join('audio', 'new_record_sound.ogg'))
        self.ability_sound = pygame.mixer.Sound(join('audio', 'ability.ogg'))
        
        # sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.player = Player(self.all_sprites, self.ability_sound)

        # load record
        try:
            with open(join('data', 'record.txt')) as f:
                STATS['record'] = json.load(f)
        except FileNotFoundError:
            pass

        # costom events
        self.obstacle_event = pygame.event.custom_type()
        pygame.time.set_timer(self.obstacle_event, 500)

    def save_record(self):
        if STATS['score'] > STATS['record']:
            STATS['record'] = STATS['score']
        with open(join('data', 'record.txt'), 'w') as f:
            json.dump(STATS['record'], f)

    def collision(self):
        return pygame.sprite.spritecollide(self.player, self.obstacle_sprites, True, pygame.sprite.collide_mask)

    def run(self):
        # game loop
        while self.running:
            dt = self.clock.tick(60) / 1000
            settings.update_time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False 
                elif event.type == self.obstacle_event:
                    if settings.game_time < 20000:
                        Obstacle((self.all_sprites, self.obstacle_sprites), 250, self.record_sound)
                    elif 20000 <= settings.game_time < 40:
                        Obstacle((self.all_sprites, self.obstacle_sprites), 350, self.record_sound)
                    else:
                        Obstacle((self.all_sprites, self.obstacle_sprites), 450, self.record_sound)

            self.all_sprites.update(dt)

            if self.collision() and self.player.can_collide:
                STATS['health'] -= 1
                if STATS['health'] >= 1:
                    pygame.draw.circle(self.player.glow, (255,0,0,100), (40,40), 40, width=5)
                    self.player.speed += 100
                    self.damage_sound.play()
                else:
                    self.death_sound.play()
                    self.player.kill()
                    self.running = False

            # background after time
            self.bg_timer += dt * 1000
            if self.bg_timer >= self.bg_interval:
                self.bg_timer = 0
                self.bg_index = (self.bg_index + 1) % len(BACKGROUNDS['bg1'])
            if settings.game_time < 20000:
                bg_frames = BACKGROUNDS['bg1']
            elif 20000 <= settings.game_time < 40:
                bg_frames = BACKGROUNDS['bg2']
            else:
                bg_frames = BACKGROUNDS['bg3']

            # draw
            self.screen.blit(bg_frames[self.bg_index % len(bg_frames)], (0, 0))
            self.all_sprites.draw(self.screen)
            
            # draw text
            stats_text = self.font1.render(f"Lives: {STATS['health']}\nScore: {STATS['score']}\nRecord: {STATS['record']}", True, "black")
            self.screen.blit(stats_text, (20,20))

            # ability ready
            if STATS['ability'] and STATS['health']:
                self.screen.blit(self.player.glow, self.player.rect.move(-5,-5))

            pygame.display.update()

        # closing sequence
        self.save_record()

        # game-over screen
        pygame.mixer.music.fadeout(3000)
        for i in range(1,11):
            pygame.draw.rect(game.screen,'black',((0,0),(130 * i,WINDOW_HEIGHT)))
            pygame.display.update()
            sleep(0.25)
        game_over_message = game.font2.render("Game Over!", True, "red")
        game_over_rect = game_over_message.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        game.screen.blit(game_over_message, game_over_rect)
        pygame.display.update()
        sleep(3)

        # close
        pygame.quit()
        exit()

if __name__ == '__main__':
    game = Game()
    game.run()