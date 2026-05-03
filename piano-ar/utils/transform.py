import cv2
import numpy as np

WIDTH = 800
HEIGHT = 200

def get_matrix(points):
    src = np.float32(points)
    dst = np.float32([
        [0, 0],
        [WIDTH, 0],
        [WIDTH, HEIGHT],
        [0, HEIGHT]
    ])
    
    return cv2.getPerspectiveTransform(src, dst)

def warp(frame, matrix):
    return cv2.warpPerspective(frame, matrix, (WIDTH, HEIGHT))