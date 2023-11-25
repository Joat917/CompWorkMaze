from maze import Maze, np
from visualize import visualize
from PIL import Image, ImageDraw, ImageFont
import pygame
from sys import exit


class Main:
    root = None
    displays = []
    eventFuncs = []
    timelyFuncs = []
    refreshZones = []
    fullScreenRefresh = True
    fps = 20
    screenSize = (720, 540)

    def __init__(self) -> None:
        self.clock = pygame.time.Clock()
        pygame.display.init()
        Main.root = pygame.display.set_mode(self.screenSize)
        pygame.display.set_caption("MazeProject")
        try:
            im=pygame.image.load('./img/icon.png')
            pygame.display.set_icon(im)
        except:
            pass

        def _checkQuit(event):
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)
            return True

        def _forceRefresh(event):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.forceRefresh()

        # def _raiseExc(event):
        #     if event.type==pygame.KEYDOWN and event.key==pygame.K_q:
        #         raise RuntimeError('Fatal Error')
        self.eventFuncs.append(_checkQuit)
        self.eventFuncs.append(_forceRefresh)
        # self.eventFuncs.append(_raiseExc)

    def processEvent(self):
        for event in pygame.event.get():
            for func in self.eventFuncs:
                if func(event) == False:
                    break
        for func in self.timelyFuncs:
            func()

    @classmethod
    def forceRefresh(cls):
        pygame.display.flip()

    def display(self):
        if self.fullScreenRefresh or self.refreshZones:
            for func in self.displays:
                func()
            if self.fullScreenRefresh:
                pygame.display.flip()
            else:
                for z in self.refreshZones:
                    pygame.display.update(z)
            Main.fullScreenRefresh = False
            self.refreshZones.clear()

    def mainloop(self):
        while True:
            self.processEvent()
            self.display()
            self.clock.tick(self.fps)


class Background:
    def __init__(self, fp='./img/background.jpg', alt=(200, 0, 0)) -> None:
        try:
            im = Image.open(fp).convert('RGB')
            im = im.resize(Main.screenSize)
        except FileNotFoundError:
            im = Image.new('RGB', Main.screenSize, alt)
        self.image = pygame.image.frombuffer(
            im.tobytes(), im.size, 'RGB')
        Main.displays.append(self.show)

    def show(self):
        Main.root.blit(self.image, (0, 0))


class Button:
    def __init__(self, rect: pygame.Rect, text='Button', textcolor=(255, 255, 255, 255),
                 color=(127, 127, 127, 255), onclick=lambda: None,
                 font=ImageFont.truetype('arial.ttf', 20), keyCodes=[], buttonCodes=[1]) -> None:
        self.rect = rect
        self.onclick = onclick
        self.keyCodes = keyCodes
        self.buttonCodes = buttonCodes
        im = Image.new('RGBA', self.rect.size, color)
        if text:
            im2 = Image.new('RGBA', self.rect.size)
            ImageDraw.Draw(im2).text((0, 0), text, fill=textcolor, font=font)
            w = 0
            h = 0
            for x in range(im2.width-1, 0, -1):
                for y in range(im2.height):
                    if im2.getpixel((x, y))[3]:
                        w = x
                        break
                if w:
                    break
            for y in range(im2.height-1, 0, -1):
                for x in range(w):
                    if im2.getpixel((x, y))[3]:
                        h = y
                        break
                if h:
                    break
            im2 = im2.crop((0, 0, w+1, h+1))
            im.paste(im2, ((im.width-im2.width)//2,
                           (im.height-im2.height)//2), im2.getchannel('A'))
        self.image = pygame.image.frombuffer(
            im.tobytes(), im.size, 'RGBA')
        Main.displays.append(self.display)
        Main.eventFuncs.append(self.procEvent)

    def posInMe(self, pos: tuple):
        return self.rect.left < pos[0] < self.rect.right and self.rect.top < pos[1] < self.rect.bottom

    def procEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in self.buttonCodes:
                if self.posInMe(event.pos):
                    self.onclick()
        elif self.keyCodes and event.type == pygame.KEYDOWN:
            if event.key in self.keyCodes:
                self.onclick()

    def display(self):
        Main.root.blit(self.image, self.rect)

    def __del__(self):
        if self.display in Main.displays:
            Main.displays.remove(self.display)
        if self.procEvent in Main.eventFuncs:
            Main.eventFuncs.remove(self.procEvent)


class MazeShower:
    def __init__(self, pic: Image.Image) -> None:
        self.pic = pic
        self.mainrect = pygame.Rect(0, 0, 540, 540)
        self.zoom = 1
        self.picCoord = (0, 0)
        self.fit()
        Main.displays.append(self.show)
        Main.eventFuncs.append(self.procEvent)
        Main.timelyFuncs.append(self.timelyFunc)
        self._event_active = False
        self._event_buttonBonus = [0, 0]
        self._event_arrowDown = {
            pygame.K_UP: False, pygame.K_DOWN: False, pygame.K_LEFT: False, pygame.K_RIGHT: False}
        self._event_buttonMoveCooldown = 0
        self._event_last_block = None

    def xy2wh(self, x, y, check=True):
        target = (round((x-self.picCoord[0])/self.zoom),
                  round((y-self.picCoord[1])/self.zoom))
        if check and (target[0] < 0 or target[0] >= self.pic.width
                      or target[1] < 0 or target[1] >= self.pic.height):
            return None
        else:
            return target

    def wh2xy(self, w, h):
        return (round(w*self.zoom+self.picCoord[0]),
                round(h*self.zoom+self.picCoord[1]))

    def rezoom(self, zoom, center=(0, 0)):
        c = self.xy2wh(*center, check=False)
        self.zoom = zoom
        im = self.pic.resize((round(self.pic.width*zoom),
                              round(self.pic.height*zoom)))
        c2 = self.wh2xy(*c)
        self.picCoord = (self.picCoord[0]-c2[0]+center[0],
                         self.picCoord[1]-c2[1]+center[1])
        self.image = pygame.image.frombuffer(
            im.tobytes(), im.size, im.mode
        )
        Main.refreshZones.append(self.mainrect)

    def drag(self, dx, dy):
        self.picCoord = (self.picCoord[0]+dx, self.picCoord[1]+dy)
        Main.refreshZones.append(self.mainrect)

    def buttonMove(self, dx, dy):
        if dx > 0:
            if self._event_buttonBonus[0] >= 0:
                self.drag(dx+self._event_buttonBonus[0], 0)
                self._event_buttonBonus[0] += dx
            else:
                self._event_buttonBonus[0] = 0
                self.drag(dx, 0)
        elif dx < 0:
            if self._event_buttonBonus[0] <= 0:
                self.drag(dx+self._event_buttonBonus[0], 0)
                self._event_buttonBonus[0] += dx
            else:
                self._event_buttonBonus[0] = 0
                self.drag(dx, 0)
        if dy > 0:
            if self._event_buttonBonus[1] >= 0:
                self.drag(0, dy+self._event_buttonBonus[1])
                self._event_buttonBonus[1] += dy
            else:
                self._event_buttonBonus[1] = 0
                self.drag(0, dy)
        elif dy < 0:
            if self._event_buttonBonus[1] <= 0:
                self.drag(0, dy+self._event_buttonBonus[1])
                self._event_buttonBonus[1] += dy
            else:
                self._event_buttonBonus[1] = 0
                self.drag(0, dy)

    def mouseIn(self, coord):
        return self.mainrect.left < coord[0] < self.mainrect.right\
            and self.mainrect.top < coord[1] < self.mainrect.bottom

    def fit(self):
        self.rezoom(min(self.mainrect.width/self.pic.width,
                    self.mainrect.height/self.pic.height))
        self.picCoord = (0, 0)

    def refresh(self, pic):
        self.pic = pic
        im = self.pic.resize((round(self.pic.width*self.zoom),
                              round(self.pic.height*self.zoom)))
        self.image = pygame.image.frombuffer(
            im.tobytes(), im.size, im.mode
        )
        Main.refreshZones.append(self.mainrect)

    def show(self):
        Main.root.blit(self.image, self.picCoord)

    def procEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in [1, 3] and self.mouseIn(event.pos):
                self._event_active = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self._event_active = False
            self._event_last_block = None
        elif event.type == pygame.WINDOWLEAVE:
            self._event_active = False
            self._event_last_block = None
            for i in self._event_arrowDown:
                self._event_arrowDown[i] = False
        elif event.type == pygame.KEYDOWN:
            if event.key in self._event_arrowDown:
                self._event_arrowDown[event.key] = True
        elif event.type == pygame.KEYUP:
            if event.key in self._event_arrowDown:
                self._event_arrowDown[event.key] = False

    def timelyFunc(self):
        if not self._event_buttonMoveCooldown:
            self._event_buttonMoveCooldown = int(0.02*Main.fps)
            if self._event_arrowDown[pygame.K_UP] and not self._event_arrowDown[pygame.K_DOWN]:
                self.buttonMove(0, -1)
            elif not self._event_arrowDown[pygame.K_UP] and self._event_arrowDown[pygame.K_DOWN]:
                self.buttonMove(0, 1)
            else:
                self._event_buttonBonus[1] = 0
            if self._event_arrowDown[pygame.K_LEFT] and not self._event_arrowDown[pygame.K_RIGHT]:
                self.buttonMove(-1, 0)
            elif not self._event_arrowDown[pygame.K_LEFT] and self._event_arrowDown[pygame.K_RIGHT]:
                self.buttonMove(1, 0)
            else:
                self._event_buttonBonus[0] = 0
        else:
            self._event_buttonMoveCooldown -= 1


class MazeOperator:
    def __init__(self) -> None:
        self.maze = Maze(shape=(40, 40, 2, 1))
        self.maze.generate()
        self.highlights = []
        self.highlights2 = []
        self.monitor = MazeShower(
            visualize(self.maze, highlights=self.highlights, highlights2=self.highlights2, leftoverCoords=(0, 0)))
        Main.eventFuncs.append(self.procEvent)
        self.mode_edit = False
        self.z = 0
        self.w = 0

        self.sidePanel = {
            'b': Button(pygame.Rect(540, 0, 180, 540),
                        text='', color=(0, 0, 127, 127)),
            'title': Button(pygame.Rect(540, 0, 180, 100),
                            'Side\nPanel', color=(0, 0, 0, 0), font=ImageFont.truetype('arial.ttf', 40)),
            'fit': Button(pygame.Rect(540, 100, 180, 40), 'Fit(F)',
                          color=(0, 0, 0, 0), onclick=self.monitor.fit),
            'edit': Button(pygame.Rect(540, 140, 180, 40), 'Edit(E)',
                           color=(0, 0, 0, 0), onclick=self.edit),
            'info': Button(pygame.Rect(540, 180, 180, 40), 'Z:{}/{}, W:{}/{}'.format(
                self.z, self.maze.shape[2]-1, self.w, self.maze.shape[3]-1),
                color=(0, 0, 0, 0)),
            'settings': Button(pygame.Rect(540, 220, 180, 40), 'Settings(S)',
                               color=(0, 0, 0, 0), onclick=lambda: Settings(self), keyCodes=[pygame.K_s]),
            'layer': Button(pygame.Rect(540, 260, 180, 40), 'Layer(I/K/J/L)',
                            color=(0, 0, 0, 0), onclick=lambda: Info('Tools on 3-&4-D Mazes:\nI+/K- on Z axis;\nL+/J- on W axis.'))
        }

    def procEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in [1, 3]:
                if self.mode_edit:
                    _c = self.monitor.xy2wh(*event.pos)
                    if _c is not None:
                        coord = tuple(i//5-1 for i in _c)+(self.z, self.w)
                        self.monitor._event_last_block = coord
                        if self.maze.legalTicker(np.array(coord, np.int32)):
                            self.maze[np.array(coord, np.int32)] = int(
                                event.button == 3)
                            self.refresh()
                elif self.monitor._event_active and event.button == 1:
                    _c = self.monitor.xy2wh(*event.pos)
                    if _c is not None:
                        coord = tuple(i//5-1 for i in _c)+(self.z, self.w)
                        if self.maze.legalTicker(np.array(coord, np.int32)) and self.maze[np.array(coord, np.int32)] == 0:
                            if coord not in self.highlights[-2:]:
                                self.highlights = self.highlights[-1:]+[coord]
                            else:
                                c2 = self.highlights.pop()
                                if c2 != coord:
                                    self.highlights = [c2]
                                elif self.highlights:
                                    self.highlights = [self.highlights[-1]]
                            if len(self.highlights) >= 2:
                                try:
                                    Info('Seeking for path...', confirm=False)
                                    self.highlights2 = self.maze.findpath(
                                        self.highlights[-2], self.highlights[-1])
                                except IndexError:
                                    Info('No possible path!')
                                    self.highlights2 = []
                            else:
                                self.highlights2 = []
                            self.refresh()
            elif event.button == 4:
                self.monitor.rezoom(self.monitor.zoom*1.2,
                                    pygame.mouse.get_pos())
            elif event.button == 5:
                self.monitor.rezoom(self.monitor.zoom/1.2,
                                    pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEMOTION:
            _c = self.monitor.xy2wh(*event.pos)
            if _c is not None and self.monitor._event_active and self.mode_edit:
                if event.buttons in [(1, 0, 0), (0, 0, 1)]:
                    coord = tuple(i//5-1 for i in _c)+(self.z, self.w)
                    if self.monitor._event_last_block != coord:
                        self.monitor._event_last_block = coord
                        if self.maze.legalTicker(np.array(coord, np.int32)):
                            self.maze[np.array(coord, np.int32)] = int(
                                event.buttons == (0, 0, 1))
                            self.refresh()
            elif event.type == pygame.MOUSEMOTION:
                if self.monitor._event_active and not self.mode_edit and event.buttons == (0, 0, 1) and self.monitor.mouseIn(event.pos):
                    self.monitor.drag(*event.rel)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_EQUALS:
                self.monitor.rezoom(self.monitor.zoom*1.2,
                                    pygame.mouse.get_pos())
            elif event.key == pygame.K_MINUS:
                self.monitor.rezoom(self.monitor.zoom/1.2,
                                    pygame.mouse.get_pos())
            elif event.key == pygame.K_f:
                self.monitor.fit()
            elif event.key == pygame.K_e:
                self.edit()
            elif event.key == pygame.K_c:
                if self.mode_edit:
                    self.clear()
            elif event.key == pygame.K_g:
                if self.mode_edit:
                    self.reGenerate()
            elif event.key == pygame.K_i:
                newz = (self.z+1) % self.maze.shape[2]
                if newz != self.z:
                    self.z = newz
                    self.refresh(xzchange=True)
            elif event.key == pygame.K_k:
                newz = (self.z-1) % self.maze.shape[2]
                if newz != self.z:
                    self.z = newz
                    self.refresh(xzchange=True)
            elif event.key == pygame.K_j:
                neww = (self.w-1) % self.maze.shape[3]
                if neww != self.w:
                    self.w = neww
                    self.refresh(xzchange=True)
            elif event.key == pygame.K_l:
                neww = (self.w+1) % self.maze.shape[3]
                if neww != self.w:
                    self.w = neww
                    self.refresh(xzchange=True)

        elif event.type == pygame.DROPFILE:
            try:
                with open(event.file, 'r', encoding='utf-8') as file:
                    shape = list(map(int, file.readline().strip().split()))[
                        ::-1]
                    assert len(shape) == 2
                    l = []
                    for _ in range(shape[1]):
                        l.append(
                            [[[int(i)]] for i in file.readline().strip().split()])
                        assert len(l[-1]) == shape[0]

                l2 = np.array(l, dtype=np.uint8).transpose((1, 0, 2, 3))
                self.maze = Maze(data=l2)
                self.z = 0
                self.w = 0
                self.highlights.clear()
                self.highlights2.clear()
                self.refresh(xzchange=True)
                self.monitor.fit()

            except FileNotFoundError:
                Info('(Error) Cannot find file:\n{}'.format(event.file))
            except OSError:
                Info('(Error) Cannot open file:\n{}'.format(event.file))
            except Exception:
                import time
                import traceback
                with open('log.txt', 'a+', encoding='utf-8') as file:
                    print(time.time(), file=file)
                    print(traceback.format_exc(), file=file)
                Info('(Error) Cannot read file:\n{}\nDetails in log.txt'.format(
                    event.file))

    def refresh(self, xzchange=False):
        if xzchange:
            self.sidePanel['info'].__del__()
            self.sidePanel['info'] = Button(pygame.Rect(540, 180, 180, 40), 'Z:{}/{}, W:{}/{}'.format(
                self.z, self.maze.shape[2]-1, self.w, self.maze.shape[3]-1),
                color=(0, 0, 0, 0))
            Main.refreshZones.append(pygame.Rect(540, 180, 180, 40))
        if self.mode_edit:
            self.monitor.refresh(
                visualize(self.maze, leftoverCoords=(self.z, self.w)))
        else:
            self.monitor.refresh(
                visualize(self.maze, highlights=self.highlights,
                          highlights2=self.highlights2, leftoverCoords=(self.z, self.w)))

    def clear(self):
        self.maze.data.fill(0)
        self.refresh()
        # Main.forceRefresh()

    def reGenerate(self, shape=None):
        if shape == None:
            shape = self.maze.shape
        if shape[0]*shape[1]*shape[2]*shape[3] > 1000:
            Info('Large Maze takes LONG to make!\nPlease wait patiently...', confirm=False)
        self.maze = Maze(shape=shape)
        self.maze.generate()
        self.monitor.refresh(
            visualize(self.maze, leftoverCoords=(self.z, self.w)))
        self.monitor.fit()

    def edit(self):
        self.mode_edit ^= True
        if self.mode_edit:
            self.monitor.refresh(
                visualize(self.maze, leftoverCoords=(self.z, self.w)))
            self.sidePanel['edit'].__del__()
            self.sidePanel['edit'] = Button(pygame.Rect(540, 140, 180, 40), 'PathFind(E)',
                                            color=(0, 0, 0, 0), onclick=self.edit)
            self.sidePanel['generate'] = Button(pygame.Rect(540, 300, 180, 40), 'Generate(G)',
                                                color=(0, 0, 0, 0), onclick=self.reGenerate)
            self.sidePanel['clear'] = Button(pygame.Rect(540, 340, 180, 40), 'Clear(C)',
                                             color=(0, 0, 0, 0), onclick=self.clear)
            Info(
                'EDIT MODE ON!\nLeft click to make path; \nRight Click to make wall;\n+/- to zoom in/out\nArrows to move around.\nYou can also Generate a new maze.')
        else:
            self.highlights.clear()
            self.highlights2.clear()
            self.sidePanel['edit'].__del__()
            self.sidePanel['generate'].__del__()
            self.sidePanel['clear'].__del__()
            self.sidePanel['edit'] = Button(pygame.Rect(540, 140, 180, 40), 'Edit(E)',
                                            color=(0, 0, 0, 0), onclick=self.edit)
            Info(
                'EDIT MODE OFF!\nYou can left click anywhere \n to find path between places;\nRight drag to move around.')


class Info:
    def __init__(self, prompt='prompt here...', confirm=True) -> None:
        self.buttons = [
            Button(pygame.Rect(0, 0, 720, 540), '', color=(0, 0, 0, 127)),
            Button(pygame.Rect(100, 100, 340, 280),
                   'Info:\n{}'.format(prompt), textcolor=(0, 0, 0, 255), color=(255, 127, 127, 255)),
        ]
        if confirm:
            self.buttons.append(Button(pygame.Rect(200, 400, 140, 50), 'Confirm',
                                       onclick=self.end, color=(0, 200, 0, 255), keyCodes=[pygame.K_RETURN, pygame.K_SPACE]))
        self.goloop = True
        self.clock = pygame.time.Clock()
        Main.fullScreenRefresh = True
        if confirm:
            self.loop()
        else:
            Main.display(Main)
            Main.forceRefresh()
        for b in self.buttons:
            # del b
            b.__del__()
        Main.fullScreenRefresh = True
        del self

    def loop(self):
        while self.goloop:
            Main.display(Main)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    Main.forceRefresh()
                self.buttons[-1].procEvent(event)
            self.clock.tick(Main.fps)

    def end(self):
        self.goloop = False


class Settings:
    def __init__(self, o: MazeOperator) -> None:
        self.o = o
        self.shape = list(o.maze.shape)
        self.background = Background()
        self.buttons = [
            Button(pygame.Rect(0, 0, 720, 540), '', color=(0, 0, 0, 100)),
            Button(pygame.Rect(10, 10, 100, 60), 'Settings'),
            Button(pygame.Rect(10, 80, 100, 60), 'Columns'),
            Button(pygame.Rect(10, 150, 100, 60), 'Rows'),
            Button(pygame.Rect(10, 220, 100, 60), 'Z-Coord'),
            Button(pygame.Rect(10, 290, 100, 60), 'W-Coord'),
            Button(pygame.Rect(10, 360, 100, 60),
                   'Discard', onclick=self.end),
            Button(pygame.Rect(120, 360, 100, 60),
                   'Save', onclick=self.save),
        ]

        def _add(i, d):
            def _nf():
                self.shape[i] += d
                if self.shape[i] <= 0:
                    self.shape[i] = 1
                self.buttons[i-4].__del__()
                self.buttons[i-4] = Button(
                    pygame.Rect(120, 80+70*i, 100, 60),
                    str(self.shape[i]), color=(0, 0, 0, 0))
                Main.refreshZones.append(pygame.Rect(120, 80+70*i, 100, 60))
            return _nf
        _dic = [1, 5, 20]
        for i in range(4):
            exec('i{}={}'.format(i, i))
            for j in range(len(_dic)):
                self.buttons.append(Button(
                    pygame.Rect(230+120*j, 80+70*i, 60, 60),
                    '+{}'.format(_dic[j]), color=(0, 0, 0, 0),
                    onclick=_add(i, _dic[j])
                ))
                self.buttons.append(Button(
                    pygame.Rect(290+120*j, 80+70*i, 60, 60),
                    '-{}'.format(_dic[j]), color=(0, 0, 0, 0),
                    onclick=_add(i, -_dic[j])
                ))
        for i in range(4):
            self.buttons.append(Button(
                pygame.Rect(120, 80+70*i, 100, 60),
                str(self.shape[i]), color=(0, 0, 0, 0)
            ))
        self.goloop = True
        self.clock = pygame.time.Clock()
        Main.fullScreenRefresh = True
        self.loop()
        Main.displays.remove(self.background.show)
        del self

    def loop(self):
        while self.goloop:
            Main.display(Main)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    Main.forceRefresh()
                for b in self.buttons:
                    b.procEvent(event)
            self.clock.tick(Main.fps)
        for b in self.buttons:
            # del b
            b.__del__()
        Main.fullScreenRefresh = True

    def end(self):
        self.goloop = False

    def save(self):
        if self.shape[0]*self.shape[1]*self.shape[2]*self.shape[3] > 1000:
            Info('Large Maze takes LONG to make!\nPlease wait patiently...', confirm=False)
        self.o.maze = Maze(shape=self.shape)
        self.o.maze.generate()
        self.o.z = 0
        self.o.w = 0
        self.o.highlights.clear()
        self.o.highlights2.clear()
        self.o.refresh(xzchange=True)
        self.o.monitor.fit()
        # Info('Press R to refresh screen!\n(a bug but don\'t know how to fix it)')
        self.end()


# @debug
def main():
    try:
        m = Main()
        b = Background()
        o = MazeOperator()
        m.mainloop()
    except SystemExit:
        exit(0)
    except Exception as exc:
        import traceback
        import time
        with open('log.txt', 'a+', encoding='utf-8') as file:
            print(time.time(), file=file)
            print(traceback.format_exc(), file=file)
        Info('(FATAL ERROR) {}'.format(exc))


if __name__ == "__main__":
    main()
