from PIL import Image, ImageDraw
import numpy as np

BLOCK_SIZE = np.array([5, 5], dtype=np.int32)


def visualize(m, road=(255, 255, 255, 255), wall=(0, 0, 255, 255), border=(255, 0, 0, 255),
              highlights=[], highlightColor=(127, 255, 127, 255),
              highlights2=[], highlight2Color=(255, 127, 255, 255),
              highlights3=[], highlight3Color=(255, 200, 127, 255), leftoverCoords=()):
    assert m.dimension == 2+len(leftoverCoords), '{} Not a {}-dimensional maze grid!'.format(m.dimension, 2+len(leftoverCoords))
    if m.dimension != 2:
        grid = m.data[(slice(None, None, None), slice(
            None, None, None),)+leftoverCoords]
    else:
        grid = m.data
    im = Image.new('RGBA', tuple(BLOCK_SIZE*m.shape[:2]+BLOCK_SIZE*2), border)
    imd = ImageDraw.Draw(im)
    for row in range(m.shape[1]):
        for col in range(m.shape[0]):
            if (col, row)+leftoverCoords in highlights:
                imd.rectangle((tuple(BLOCK_SIZE*(1+col, 1+row)),
                              tuple(BLOCK_SIZE*(2+col, 2+row))), highlightColor)
            elif (col, row)+leftoverCoords in highlights2:
                imd.rectangle((tuple(BLOCK_SIZE*(1+col, 1+row)),
                              tuple(BLOCK_SIZE*(2+col, 2+row))), highlight2Color)
            elif (col, row)+leftoverCoords in highlights3:
                imd.rectangle((tuple(BLOCK_SIZE*(1+col, 1+row)),
                              tuple(BLOCK_SIZE*(2+col, 2+row))), highlight3Color)
            elif grid[col, row]:
                imd.rectangle((tuple(BLOCK_SIZE*(1+col, 1+row)),
                              tuple(BLOCK_SIZE*(2+col, 2+row))), wall)
            else:
                imd.rectangle((tuple(BLOCK_SIZE*(1+col, 1+row)),
                              tuple(BLOCK_SIZE*(2+col, 2+row))), road)
    return im


if __name__ == "__main__":
    from maze import Maze
    m = Maze(shape=(100, 100))
    m.generate()
    path = m.findpath()
    visualize(m, highlights=path).show()
