import numpy as np
import random

_DEBUG=1

class Maze:
    def __init__(self, data=None, shape=(4, 4)) -> None:
        if data is not None:
            self.data = np.array(data, dtype=np.uint8)
            self.shape = self.data.shape
        else:
            self.data = np.zeros(shape, dtype=np.uint8)
            self.shape = shape
        self.dimension = len(self.shape)
        self.directions = [np.array([int(j == i) for j in range(self.dimension)], dtype=np.int32)
                           for i in range(self.dimension)]\
            + [np.array([-int(j == i) for j in range(self.dimension)], dtype=np.int32)
               for i in range(self.dimension)]

    def __getitem__(self, ticker):
        return self.data[tuple(ticker)]

    def __setitem__(self, ticker, value):
        if value < 0:
            value = 0
        elif value > 255:
            value = 255
        self.data[tuple(ticker)] = int(value)

    def legalTicker(self, ticker: np.ndarray):
        return np.all(ticker >= 0) and np.all(ticker < self.shape)

    def neighbors(self, ticker):
        places = [ticker+d for d in self.directions]
        places = [t for t in places if self.legalTicker(t)]
        return places

    def deepcopy(self):
        return Maze(self.data.copy())

    def __str__(self):
        if self.dimension == 1:
            return ' '.join(map(str, self.data))
        elif self.dimension == 2:
            return '\n'.join([' '.join(map(str, self.data[:, i])) for i in range(self.shape[1])])
        else:
            return 'Maze object{{dimension:{}, shape:{}}}'.format(self.dimension, self.shape)

    def generate(self):
        # if _MazeGenerator.smul(self.shape)>2400:
        #     import sys
        #     sys.setrecursionlimit(9999)
        self.data.fill(1)
        while self.data[(-1,)*self.dimension] == 1:
            self.data.fill(1)
            self.data = _MazeGenerator(self.data)()
        # self.data = _MazeGenerator(self.data)()

    def findpath(self, start=None, end=None):
        if start == None:
            start = (0,)*self.dimension
        elif not self.legalTicker(np.array(start, dtype=np.int32)):
            raise ValueError("start not a valid ticker")
        if end == None:
            end = tuple([i-1 for i in self.shape])
        elif not self.legalTicker(np.array(end, dtype=np.int32)):
            raise ValueError("end not a valid ticker")
        return _PathFinder(self, start, end)()


class _MazeGenerator(Maze):
    def __init__(self, data) -> None:
        super().__init__(data)
        self.exploreHistory = [np.array((0,)*self.dimension, dtype=np.int32)]
        self.result = False
        self.funcDeque = []  # (func, (args))
        if self.dimension == 4:
            try:
                if not _DEBUG:
                    raise ImportError("Unknown bug not ready to be fixed")
                import mazeGeneratorCExtension as fourDExtension
                self.extended = True
                self.fourDExtension = fourDExtension
            except ImportError:
                if _DEBUG:
                    __import__('traceback').print_exc()
                self.extended = False
        else:
            self.extended = False

    def emptyNeighbors(self, ticker):
        return [t for t in self.neighbors(ticker) if self[t] == 1]

    def allEmptyNeighbor(self, ticker, exception=None):
        for t in self.neighbors(ticker):
            if exception is not None and np.all(t == exception):
                continue
            if self[t] == 0:
                return False
        return True

    def dig(self, ticker):
        out = self[ticker]
        self[ticker] = 0
        return out

    def explore(self, ticker):
        if self[ticker] == 1 and self.allEmptyNeighbor(ticker, self.exploreHistory[-1]):
            self.dig(ticker)
            self.exploreHistory.append(ticker)
            targets = self.neighbors(ticker)
            _funcdeq = []
            if targets:
                random.shuffle(targets)
                for t in targets:
                    _funcdeq.append((self.explore, (t,)))
            _funcdeq.append((self.exploreHistory.pop, ()))
            self.funcDeque = _funcdeq+self.funcDeque

    @staticmethod
    def smul(a):
        out = 1
        for i in a:
            out *= i
        return out

    def nran(self):
        t = []
        for i in range(self.dimension):
            t.append(random.randint(0, self.shape[i]-1))
        return np.array(t, dtype=np.int32)

    def randRemove(self, prop=0.03):
        for _ in range(int(prop*self.smul(self.shape))):
            self.dig(self.nran())

    def makeDest(self, _f=None):
        "make way to dest if a path doesn't exist."
        if _f is None:
            if self[[i-1 for i in self.shape]] == 1:
                try:
                    self.makeDest([i-1 for i in self.shape])
                except RuntimeError:
                    return
        else:
            if self.dig(_f) == 0:
                raise RuntimeError
            self.makeDest(random.choice(self.neighbors(_f)))

    def __call__(self):
        if self.result == False:
            if self.dimension == 4 and self.extended:
                self.fourDExtension.generate(self)
            else:
                self.explore(np.array((0,)*self.dimension, dtype=np.int32))
                while self.funcDeque:
                    func, args = self.funcDeque.pop(0)
                    func(*args)
            self.result = True
            self.makeDest()
            self.randRemove()
        return self.data


class _PathFinder:
    def __init__(self, maze: Maze, start, end) -> None:
        self.maze = maze
        self.dest = np.array(end, dtype=np.int32)
        start = tuple(start)
        self.history = {start: None}  # latter->former
        self.frontier = [start]
        self.costs = {start: 0}  # ticker:current_cost

    def roadNeighbors(self, ticker):
        return [t for t in self.maze.neighbors(ticker) if self.maze[t] == 0]

    def distance(self, ticker):
        return sum(abs(ticker-self.dest))

    def _findpath(self, start):
        current_cost = self.costs[tuple(start)]
        nextstep = self.roadNeighbors(start)
        if self.history[tuple(start)] is not None:
            for i in range(len(nextstep)):
                if np.all(nextstep[i] == self.history[tuple(start)]):
                    nextstep.pop(i)
                    break
        for t in nextstep:
            if tuple(t) in self.costs:
                if current_cost+1 < self.costs[tuple(t)]:
                    self.costs[tuple(t)] = current_cost+1
                    self.history[tuple(t)] = start
            else:
                self.history[tuple(t)] = start
                self.frontier.append(t)
                self.costs[tuple(t)] = current_cost+1
        self.frontier.sort(key=lambda t: self.distance(t)+self.costs[tuple(t)])

    def __call__(self):
        while tuple(self.dest) not in self.costs:
            t = self.frontier.pop(0)
            self._findpath(t)
        out = [self.dest]
        while out[-1] is not None:
            out.append(self.history[tuple(out[-1])])
        out.pop()
        return [tuple(i) for i in out[::-1]]


if __name__ == "__main__":
    a = Maze(shape=(20, 20, 1, 1))
    a.generate()
    print(hex(a.data.ctypes._as_parameter_.value))
    a2 = Maze(a.data[:, :, 0, 0], (20, 20))
    print(a2)
    print(''.join([str(i).replace(' ', '') for i in a2.findpath()]))
