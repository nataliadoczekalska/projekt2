import math
import random
from psychopy import visual, event, core
import multiprocessing as mp
import pygame as pg
import pandas as pd
import filterlib as flt
import blink as blk
from pyOpenBCI import OpenBCIGanglion

import pygame
from pygame import mixer


pygame.init()

def blinks_detector(quit_program, blink_det, blinks_num, blink,):
    def detect_blinks(sample):
        if SYMULACJA_SYGNALU:
            smp_flted = sample
        else:
            smp = sample.channels_data[0]
            smp_flted = frt.filterIIR(smp, 0)


        brt.blink_detect(smp_flted, -38000)
        if brt.new_blink:
            if brt.blinks_num == 1:

                print('CONNECTED. Speller starts detecting blinks.')
            else:
                blink_det.put(brt.blinks_num)
                blinks_num.value = brt.blinks_num
                blink.value = 1

        if quit_program.is_set():
            if not SYMULACJA_SYGNALU:
                print('Disconnect signal sent...')
                board.stop_stream()

                
    ####ZMIENIĆ NA FALSE I WPISAĆ MAC####
    
    SYMULACJA_SYGNALU = False

    mac_adress = 'f0:a6:74:94:b3:4d'


    clock = pg.time.Clock()
    frt = flt.FltRealTime()
    brt = blk.BlinkRealTime()

    if SYMULACJA_SYGNALU:
        df = pd.read_csv('dane_do_symulacji/data.csv')
        for sample in df['signal']:
            if quit_program.is_set():
                break
            detect_blinks(sample)
            clock.tick(200)
        print('KONIEC SYGNAŁU')
        quit_program.set()
    else:
        board = OpenBCIGanglion(mac=mac_adress)
        board.start_stream(detect_blinks)

if __name__ == "__main__":


    blink_det = mp.Queue()
    blink = mp.Value('i', 0)
    blinks_num = mp.Value('i', 0)

    quit_program = mp.Event()

    proc_blink_det = mp.Process(
        name='proc_',
        target=blinks_detector,
        args=(quit_program, blink_det, blinks_num, blink,)
        )


    proc_blink_det.start()
    print('subprocess started')


    screen = pygame.display.set_mode((800, 600))


    background = pygame.image.load('space.jpeg')


    mixer.music.load("background.wav")
    mixer.music.play(-1)


    pygame.display.set_caption("Space Invader")
    icon = pygame.image.load('ufo.png')
    pygame.display.set_icon(icon)


    playerImg = pygame.image.load('wizard.png')
    playerX = 370
    playerY = 480
    playerX_change = 0


    enemyImg = []
    enemyX = []
    enemyY = []
    enemyX_change = []
    enemyY_change = []
    num_of_enemies = 6

    for i in range(num_of_enemies):
        enemyImg.append(pygame.image.load('monster.png'))
        enemyX.append(random.randint(0, 736))
        enemyY.append(random.randint(50, 150))
        enemyX_change.append(4)
        enemyY_change.append(40)




    bulletImg = pygame.image.load('magic.png')
    bulletX = 0
    bulletY = 480
    bulletX_change = 0
    bulletY_change = 10
    bullet_state = "ready"



    score_value = 0
    font = pygame.font.Font('freesansbold.ttf', 32)

    textX = 10
    testY = 10


    over_font = pygame.font.Font('freesansbold.ttf', 64)


    def show_score(x, y):
        score = font.render("Score : " + str(score_value), True, (255, 255, 255))
        screen.blit(score, (x, y))


    def game_over_text():
        over_text = over_font.render("GAME OVER", True, (255, 255, 255))
        screen.blit(over_text, (200, 250))


    def player(x, y):
        screen.blit(playerImg, (x, y))


    def enemy(x, y, i):
        screen.blit(enemyImg[i], (x, y))


    def fire_bullet(x, y):
        global bullet_state
        bullet_state = "fire"
        screen.blit(bulletImg, (x + 16, y + 10))


    def isCollision(enemyX, enemyY, bulletX, bulletY):
        distance = math.sqrt(math.pow(enemyX - bulletX, 2) + (math.pow(enemyY - bulletY, 2)))
        if distance < 27:
            return True
        else:
            return False



    running = True
    while running:

        #Prędkość gry
        pygame.time.delay(15)
        
        screen.fill((0, 0, 0))

        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    playerX_change = -5
                if event.key == pygame.K_RIGHT:
                    playerX_change = 5
                if event.key == pygame.K_SPACE:
                    if bullet_state is "ready":
                        bulletSound = mixer.Sound("laser.wav")
                        bulletSound.play()
                        bulletX = playerX
                        fire_bullet(bulletX, bulletY)



            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    playerX_change = 0

        if blink.value == 1 :
            if bullet_state is "ready":
                bulletSound = mixer.Sound("laser.wav")
                bulletSound.play()
                bulletX = playerX
                fire_bullet(bulletX, bulletY)
            blink.value=0



        playerX += playerX_change
        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736


        for i in range(num_of_enemies):


            if enemyY[i] > 440:
                for j in range(num_of_enemies):
                    enemyY[j] = 2000
                game_over_text()
                break

            enemyX[i] += enemyX_change[i]
            if enemyX[i] <= 0:
                enemyX_change[i] = 4
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= 736:
                enemyX_change[i] = -4
                enemyY[i] += enemyY_change[i]


            collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
            if collision:
                explosionSound = mixer.Sound("explosion.wav")
                explosionSound.play()
                bulletY = 480
                bullet_state = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, 736)
                enemyY[i] = random.randint(50, 150)

            enemy(enemyX[i], enemyY[i], i)


        if bulletY <= 0:
            bulletY = 480
            bullet_state = "ready"

        if bullet_state is "fire":
            fire_bullet(bulletX, bulletY)
            bulletY -= bulletY_change

        player(playerX, playerY)
        show_score(textX, testY)

        pygame.display.update()

    proc_blink_det.join()
