"""Snake game. Snake just stops ahead of stones borders and other snakes. He does not die. """

import sys, random, time
import keyboard
import operator

GRASS   = '.'
STONE   = 'O'
HEAD    = '+'
BODY    = '#'
TAIL    = '`'
BUG     = '*'
FAULT   = 'x'

class Space(object):    

    def __init__(self, width = 32, height = 20):
        self._width = width
        self._height = height
        self._space = [ [[GRASS] for i in range(width)] for j in range(height)]
        self.info = ''

    def Display(self):
        print(self.info)

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
        super().Display()
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

class WinConsoleSpace(Space):
    # https://en.wikipedia.org/wiki/Box-drawing_character
    # https://en.wikipedia.org/wiki/Geometric_Shapes
    # ...
    # "\u2219" - bold dot
    sim_table = {BUG : '\u263C', 
                 GRASS : ' ', STONE : "\u2588",
                 HEAD : "\u263B", BODY : "\u25CB", TAIL : "\u25CB"}
    BORDER_H = "\u2500"
    BORDER_V = "\u2502"
    CORNER_0 = "\u250C"
    CORNER_1 = "\u2510"
    CORNER_2 = "\u2518"
    CORNER_3 = "\u2514"
    CLEAR_RIGHT = " "*10

    def GetSymbol(self, s):
        return self.sim_table.get(s, None) or s

    def __init__(self, width = 32, height = 20):
        super().__init__(width, height)
        import WinConsole
        self.c = WinConsole.WinConsoleClass()
        self.start_line = self.c.get_console_cursor_pos()["y"]
        print("\n"*(height+5))  # space placeholder

    def Display(self):
        self.c.set_console_cursor_pos(0, self.start_line)
        super().Display()
        self.c.set_console_cursor_pos(0, self.start_line+2)
        # self.c.set_console_color(self.c.FOREGROUND_YELLOW, 
        #                          self.c.BACKGROUND_BLACK)
        print(self.CORNER_0, self.BORDER_H * self._width, self.CORNER_1,
              self.CLEAR_RIGHT, sep='')
        for row in self._space:
            print(self.BORDER_V, end='')
            for field in row: 
                print(self.GetSymbol(field[-1]), end='')
            print(self.BORDER_V, self.CLEAR_RIGHT, sep='')        
        print(self.CORNER_3, self.BORDER_H * self._width, self.CORNER_2, 
              self.CLEAR_RIGHT, sep='')



class Snake(object):
    GROUND  = complex ( 0,  0)
    UP      = complex (-1,  0)
    DOWN    = complex ( 1,  0)
    RIGHT   = complex ( 0,  1)
    LEFT    = complex ( 0, -1)
    
    def __init__(self, length = 5, x = 0, y = 0, look = DOWN):
        self._is_alive = True
        self._step_index = 0
        self._relief_time = None
        self._step_duration_s = 0.3
        self._segments = []
        self._segments.append({'field' : complex(x, y), 'look' : look})
        for i in range(1, length):
            self.AppendTail()
            # self._segments.append({'field' : complex(x, y+i), 'look' : look})
            # look = self.LEFT
    
    def IsAlive(self):
        return self._is_alive

    def SetAlive(self, v):
        self._is_alive = v
    
    def GetReliefTime(self):
        return self._relief_time

    def SetReliefTime(self, v):
        self._relief_time = v

    def AppendTail(self, side = GROUND):
        tail = self._segments[-1]
        new_segment = {'field' : tail['field'] + side, 'look' : -side}
        self._segments.append(new_segment)

    def TrimTail(self):
        if len(self._segments) > 1:
            del self._segments[-1]

    def __iter__(self):
        return iter(self._segments)

    def __getitem__(self, key):
        return self._segments[key]

    @classmethod
    def IsSnake(cls, w):
        return w in (HEAD, BODY, TAIL)

    def GetLength(self):
        return len(self._segments)

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
    def GetHeadField(self):
        return self.GetHead()['field']
    def GetLookField(self):
        return self.GetHead()['field'] + self.GetHead()['look']

    def Move(self):
        if self.GetHeadLook() == self.GROUND:
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

    def Interact(self, space):
        look_field = self.GetLookField()
        in_front = space.GetFieldTop(look_field)
        
        if in_front == GRASS:
            pass
        elif in_front == BUG:
            space.RemoveFieldTop(look_field)
            self.AppendTail()
            space.PlaceRandom(BUG)
        else:
            # Other (or unknown) field
            self.SetHeadLook(Snake.GROUND)

        if (self.GetReliefTime() and self._step_index > 0 and
            self._step_index % self.GetReliefTime() == 0):
            tail_field = self[-1]['field']
            self.TrimTail()
            space.PlaceFieldTop(tail_field, FAULT)
            if self.GetLength() <= 1:
                self.SetAlive(False)
        self._step_index += 1


class AiSnake(Snake):
        
    def Interact(self, space):
        looks = [self.UP,  self.RIGHT, self.DOWN, self.LEFT]
        random.shuffle(looks)
        allowed_looks = []
        for look in looks:
            in_front = space.GetFieldTop(self.GetHeadField() + look)
            if in_front == BUG:
                self.SetHeadLook(look)
                break
            if in_front == GRASS:
                allowed_looks.append(look)
        if space.GetFieldTop(self.GetLookField()) not in (GRASS, BUG):
            look = allowed_looks[0] if len(allowed_looks) > 0 else self.GROUND
            self.SetHeadLook(look)

        Snake.Interact(self, space)



def ControlSnakeStep(snake, poll_period_s = 0.05):
    look_dict = {'up': Snake.UP, 'down': Snake.DOWN, 
                 'right': Snake.RIGHT, 'left': Snake.LEFT, 
                 'space': Snake.GROUND}

    speed_changed = 0
    t_start_ns = time.perf_counter_ns()
    control_period_s = snake.GetStepPeriod()
    while(time.perf_counter_ns() < (t_start_ns + control_period_s * 10**9)):
        time.sleep(poll_period_s)
        for key, look in look_dict.items():
            if keyboard.is_pressed(key):
                snake.SetHeadLook(look)
        if not speed_changed and keyboard.is_pressed('+'):
            snake.IncreaseSpeed()
            speed_changed = 1
        if not speed_changed and keyboard.is_pressed('-'):
            snake.DecreaseSpeed()
            speed_changed = 1
        if keyboard.is_pressed('Esc'):
            snake.SetAlive(False)



def Run():
    """
    Выполняет главный цикл игры,
    при этом вызывает функции отображения и 
    ожидания следующего шага.
    """
    try:
        while(True):
            # space = ConsoleSpace()
            # space = DebugConsoleSpace()
            space = WinConsoleSpace()
            space.PlaceRandom(STONE, how_much=0.05)
            space.PlaceRandom(BUG, how_much=1)

            snakes = {}
            my_snake = Snake()
            my_snake.SetReliefTime(100)
            snakes["my"] = my_snake

            neighbour_snake = AiSnake(x = 5 , y = 5)
            snakes["Jim"] = neighbour_snake

            for s in snakes.values():
                space.PlaceSnake(s)
            space.Display()

            while(True):
                ControlSnakeStep(my_snake)

                for snake in snakes.values():
                    snake.Interact(space)
                    space.ElevateSnake(snake)
                    snake.Move()
                    space.PlaceSnake(snake)
                
                space.info = "Length: {} Step time: {:0.2f}".format(
                        my_snake.GetLength(), my_snake.GetStepPeriod())
                space.Display()
                if not my_snake.IsAlive():
                    break

    except KeyboardInterrupt as e:
        print('We hope you have fun')
        

if __name__ == '__main__':
    Run()