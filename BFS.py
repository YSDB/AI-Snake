# coding: utf-8
import pygame
import sys
import time
import random
from pygame.locals import *

redcolor = pygame.Color('red')
bluecolor = pygame.Color('blue')
blackcolor = pygame.Color('black')
whitecolor = pygame.Color('white')

Height = 25
Width = 25
Space = Height*Width
Head = 0

Left = -1
Right = 1
Up = -Width
Down = Width

Food = 0
Default = (Height+1)*(Width+1)
Snake = 2*Default

Error = -1234

board = [0]*Space
snake = [0]*(Space+1)
snake[Head] = 1*Width+1
snake_size = 1

tmpboard = [0]*Space
tmpsnake = [0]*(Space+1)
tmpsnake[Head] = 1*Width+1
tmpsnake_size = 1

food = 4*Width+7
bst_mov = Error

move = [Left,Right,Up,Down]
score =0

def free_cell(idx,vsize,vsnake):
    return not (idx in vsnake[:vsize]) #see if 'idx' is in vsnake[:vsize]

def move_possible(idx,vmove):
    flag = False
    if vmove == Left:
        flag = True if idx%Width > 1 else False
    if vmove == Right:
        flag = True if idx%Width < 23 else False
    if vmove == Up:
        flag = True if idx//Width >1 else False
    if vmove == Down:
        flag = True if idx//Width <23 else False
    return flag



def distance_reset(vsnake,vsize,vboard):# Discern three kinds of parameters
    for i in range(Space):
        if i == food:
            vboard[i] = Food
        elif free_cell(i,vsize,vsnake):
            vboard[i] = Default
        else:
            vboard[i] = Snake


def distance_BFS(vfood,vsnake,vboard):
    queue = []
    queue.append(vfood)
    inqueue = [0] * Space
    found = False
    while len(queue)!=0:
        idx = queue.pop(0)#food position
        #print('a=',idx)
        if inqueue[idx] == 1:
            #print('b=',inqueue[idx])
            continue
        inqueue[idx] = 1 #food position is 1
        for i in range(4):
            #print(idx+move[i])
            #print(vboard[idx]+1)
            #print(vboard[idx+move[i]])
            if move_possible(idx, move[i]):
                if idx + move[i] == vsnake[Head]: 
                    found = True
                if vboard[idx+move[i]] < Snake: # not snake body
                    if vboard[idx+move[i]] > vboard[idx]+1:
                        vboard[idx+move[i]] = vboard[idx]+1
                    if inqueue[idx+move[i]] == 0: 
                        queue.append(idx+move[i])
                        #print(queue)
    #print('found',found)
    return found
                    
def short_path(vsnake,vboard):
    bst_mov = Error
    min = Snake
    for i in range(4):
        if move_possible(vsnake[Head],move[i]) and vboard[vsnake[Head]+move[i]]<min:
            min = vboard[vsnake[Head]+move[i]]
            bst_mov= move[i]
    return bst_mov
                         
def long_path(vsnake,vboard):
    bst_mov = Error
    max = Snake
    for i in range(4):
        if move_possible(vsnake[Head],move[i]) and vboard[vsnake[Head]+move[i]]<Default:
            max = vboard[vsnake[Head]+move[i]]
            bst_mov = move[i]
    return bst_mov

def tail_check():
    global tmpboard,tmpsnake,food,tmpsnake_size
    tmpboard[tmpsnake[tmpsnake_size-1]] = 0
    tmpboard[food] = Snake
    result = distance_BFS(tmpsnake[tmpsnake_size-1],tmpsnake,tmpboard)
    for i in range(4):
        if move_possible(tmpsnake[Head],move[i]) and tmpsnake[Head]+move[i]==tmpsnake[tmpsnake_size-1] and tmpsnake_size>3:
            result = False
    return result

def follow_tail():
    global tmpboard,tmpsnake,food,tmpsnake_size
    tmpsnake_size = snake_size
    tmpsnake = snake[:] # avoid change simultaneously, or they aim at same list
    distance_reset(tmpsnake,tmpsnake_size,tmpboard)
    tmpboard[tmpsnake[tmpsnake_size-1]] = Food
    tmpsnake[food] = Snake
    distance_BFS(tmpsnake[tmpsnake_size-1],tmpsnake,tmpboard)
    tmpboard[tmpsnake[tmpsnake_size-1]] = Snake
    return long_path(tmpsnake,tmpboard)

def random_walking():
    global food,snake,snake_size,board
    bst_mov = Error
    distance_reset(snake,snake_size,board)
    distance_BFS(food,snake,board)
    min = Snake

    for i in range(4):
        if move_possible(snake[Head],move[i]) and board[snake[Head]+move[i]]<min:
            min = board[snake[Head]+move[i]]
            bst_mov = move[i]
    return bst_mov

def shift_array(arr,size):
    for i in range(size,0,-1):
        arr[i] = arr[i-1]

def food_generate():
    global food,snake_size
    cell = False
    while not cell:
        W = random.randint(1,Width-2)
        H = random.randint(1,Height-2)
        food = H*Width + W
        cell = free_cell(food,snake_size,snake)
    pygame.draw.rect(playsurface,redcolor,Rect(20*(food//Width),20*(food%Width),20,20))
        

def real_move(vbst_mov):
    global snake,board,snake_size,score
    shift_array(snake,snake_size)
    snake[Head] += vbst_mov
    p = snake[Head]
    for body in snake:
        pygame.draw.rect(playsurface,whitecolor,Rect(20*(body//Width),20*(body%Width),20,20))
        pygame.draw.rect(playsurface,bluecolor,Rect(20*(p//Width),20*(p%Width),20,20))
    pygame.draw.rect(playsurface,whitecolor,Rect(20*(snake[snake_size-1]//Width),20*(snake[snake_size-1]%Width),20,20))
    pygame.draw.rect(playsurface,bluecolor,Rect(0,0,20,20))

    pygame.display.flip()

    if snake[Head] == food:
        board[snake[Head]]= Snake
        snake_size += 1
        score += 1
        if snake_size < Space: food_generate()
    else:
        board[snake[Head]] = Snake
        board[snake[snake_size]] = Default
        pygame.draw.rect(playsurface,blackcolor,Rect(20*(snake[snake_size]//Width),20*(snake[snake_size%Width]),20,20))

        pygame.display.flip()
        
def virtual_move():
    global snake,board,snake_size,tmpsnake,tmpboard,tmpsnake_size,food
    tmpsnake_size = snake_size
    #print(snake_size)
    tmpsnake = snake[:]
    tmpboard = board[:]
    distance_reset(tmpsnake,tmpsnake_size,tmpboard)

    food_ate = False

    while not food_ate:
        distance_BFS(food,tmpsnake,tmpboard)
        Move = short_path(tmpsnake,tmpboard)
        shift_array(tmpsnake,tmpsnake_size)
        tmpsnake[Head] += Move
        #print(tmpsnake)
        if tmpsnake[Head] == food:
            tmpsnake_size += 1
            distance_reset(tmpsnake,tmpsnake_size,tmpboard)
            tmpboard[food] = Snake
            food_ate = True

        else:
            tmpboard[tmpsnake[Head]] = Snake
            tmpboard[tmpsnake[tmpsnake_size-1]] = Default

def safe_way():
    global snake,board
    safe_move = Error
    virtual_move()
    #print(888)
    if tail_check():
        return short_path(snake,board)
    safe_move = follow_tail()
    #print(safe_move)
    return safe_move

    

pygame.init()
playtime = pygame.time.Clock()
playsurface = pygame.display.set_mode((500,500))
pygame.display.set_caption('Gluttonous Snake')
playsurface.fill(blackcolor)



pygame.draw.rect(playsurface,redcolor,Rect(20*(food//Width),20*(food%Width),20,20))

while True:
    for event in pygame.event.get():
        if event == QUIT:
            print(score)
            pygame.quit()
            sys.exit()
        elif event == KEYDOWN:
            if event.key == K_ESCAPE:
                print(score)
                pygame.quit()
                sys.exit()
    pygame.display.flip()
    pygame.draw.rect(playsurface,bluecolor,Rect(0,0,500,500),40)
       
            
    distance_reset(snake,snake_size,board)
    #print(666)
    
    if distance_BFS(food,snake,board):
        #print(888)
        bst_mov = safe_way()
        #print(123)
    else:
        bst_mov = follow_tail()
        #print(234)
        
    if bst_mov == Error:
        bst_mov = random_walking()
        #print(345)
    if bst_mov != Error:
        real_move(bst_mov)
        #print(456)
        
    else:
        print(score)
        sys.exit()
    playtime.tick(1)
