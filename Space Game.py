import pygame
import sys
from random import shuffle
from pygame.locals import *

red = (255, 0, 0)
green = (0, 255, 0)
yellow = (255, 255, 0)
orange = (255, 128, 0)
purple = (82, 6, 36)

playerwidth = 30
playerheight = 10
player1 = 'Player 1'
playerspeed = 5
playercolor = yellow

gametitle = 'Space'
displaywidth = 635
displayheight = 480
bgcolor = purple
xmargin = 50
ymargin = 50

bulletwidth = 8
bulletheight = 6
bulletoffset = 600

enemywidth = 26
enemyheight = 26
enemyname = 'enemi'
enemygap = 23
arraywidth = 10
arrayheigt = 4
movetime = 900
movex = 10
movey = enemyheight
timeoffset = 300

dire = {pygame.K_LEFT: (-1),
        pygame.K_RIGHT: (1)}


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.width = playerwidth
        self.height = playerheight
        self.image = pygame.Surface((self.width, self.height))
        self.color = playercolor
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.name = player1
        self.speed = playerspeed
        self.vectorx = 0

    def update(self, keys, *args):
        for key in dire:
            if keys[key]:
                self.rect.x += dire[key] * self.speed
        self.check_for_side()
        self.image.fill(self.color)

    def check_for_side(self):
        if self.rect.right > displaywidth:
            self.rect.right = displaywidth
            self.vectorx = 0
        elif self.rect.left < 0:
            self.rect.left = 0
            self.vectorx = 0


class Blocker(pygame.sprite.Sprite):
    def __init__(self, side, color, row, column):
        pygame.sprite.Sprite.__init__(self)
        self.width = side
        self.height = side
        self.color = color
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.name = 'blocker'
        self.row = row
        self.column = column


class Bullet(pygame.sprite.Sprite):
    def __init__(self, rect, color, vectory, speed):
        pygame.sprite.Sprite.__init__(self)
        self.width = bulletwidth
        self.height = bulletheight
        self.color = color
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.centerx = rect.centerx
        self.rect.top = rect.bottom
        self.name = 'bullet'
        self.vectory = vectory
        self.speed = speed

    def update(self, *args):
        self.oldLocation = (self.rect.x, self.rect.y)
        self.rect.y += self.vectory * self.speed
        if self.rect.bottom < 0:
            self.kill()
        elif self.rect.bottom > 500:
            self.kill()


class Enemy(pygame.sprite.Sprite):

    def __init__(self, row, column):
        pygame.sprite.Sprite.__init__(self)
        self.width = enemywidth
        self.height = enemyheight
        self.row = row
        self.column = column
        self.image = self.set_image()
        self.rect = self.image.get_rect()
        self.name = 'enemi'
        self.vectorx = 1
        self.moveNumber = 0
        self.moveTime = movetime
        self.timeOffset = row * timeoffset
        self.timer = pygame.time.get_ticks() - self.timeOffset

    def update(self, keys, currentTime):
        if currentTime - self.timer > self.moveTime:
            if self.moveNumber < 6:
                self.rect.x += movex * self.vectorx
                self.moveNumber += 1
            elif self.moveNumber >= 6:
                self.vectorx *= -1
                self.moveNumber = 0
                self.rect.y += movey
                if self.moveTime > 100:
                    self.moveTime -= 50
            self.timer = currentTime

    def set_image(self):
        if self.row == 0:
            image = pygame.image.load('A.png')
        elif self.row == 1:
            image = pygame.image.load('A.png')
        elif self.row == 2:
            image = pygame.image.load('A.png')
        else:
            image = pygame.image.load('A.png')
        image.convert_alpha()
        image = pygame.transform.scale(image, (self.width, self.height))
        return image


class Text(object):
    def __init__(self, font, size, message, color, rect, surface):
        self.font = pygame.font.Font(font, size)
        self.message = message
        self.surface = self.font.render(self.message, True, color)
        self.rect = self.surface.get_rect()
        self.setRect(rect)

    def setRect(self, rect):
        self.rect.centerx, self.rect.centery = rect.centerx, rect.centery - 5

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class App(object):

    def __init__(self):
        pygame.init()
        self.displaySurf, self.displayRect = self.make_screen()
        self.gameStart = True
        self.gameOver = False
        self.beginGame = False

    def reset_game(self):
        self.gameStart = True
        self.needToMakeEnemies = True
        self.introMessage1 = Text('tipografia.ttf', 50, 'Bienvenido al Spacio', orange, self.displayRect, self.displaySurf)
        self.introMessage2 = Text('tipografia.ttf', 30, 'Presione para continuar', orange, self.displayRect,
                                  self.displaySurf)
        self.introMessage2.rect.top = self.introMessage1.rect.bottom + 5
        self.gameOverMessage = Text('tipografia.ttf', 80, 'Game Over', orange, self.displayRect, self.displaySurf)
        self.player = self.make_player()
        self.bullets = pygame.sprite.Group()
        self.greenBullets = pygame.sprite.Group()
        self.blockerGroup1 = self.make_blockers(0)
        self.blockerGroup2 = self.make_blockers(1)
        self.blockerGroup3 = self.make_blockers(2)
        self.blockerGroup4 = self.make_blockers(3)
        self.allBlockers = pygame.sprite.Group(self.blockerGroup1, self.blockerGroup2, self.blockerGroup3,
                                               self.blockerGroup4)
        self.allSprites = pygame.sprite.Group(self.player, self.allBlockers)
        self.keys = pygame.key.get_pressed()
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.enemyMoves = 0
        self.enemyBulletTimer = pygame.time.get_ticks()
        self.gameOver = False
        self.gameOverTime = pygame.time.get_ticks()

    def make_blockers(self, number=1):
        blockerGroup = pygame.sprite.Group()
        for row in range(5):
            for column in range(7):
                blocker = Blocker(8, yellow, row, column)
                blocker.rect.x = 70 + (220 * number) + (column * blocker.width)
                blocker.rect.y = 375 + (row * blocker.height)
                blockerGroup.add(blocker)
        for blocker in blockerGroup:
            if (blocker.column == 0 and blocker.row == 0 or blocker.column == 6 and blocker.row == 0):
                blocker.kill()
        return blockerGroup

    def check_for_enemy_bullets(self):
        redBulletsGroup = pygame.sprite.Group()
        for bullet in self.bullets:
            if bullet.color == green:
                redBulletsGroup.add(bullet)
        for bullet in redBulletsGroup:
            if pygame.sprite.collide_rect(bullet, self.player):
                if self.player.color == yellow:
                    self.player.color = orange
                elif self.player.color == orange:
                    self.player.color = red
                elif self.player.color == red:
                    self.gameOver = True
                    self.gameOverTime = pygame.time.get_ticks()
                bullet.kill()

    def shoot_enemy_bullet(self, rect):
        if (pygame.time.get_ticks() - self.enemyBulletTimer) > bulletoffset:
            self.bullets.add(Bullet(rect, green, 1, 5))
            self.allSprites.add(self.bullets)
            self.enemyBulletTimer = pygame.time.get_ticks()

    def find_enemy_shooter(self):
        columnList = []
        for enemy in self.enemies:
            columnList.append(enemy.column)
        columnSet = set(columnList)
        columnList = list(columnSet)
        shuffle(columnList)
        column = columnList[0]
        enemyList = []
        rowList = []
        for enemy in self.enemies:
            if enemy.column == column:
                rowList.append(enemy.row)
        row = max(rowList)
        for enemy in self.enemies:
            if enemy.column == column and enemy.row == row:
                self.shooter = enemy

    def make_screen(self):
        pygame.display.set_caption(gametitle)
        displaySurf = pygame.display.set_mode((displaywidth, displayheight))
        displayRect = displaySurf.get_rect()
        displaySurf.fill(bgcolor)
        displaySurf.convert()
        return displaySurf, displayRect

    def make_player(self):
        player = Player()
        player.rect.centerx = self.displayRect.centerx
        player.rect.bottom = self.displayRect.bottom - 5
        return player

    def make_enemies(self):
        enemies = pygame.sprite.Group()
        for row in range(arrayheigt):
            for column in range(arraywidth):
                enemy = Enemy(row, column)
                enemy.rect.x = xmargin + (column * (enemywidth + enemygap))
                enemy.rect.y = ymargin + (row * (enemyheight + enemygap))
                enemies.add(enemy)
        return enemies

    def check_input(self):
        for event in pygame.event.get():
            self.keys = pygame.key.get_pressed()
            if event.type == QUIT:
                self.terminate()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE and len(self.greenBullets) < 1:
                    bullet = Bullet(self.player.rect, red, -1, 20)
                    self.greenBullets.add(bullet)
                    self.bullets.add(self.greenBullets)
                    self.allSprites.add(self.bullets)
                elif event.key == K_ESCAPE:
                    self.terminate()

    def game_start_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.terminate()
            elif event.type == KEYUP:
                self.gameOver = False
                self.gameStart = False
                self.beginGame = True

    def game_over_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.terminate()
            elif event.type == KEYUP:
                self.gameStart = True
                self.beginGame = False
                self.gameOver = False

    def check_collisions(self):
        self.check_for_enemy_bullets()
        pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
        pygame.sprite.groupcollide(self.enemies, self.allBlockers, False, True)
        self.collide_green_blockers()
        self.collide_red_blockers()

    def collide_green_blockers(self):
        for bullet in self.greenBullets:
            casting = Bullet(self.player.rect, green, -1, 20)
            casting.rect = bullet.rect.copy()
            for pixel in range(bullet.speed):
                hit = pygame.sprite.spritecollideany(casting, self.allBlockers)
                if hit:
                    hit.kill()
                    bullet.kill()
                    break
                casting.rect.y -= 1

    def collide_red_blockers(self):
        reds = (shot for shot in self.bullets if shot.color == green)
        red_bullets = pygame.sprite.Group(reds)
        pygame.sprite.groupcollide(red_bullets, self.allBlockers, True, True)

    def check_game_over(self):
        if len(self.enemies) == 0:
            self.gameOver = True
            self.gameStart = False
            self.beginGame = False
            self.gameOverTime = pygame.time.get_ticks()
        else:
            for enemy in self.enemies:
                if enemy.rect.bottom > displayheight:
                    self.gameOver = True
                    self.gameStart = False
                    self.beginGame = False
                    self.gameOverTime = pygame.time.get_ticks()

    def terminate(self):
        pygame.quit()
        sys.exit()

    def main_loop(self):
        while True:
            if self.gameStart:
                self.reset_game()
                self.gameOver = False
                self.displaySurf.fill(bgcolor)
                self.introMessage1.draw(self.displaySurf)
                self.introMessage2.draw(self.displaySurf)
                self.game_start_input()
                pygame.display.update()
            elif self.gameOver:
                self.displaySurf.fill(bgcolor)
                self.gameOverMessage.draw(self.displaySurf)
                if (pygame.time.get_ticks() - self.gameOverTime) > 2000:
                    self.game_over_input()
                pygame.display.update()
            elif self.beginGame:
                if self.needToMakeEnemies:
                    self.enemies = self.make_enemies()
                    self.allSprites.add(self.enemies)
                    self.needToMakeEnemies = False
                    pygame.event.clear()
                else:
                    currentTime = pygame.time.get_ticks()
                    self.displaySurf.fill(bgcolor)
                    self.check_input()
                    self.allSprites.update(self.keys, currentTime)
                    if len(self.enemies) > 0:
                        self.find_enemy_shooter()
                        self.shoot_enemy_bullet(self.shooter.rect)
                    self.check_collisions()
                    self.allSprites.draw(self.displaySurf)
                    self.blockerGroup1.draw(self.displaySurf)
                    pygame.display.update()
                    self.check_game_over()
                    self.clock.tick(self.fps)

if __name__ == '__main__':
    app = App()
    app.main_loop()