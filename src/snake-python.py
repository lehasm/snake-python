
import sys, random, time
import keyboard
import operator

GRASS   = '.'
STONE   = 'O'
HEAD    = '+'
BODY    = '+'
TAIL    = '+'

class Space(object):    

    def __init__(self, width = 12, height = 8):
        self._space = [ [[GRASS] for i in range(width)] for j in range(height)]

    def Display(self):
        pass

    def _GetField(self, r, c):
        # print(f, self._space[f[0]], self._space[f[0]][f[1]])
        if self._space[r:] and self._space[r][c:] :
            return self._space[r][c]
            return None

    def ElevateSnake(self, snake):
        for s in snake:
            f = self._GetField(*s['field'])
            for i in range(len(f)):
                if snake.IsSnake(f[-i]):
                    del f[-i]
                    break
            else:
                raise KeyError("No snake found in field [{}][{}]: {}".format(
                                s['field'][0], s['field'][1], str(f)))

    def PlaceSnake(self, snake):
        for s in snake:
            f = self._GetField(*s['field'])
            if f:
                f.append(HEAD)

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
    GROUND  = ( 0,  0)
    UP      = (-1,  0)
    DOWN    = ( 1,  0)
    RIGHT   = ( 0,  1)
    LEFT    = ( 0, -1)
    
    def __init__(self, length = 5, x = 0, y = 0, look = DOWN):
        self._segments = []
        for i in range(length):
            self._segments.append({'field' : (x, y+i), 'look' : look})
    
    def __iter__(self):
        return iter(self._segments)

    @classmethod
    def IsSnake(cls, w):
        return w in (HEAD, BODY, TAIL)

    def Move(self):
        for i in range(len(self._segments)-1, 1):
            s = self._segments[i]
            # move segment in a look direction
            # (add coordinates)
            s['field'] = tuple(map(operator.add, s['field'], s['look']))
            if i != 0:
                # set next segment look
                s['look'] = self._segments[i-1]['look'] 
        # print(self._segments)

    def SetHeadLook(self, l):
        self._segments[0]['look'] = l


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