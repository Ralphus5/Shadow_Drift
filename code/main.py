import settings
from settings import *
from sprites import *

class Game:
    def __init__(self):
        # initialization and window
        pygame.init()
        self.running = True
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Shadow Drift')

        # font
        self.font1 = pygame.font.Font(None, 50)
        self.font2 = pygame.font.SysFont('Times New Roman', 200)

        # sounds
        self.music = pygame.mixer.Sound(join('audio', '8-Bit-Indigestion.mp3'))
        self.music.set_volume(0.5)
        self.music.play(loops=-1)
        self.damage_sound = pygame.mixer.Sound(join('audio', 'damage.wav'))
        self.death_sound = pygame.mixer.Sound(join('audio', 'death-sound.mp3'))
        self.record_sound = pygame.mixer.Sound(join('audio', 'new_record_sound.wav'))
        self.ability_sound = pygame.mixer.Sound(join('audio', 'ability.wav'))
        
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
                    if game_time < 20:
                        Obstacle((self.all_sprites, self.obstacle_sprites), 250, self.record_sound)
                    elif 20 <= game_time < 40:
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

            # background color after time
            if game_time < 20:
                self.screen.fill(COLORS["bg-1"])
            elif 20 <= game_time < 40:
                self.screen.fill(COLORS['bg-2'])
            else:
                self.screen.fill(COLORS['bg-3'])

            # draw
            self.all_sprites.draw(self.screen)
            
            # draw text
            stats_text = self.font1.render(f"Lives: {STATS['health']}\nScore: {STATS['score']}\nRecord: {STATS['record']}", True, "black")
            self.screen.blit(stats_text, (20,20))

            # ability ready
            if STATS['ability'] and STATS['health']:
                self.screen.blit(self.player.glow, self.player.rect.move(-5,-5))

            pygame.display.update()

        # --- CLOSING THE GAME ---
        # save
        if STATS['score'] > STATS['record']:
            STATS['record'] = STATS['score']
        with open(join('data', 'record.txt'), 'w') as f:
            json.dump(STATS['record'], f)

        # game-over screen
        game.music.fadeout(3000)
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