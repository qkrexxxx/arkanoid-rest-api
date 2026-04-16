import getpass
import random
import re
import time
from threading import Thread

import pgzrun
import requests
from pygame import font

WIDTH = 640
HEIGHT = 480
TITLE = 'Mocna hra'

ball = Actor('ball')
ball.x = WIDTH / 2
ball.y = HEIGHT / 2
ball.dx = 1
ball.dy = -1
ball.speed = 3
ball.running = True

user = "user2"
paddle = Actor('paddle')
paddle.x = WIDTH / 2
paddle.bottom = HEIGHT
paddle.speed = 8

bricks = []
colors = ['red', 'purple', 'blue', 'yellow', 'green', 'grey']

class HighScores():
    text = ''
    offset = 0

high_scores = HighScores()

for y in range(4):
    for x in range(10):
        color = random.choice(colors)
        brick = Actor(f'brick.{color}')
        brick.left = x * brick.width
        brick.top = y * brick.height
        bricks.append(brick)


def draw():
    screen.blit('arkanoid.background', (0, 0))
    for brick in bricks:
        brick.draw()
    ball.draw()
    paddle.draw()

    width, _ = font.SysFont(None, 24).size(high_scores.text)
    screen.draw.text(high_scores.text, (WIDTH - high_scores.offset, HEIGHT - 20))
    if high_scores.offset < WIDTH + width:
        high_scores.offset += 1
    else:
        high_scores.offset = 0


def update():
    if high_scores.offset == 0:
        run_in_parallel(update_scores, [])

    if ball.running is True:
        ball.x = ball.x + ball.dx * ball.speed
        ball.y = ball.y + ball.dy * ball.speed

        if ball.right > WIDTH:
            ball.dx = -1

        elif ball.left < 0:
            ball.dx = +1

        if ball.top < 0:
            ball.dy = +1

        elif ball.bottom > HEIGHT:
            print('Looser')
            # send score to backend (lose)
            run_in_parallel(send_score, [len(bricks)])
            quit()

        for brick in bricks:
            if ball.colliderect(brick):
                
                payload = {
                    "name": user,
                    "action": "brick_destroyed",
                    "target": brick.image,
                    "remaining_bricks": len(bricks)-1
                }
                run_in_parallel(send_event, [payload])
                
                bricks.remove(brick)
                ball.dy = -ball.dy
                break

        #paddle.x = ball.x
        if keyboard.left is True:
            paddle.x -= paddle.speed

        if keyboard.right is True:
            paddle.x += paddle.speed

        if paddle.left < 0:
            paddle.left = 0

        if paddle.right > WIDTH:
            paddle.right = WIDTH

        if ball.colliderect(paddle):
            ball.dy *= -1

        if len(bricks) == 0:
            print('Well Done')
            # send score to backend (win)
            run_in_parallel(send_score, [len(bricks)])
            quit()


def run_in_parallel(function, args):
    thread = Thread(target=function, args=args)
    thread.start()

def send_score(score_value):
    try:
        requests.post('http://localhost:8000/score', json={'name': user, 'score': score_value})
        #requests.post('http://localhost:8000/score', json={'name': 'user_No.2', 'score': score_value})
    except Exception as e:
        print(f"Failed to send score: {e}")

def update_scores():
    try:
        values = requests.get('http://localhost:8000/score').json()
        high_scores.text = ' | '.join([value['name'] + ': ' + str(value['score']) for value in values])
    except Exception:
        high_scores.text = "Score server unavailable"

def send_event(event_data):
    try:
        requests.post('http://localhost:8000/event', json=event_data)
    except Exception as e:
        print(f"Failed to send event: {e}")

pgzrun.go()