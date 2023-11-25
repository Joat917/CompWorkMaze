from maze import Maze


def main():
    try:
        a,b=map(int, input().split())
    except Exception as exc:
        print("Invalid Input!!!")
        return 1
    m=Maze(shape=(b,a))
    m.generate()
    print(m)
    return 0

if __name__=="__main__":
    exit(main())
