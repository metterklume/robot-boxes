"""
Created on Sun Mar 25 14:30:00 2023

@author: abhishekroy
"""

from matplotlib.patches import Circle, Rectangle
from matplotlib.lines import Line2D
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import io
import PIL.Image as Image

from board import isboxfilled

def drawboard(board,size=4):
    '''Draw a board. Requires matplotlib and PIL'''
    fig, ax = plt.subplots()

    fig.set_size_inches(size,size)
    ax.set_ylim(-1.2, 0.2)
    ax.set_xlim(-1.2, 0.2)
    ax.set_aspect('equal')
    ax.set_axis_off()

    patches = []

    ox, oy = (-1,-1)
    n = board.size
    cr = 0.01
    patches = []

    for (i,j,r,s) in board.lines:
        x,y,xx,yy = ox+i/n, oy+j/n, ox+r/n, oy+s/n
        ax.add_artist(Line2D([x, xx], [y, yy],color=(0.1,0.1,0.1,0.8)))

    for i in range(n+1):
        for j in range(n+1):
            center = (ox+i/n, oy+j/n)
            circle = Circle(center, cr)
            circle.set_color([0,0,0,1])
            patches.append(circle)

    for i in range(n):
        for j in range(n):
            if isboxfilled(board, (i,j)):
                if (i,j) in board.red_boxes:
                    color = (1,0,0,0.5)
                elif (i,j) in board.blue_boxes:
                    color = (0,0,1,0.5)
                else:
                    color = (0,0,0,0.5)
                rect = Rectangle((ox+i/n+0.1/n, oy+j/n+0.1/n), 0.8/n, 0.8/n,color=color)
                patches.append(rect)

    for i in range(n+1):
        for center in [(ox+i/n,oy-0.1), (ox-0.1,oy+i/n)]:
            ax.annotate(str(i), center, fontsize=12, ha='center',va='center',
                    weight="light")

    p = PatchCollection(patches, match_original=True)
    ax.add_collection(p)

    buf = io.BytesIO()
    fig.savefig(buf, format='png',bbox_inches='tight')
    buf.seek(0)
    im = Image.open(buf)
    plt.close(fig) #don't display image
    return im
