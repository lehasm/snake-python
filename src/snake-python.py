
import sys, random, time
import keyboard
import operator

GRASS   = '.'
STONE   = 'O'
HEAD    = '+'
BODY    = '#'
TAIL    = '#'

class Space(object):    

    def __init__(self, width = 12, height = 8):
        self._space = [ [[GRASS] for i in range(width)] for j in range(height)]

    def Display(self):
        pass

    def _GetField(self, complex_coordinate):
        r = int(complex_coordinate.real)
        c = int(complex_coordinate.imag)
        if (0 <= r < len(self._space)) and (0 <= c < len(self._space[r])) :
                return self._space[r][c]
        return None

    def ElevateSnake(self, snake):
        for s in snake:
            f = self._GetField(s['field'])
            if f is None:
                continue

            for i in range(len(f)):
                if snake.IsSnake(f[-i]):
                    del f[-i]
                    break
            else:
                raise KeyError("No snake found in field {}: {}".format(
                                s['field'], str(f)))

    def PlaceSnake(self, snake):
        for s in snake:
            f = self._GetField(s['field'])
            if f:
                f.append(snake.WhatSegment(s))

class ConsoleSpace(Space):
    def Display(self):
        """
        Отображает самый верхний (с наибольшим индексом) 
        символ поля в консоли без преобразований
        """
        for row in self._space:
            for field in row: 
                print(field[-1], end='')
            print()

class DebugConsoleSpace(Space):
    def Display(self):
        """
        Отображает самый верхний (с наибольшим индексом) 
        символ поля в консоли без преобразований
        """
        print("-"*(4*12))
        for row in self._space:
            for field in row: 
                print("{:4}".format(''.join(field)), end='')
            print()


class Snake(object):
    GROUND  = complex ( 0,  0)
    UP      = complex (-1,  0)
    DOWN    = complex ( 1,  0)
    RIGHT   = complex ( 0,  1)
    LEFT    = complex ( 0, -1)
    
    def __init__(self, length = 5, x = 0, y = 0, look = DOWN):
        self._segments = []
        for i in range(length):
            self._segments.append({'field' : complex(x, y+i), 'look' : look})
            look = self.LEFT
    
    def __iter__(self):
        return iter(self._segments)

    @classmethod
    def IsSnake(cls, w):
        return w in (HEAD, BODY, TAIL)

    def Move(self):
        for i in range(len(self._segments)-1, -1, -1):
            s = self._segments[i]
            # print("Move", s)
            # move segment in a look direction
            # (add coordinates)
            s['field'] = s['field'] + s['look']
            if i != 0:
                # set next segment look
                s['look'] = self._segments[i-1]['look'] 
            # print("New", s)

    def SetHeadLook(self, l):
        self._segments[0]['look'] = l

    def WhatSegment(self, segment):
        if segment == self._segments[0]:
            return HEAD
        elif segment == self._segments[-1]:
            return TAIL
        else:
            return BODY


def ControlSnakeDuring(snake, control_period_s, poll_period_s = 0.05):
    look_dict = {'up': Snake.UP, 'down': Snake.DOWN, 
                 'right': Snake.RIGHT, 'left': Snake.LEFT, 
                 'space': Snake.GROUND}

    t_start_ns = time.perf_counter_ns()
    while(time.perf_counter_ns() < (t_start_ns + control_period_s * 10**9)):
        time.sleep(poll_period_s)
        for key, look in look_dict.items():
            if keyboard.is_pressed(key):
                snake.SetHeadLook(look)


def Run():
    """
    Выполняет главный цикл игры,
    при этом вызывает функции отображения и 
    ожидания следующего шага.
    """
    space = ConsoleSpace()
    space = DebugConsoleSpace()

    snakes = {}
    my_snake = Snake()
    snakes["my"] = my_snake

    space.PlaceSnake(my_snake)
    space.Display()

    # space.ElevateSnake(my_snake)
    # space.Display()
    # space.ElevateSnake(my_snake)
    # return

    try:
        while(True):
            ControlSnakeDuring(my_snake, control_period_s=0.5)

            for snake in snakes.values():
                space.ElevateSnake(snake)
                snake.Move()
                space.PlaceSnake(snake)
            
            space.Display()

    except KeyboardInterrupt as e:
        print('We hope you have fun')

if __name__ == '__main__':
    print('snake-python')
    Run()