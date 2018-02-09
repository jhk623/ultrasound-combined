import cv2
import numpy as np
from math import sin,cos,radians, degrees, pi

def read():
    f = open("./input/test.txt", 'r')
    output_list = []
    aaa = f.readlines()

    for i in range(len(aaa)):
        testfilename = aaa[i]
        if testfilename[-1] == "\n":
            testfilename = testfilename[:-1]
        testfile = open("./output/text/" + testfilename +  ".txt")
        testfile.readline()
        angle = testfile.readline()
        angle = float(angle[:-1])
        rad = angle

        xy = testfile.readline()
        xy = xy.split(' ')
        xmin = int(xy[0])
        ymin = int(xy[1])
        xmax = int(xy[2])
        ymax = int(xy[3])
        xc = int((xmin + xmax)/2)
        yc = int((ymin + ymax)/2)

        xm = xmin - xc
        ym = ymin - yc
        xM = xmax - xc
        yM = ymax - yc
 
        x1rot = xm * cos(rad) + ym * sin(rad)
        y1rot = xm * sin(rad) - ym * cos(rad)
        x2rot = xm * cos(rad) + yM * sin(rad)
        y2rot = xm * sin(rad) - yM * cos(rad)
        x3rot = xM * cos(rad) + yM * sin(rad)
        y3rot = xM * sin(rad) - yM * cos(rad)
        x4rot = xM * cos(rad) + ym * sin(rad)
        y4rot = xM * sin(rad) - ym * cos(rad)

        x1 = int(x1rot + xc)
        y1 = int(y1rot + yc)
        x2 = int(x2rot + xc)
        y2 = int(y2rot + yc)
        x3 = int(x3rot + xc)
        y3 = int(y3rot + yc)
        x4 = int(x4rot + xc)
        y4 = int(y4rot + yc)

        xlist = [x1,x2,x3,x4]
        ylist = [y1,y2,y3,y4]
        pts = [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]
        xmax123 = pts[xlist.index(max(x1,x2,x3,x4))]
        ymax123 = pts[ylist.index(max(y1,y2,y3,y4))]
        ymin123 = pts[ylist.index(min(y1,y2,y3,y4))]
        output_list.append((rad, xmax123, ymax123, ymin123))

    return output_list

read()

