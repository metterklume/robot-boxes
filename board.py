"""
Created on Sun Mar 25 14:30:00 2023

@author: abhishekroy
"""
from copy import copy
from dataclasses import dataclass
from typing import List, Tuple, Set, Optional, Literal
import numpy as np

Line = Tuple[int,int,int,int]
Box = Tuple[int,int]

@dataclass
class Board:
    """
    Data describing the state of a square board at some stage in the game. 

    size  --> number of boxes in each row and column. Total boxes = size*size
    lines --> lines on the board. each line (i,j,r,s) goes from (i,j) to (r,s)
              IMPORTANT: ensure that i<=j and r<=s so lines go rightwards
                         and upwards
    red_boxes  --> Boxes made by the red player (moves first)
    blue_boxes --> Boxes made by the blue player (moves second)
    """
    size: int
    
    lines: List[Line]  
    red_boxes: Optional[List[Box]] = None
    blue_boxes: Optional[List[Box]] = None

    def __post_init__(self):
        self.lines = [] if self.lines is None else self.lines
        self.red_boxes = [] if self.red_boxes is None else self.red_boxes
        self.blue_boxes = [] if self.blue_boxes is None else self.blue_boxes

    def __copy__(self):
        return Board(size=self.size,lines=copy(self.lines),red_boxes=copy(self.red_boxes),
                     blue_boxes=self.blue_boxes)


def getboxes(board:Board)->List[Box]:
    """
    Returns list of the bottom-left corners of all filled boxes.  
    """
    lines = board.lines
    boxes = []
    for i in range(board.size):
        for j in range(board.size):
            if (i,j,i+1,j) in lines and\
               (i,j+1,i+1,j+1) in lines and\
               (i,j,i,j+1) in lines and\
               (i+1,j,i+1,j+1) in lines:
                boxes.append((i,j)) 
               
    return boxes


def countboxes(board:Board)->int:
    """
    Returns number of filled boxes on the board.
    """
    return len(getboxes(board))


def isboxfilled(board:Board, box:Box)->bool:
    """
    Given the bottom-left corner of a box, check if it is filled (all lines are 
    on the board).
    """
    lines = board.lines
    i,j = box
    return (i,j,i+1,j) in lines and (i,j+1,i+1,j+1) in lines and\
            (i,j,i,j+1) in lines and (i+1,j,i+1,j+1) in lines


def getnewboxes(lines:List[Line], line:Line)->List[Box]:
    """
    Returns list of NEW boxes created by adding one NEW *line* to the *lines* 
    that have already been drawn. 
    Boxes are denoted by the bottom-left corner.
    """
    if line in lines:
        return []

    i,j,r,s = line

    above = [(i,j+1,i+1,j+1), (i,j,i,j+1), (i+1,j,i+1,j+1)]
    below = [(i,j-1,i,j), (i,j-1,i+1,j-1), (i+1,j-1,i+1,j)]
    right = [(i,j+1,i+1,j+1), (i,j,i+1,j), (i+1,j,i+1,j+1)]
    left  = [(i-1,j,i,j), (i-1,j,i-1,j+1), (i-1,j+1,i,j+1)]
    
    options = ()
    if r-i == 1:
        options = ((above, (i,j)), 
                   (below, (i,j-1)))
    elif s-j == 1:
        options = ((right, (i,j)),
                   (left,  (i-1,j))) 

    newboxes = [box for (remaining, box) in options if all((l in lines for l in remaining))]
    return newboxes


def isvalidboard(board:Board)->bool:
    """
    Check if the lines and red/blue boxes on the board are valid.
    """
    n = board.size
    valid = all((
                0<=i<=n and 0<=j<=n and 0<=r<=n and 0<=s<=n and\
                abs(i-j)+abs(r-s) == 1 \
                    for (i,j,r,s) in board.lines
                ))
    
    if board.red_boxes and board.blue_boxes:
        boxes = set(getboxes(board))
        valid = valid and all((b in boxes for b in board.red_boxes)) and\
                          all((b in boxes for b in board.blue_boxes)) and\
                          len(boxes) == len(board.red_boxes) + len(board.blue_boxes)
    return valid


def isvalidmove(board:Board, move:List[Line])->bool:
    """
    Checks validity of a move. A move is a list of lines made a player
    in his/her turn.

    If a line creates a filled box then there must a next line and so on, 
    until either no box is created or the game ends.
    """
    n = board.size
    #A move is empty iff there are no more lines to made
    if not move and len(board.lines) < 2*n*(n+1):
        return False
    #No repeated lines 
    if any((line in board.lines for line in move)) or\
        len(set(move)) != len(move):
            return False
    
    #Each of the lines in the move before the last one, must add a new box
    total_lines = list(board.lines) + move
    for i in range(len(board.lines), len(total_lines)-1):
        if not getnewboxes(total_lines[:i], total_lines[i]):
            return False
    
    #The last line must either:
    #   1. Be the last line of the game
    #   2. NOT create a new box
    if len(total_lines) < 2*n*(n+1) and getnewboxes(total_lines[:-1], move[-1]):
        return False
    
    return True


def makemove(board:Board, move:List[Line], player:Literal[0,1], 
             copyboard=True, checkmove=True)->Board:
    """
    Make a move i.e. add its line(s) to the board.
    Returns a new board or changes board directly based on *copyboard*.
    """
    if copyboard:
        board = copy(board)
    if checkmove and not isvalidmove(board, move):
        print(f"Invalid {move} for {board}")
        return board
    
    old_boxes = getboxes(board)
    board.lines += move
    new_boxes = getboxes(board)
    added_boxes = [b for b in new_boxes if b not in old_boxes]
    if player == "red":
        board.red_boxes += added_boxes
    else:
        board.blue_boxes += added_boxes
    
    return board


def get_all_lines(n:int)->List[Line]:
    """
    Returns list of all 2n(n+1) lines possible on an n X n board.
    """
    all_lines = [(i,j,i+1,j) for i in range(n) for j in range(n)]
    all_lines += [(i,j,i,j+1) for i in range(n) for j in range(n)]
    all_lines += [(n,i,n,i+1) for i in range(n)]
    all_lines += [(i,n,i+1,n) for i in range(n)]
    
    all_lines = [(min(i,r),min(j,s),max(i,r),max(j,s)) for (i,j,r,s) in all_lines]
    return all_lines
