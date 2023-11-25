from maze import Maze, np


def main():
    try:
        a, b = map(int, input().split())
    except Exception as exc:
        print("Invalid Input!!!")
        return 1
    l = []
    for _ in range(a):
        l.append(list(map(int, input().split())))
    data = np.array(l, dtype=np.uint8)
    m=Maze(data)
    try:
        l2=m.findpath()
        print(''.join([str(i).replace(' ', '') for i in l2]))
    except IndexError:
        print('No possible path!')



if __name__ == "__main__":
    exit(main())
