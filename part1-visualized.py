from maze import Maze
from visualize import visualize


def main():
    try:
        a,b=map(int, input().split())
    except Exception as exc:
        print("Invalid Input!!!")
        return 1
    m=Maze(shape=(b,a))
    m.generate()
    im=visualize(m)
    im.show()
    s=input('Save the image as ')
    im.save(s)
    return 0

if __name__=="__main__":
    exit(main())
        