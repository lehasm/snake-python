
import sys, random, time
import keyboard

GRASS   = '.'
STONE   = 'O'
HEAD    = '+'
BODY    = '+'
TAIL    = '+'

GROUND  = ( 0,  0)
UP      = (-1,  0)
DOWN    = ( 1,  0)
RIGHT   = ( 0,  1)
LEFT    = ( 0, -1)

space = None
step_duration_ms = 1000
step = 0
snakes = {
    'my' : []
}

def CreateSpace(space_width = 12,
                space_height = 8):
    global space
    space = [ [GRASS for i in range(space_width)] for j in range(space_height)]
    # print(space)


def SimpleConsoleDisplay(space):
    """
    Отображает символы поля в консоли без преобразований
    """
    for row in space:
        for field in row: 
            print(field[0], end='')
        print()


def CreateSnake(name = 'my', length = 5, x = None, y = None, look = None):
    global space
    global snakes
    x = x or len(space)//2
    y = y or len(space[x])//2
    look = look or UP
    snake = []
    for i in range(length):
        snake.append({'field' : (x, y+i), 'look' : UP})
    snakes[name] = snake


def UpdateSnakeLook(snake):
    update_dict = {'up': UP, 'down': DOWN, 'right': RIGHT, 'left': LEFT, 'space': GROUND}
    for key, look in update_dict.items():
        if keyboard.is_pressed(key):
            if snake[0]['look'] != look:
                snake[0]['look'] = look
                print('New look:', snake[0]['look'])


def SimpleWaitNextStep():
    t_start_ns = time.perf_counter_ns()
    while(time.perf_counter_ns() < (t_start_ns + step_duration_ms * 10**6)):
        time.sleep(0.05)
        UpdateSnakeLook(snakes['my'])

def MoveSnake(snake):
    pass


def Step():
    global step
    step += 1


def Run(DisplayFunction = SimpleConsoleDisplay, WaitNextStepFunction = SimpleWaitNextStep):
    """
    Выполняет главный цикл игры,
    при этом вызывает функции отображения и 
    ожидания следующего шага.
    """
    CreateSpace()
    CreateSnake()
    DisplayFunction(space)

    while(True):
        WaitNextStepFunction()
        Step()
        # DisplayFunction(space)


if __name__ == '__main__':
    print('snake-python')
    Run()