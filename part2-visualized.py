from maze import Maze, np
from visualize import visualize, Image, ImageDraw


def main():
    try:
        a, b = map(int, input().split())
    except Exception as exc:
        return 1
    l = []
    for _ in range(a):
        l.append(list(map(int, input().split())))
    data = np.array(l, dtype=np.uint8)
    m = Maze(data)
    try:
        l2 = m.findpath()
        im = visualize(m, highlights=l2)
        im.show()
        s = input('Save the image as ')
        im.save(s)
    except IndexError:
        im = Image.new('RGB', (100, 12), 'white')
        ImageDraw.Draw(im).text((0, 0), 'No possible path!', (255, 0, 0))
        im.show()
    return 0


if __name__ == "__main__":
    exit(main())
