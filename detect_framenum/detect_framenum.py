import cv2 as cv
import numpy as np
import sys

def detect_releasepoint(video_name):
    filename_input = '/Users/junkadonosuke/Desktop/研究/共同研究/慶応大/データ/%s' % video_name
    release_frame = -1

    # initialization
    movie = cv.VideoCapture(filename_input)
    if movie.isOpened() != True:
        return release_frame
    frame_num = int(movie.get(7))
    frame_rate = movie.get(5)
    height = int(movie.get(4))
    width = int(movie.get(3))

    img = [np.zeros((height, width, 3), np.uint8) for i in range(frame_num)]

    for i in range(frame_num):
        ret, img[i] = movie.read()

    tmp = 0

    while True:
        cv.imshow(video_name, img[tmp])

        key = cv.waitKey()&0xff
        if key == 44:  # leftkey
            if tmp != 0:
                tmp += -1

        elif key == 46:  # rightkey
            if tmp != frame_num - 1:
                tmp += 1

        elif key == 13:
                break

    release_frame = tmp

    return release_frame

if __name__ == '__main__':
    arg = sys.argv
    if len(arg) == 2:
        tmp = detect_releasepoint(arg[1])
        if tmp == -1:
            print (arg[1] + " cannot be opened")
        else:
            print ("release frame is " + str(tmp))
    else:
        print("augument error")
        print ("detect_framenum.py video_name")
