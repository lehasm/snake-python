
import sys, random, time
import keyboard
import operator

GRASS   = '.'
STONE   = 'O'
HEAD    = '+'
BODY    = '#'
TAIL    = '#'
BUG     = '*'
FAULT   = 'X'

class Space(object):    

    def __init__(self, width = 16, height = 10):
        self._width = width
        self._height = height
        self._space = [ [[GRASS] for i in range(width)] for j in range(height)]

    def Display(self):
        pass

    def GetField(self, complex_coordinate):
        r = int(complex_coordinate.real)
        c = int(complex_coordinate.imag)
        if (0 <= r < len(self._space)) and (0 <= c < len(self._space[r])) :
                return self._space[r][c]
        return [FAULT]

    def GetFieldTop(self, complex_coordinate):
        return self.GetField(complex_coordinate)[-1]

    def PlaceFieldTop(self, complex_coordinate, what):
        self.GetField(complex_coordinate).append(what)

    def RemoveFieldTop(self, complex_coordinate):
        f = self.GetField(complex_coordinate)
        if f: del f[-1]


    def ElevateSnake(self, snake):
        for s in snake:
            if  snake.IsSnake(self.GetFieldTop(s['field'])):
                self.RemoveFieldTop(s['field'])

    def PlaceSnake(self, snake):
        for s in snake:
            self.PlaceFieldTop(s['field'], snake.WhatSegment(s))

    def PlaceRandom(self, what, how_much = 1):
        if isinstance(how_much, float):
            how_much = int(how_much * self._width * self._height)
        for _ in range(how_much):
            r = random.randrange(0, self._height)
            c = random.randrange(0, self._width)
            self.PlaceFieldTop(complex(r, c), what)


class ConsoleSpace(Space):
    def Display(self):
        """
        Отображает самый верхний (с наибольшим индексом) 
        символ поля в консоли без преобразований
        """
        print("\n\n\n\n\n")
        for row in self._space:
            for field in row: 
                print(field[-1], end=' ')
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
        self._step_duration_s = 0.4
        self._segments = []
        self._segments.append({'field' : complex(x, y), 'look' : look})
        for i in range(1, length):
            self.AppendTail()
            # self._segments.append({'field' : complex(x, y+i), 'look' : look})
            # look = self.LEFT
    
    def AppendTail(self, side = GROUND):
        tail = self._segments[-1]
        new_segment = {'field' : tail['field'] + side, 'look' : -side}
        self._segments.append(new_segment)

    def TrimTail(self):
        if len(self._segments) > 1:
            del self._segments[-1]

    def __iter__(self):
        return iter(self._segments)

    @classmethod
    def IsSnake(cls, w):
        return w in (HEAD, BODY, TAIL)

    def GetStepPeriod(self):
        return self._step_duration_s
    def IncreaseSpeed(self):
        self._step_duration_s /= 1.2
    def DecreaseSpeed(self):
        self._step_duration_s *= 1.2

    def GetHead(self):
        return self._segments[0]
    def SetHeadLook(self, l):
        self.GetHead()['look'] = l
    def GetHeadLook(self):
        return self.GetHead()['look']

    def GetLookField(self):
        return self.GetHead()['field'] + self.GetHead()['look']

    def Move(self):
        if self.GetHead()['look'] == self.GROUND:
            return
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

    def WhatSegment(self, segment):
        if segment == self._segments[0]:
            return HEAD
        elif segment == self._segments[-1]:
            return TAIL
        else:
            return BODY


def ControlSnakeStep(snake, poll_period_s = 0.05):
    look_dict = {'up': Snake.UP, 'down': Snake.DOWN, 
                 'right': Snake.RIGHT, 'left': Snake.LEFT, 
                 'space': Snake.GROUND}

    spead_changed = 0
    t_start_ns = time.perf_counter_ns()
    control_period_s = snake.GetStepPeriod()
    while(time.perf_counter_ns() < (t_start_ns + control_period_s * 10**9)):
        time.sleep(poll_period_s)
        for key, look in look_dict.items():
            if keyboard.is_pressed(key):
                snake.SetHeadLook(look)
        if not spead_changed and keyboard.is_pressed('+'):
            snake.IncreaseSpeed()
            spead_changed = 1
        if not spead_changed and keyboard.is_pressed('-'):
            snake.DecreaseSpeed()
            spead_changed = 1

def Interact(snake, space):
    look_field = snake.GetLookField()
    in_front = space.GetFieldTop(look_field)
    if in_front == GRASS:
        pass
    elif in_front == BUG:
        space.RemoveFieldTop(look_field)
        snake.AppendTail()
        space.PlaceRandom(BUG)
    else:
        # Other (or unknown) field
        snake.SetHeadLook(Snake.GROUND)

    if(snake.GetHeadLook() != Snake.GROUND):
        space.ElevateSnake(snake)
        snake.Move()
        space.PlaceSnake(snake)


def Run():
    """
    Выполняет главный цикл игры,
    при этом вызывает функции отображения и 
    ожидания следующего шага.
    """
    space = ConsoleSpace()
    space.PlaceRandom(STONE, how_much=0.05)
    space.PlaceRandom(BUG, how_much=1)
    # space = DebugConsoleSpace()

    snakes = {}
    my_snake = Snake()
    snakes["my"] = my_snake

    space.PlaceSnake(my_snake)
    space.Display()

    try:
        while(True):
            ControlSnakeStep(my_snake)

            for snake in snakes.values():
                Interact(snake, space)
            
            space.Display()

    except KeyboardInterrupt as e:
        print('We hope you have fun')

if __name__ == '__main__':
    print('snake-python')
    Run()