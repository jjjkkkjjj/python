import cv2 as cv
import numpy as np
import sys

def overlay_video(output_path, video):
    video_num = len(video)-2

    #keio
    video_path = ['../data/video/%s' % video[i + 2] for i in range(video_num)]

    #hisamitsu
    #video_path = ['../../../../Hisamitsu/%s' % video[i + 2] for i in range(video_num)]

    # initialization
    movie = [cv.VideoCapture(video_path[i]) for i in range(video_num)]
    frame_num = 99999
    frame_rate = 0
    for i in range(video_num):
        if movie[i].isOpened() != True:
            return False, video[i + 2]
        if frame_num > movie[i].get(7):
            frame_num = movie[i].get(7)
            frame_rate = movie[i].get(5)

    height = 720
    width = 1280

    fourcc = cv.VideoWriter_fourcc(*'MPEG')
    out = cv.VideoWriter(output_path, fourcc, frame_rate, (width, height))

    tmp = 0

    while tmp < frame_num:
        img = [np.zeros((height, width, 3), np.uint8) for i in range(video_num)]
        for i in range(video_num):
            ret, img[i] = movie[i].read()
            img[i] = cv.resize(img[i], (width, height))

        output_img = img[0].copy()

        for i in range(video_num - 1):
            output_img = cv.addWeighted(output_img, float(i+1)/(i+2), img[i + 1], float(1)/(i+2), 0.0)

        out.write(output_img)
        tmp += 1

    out.release()
    for i in range(video_num):
        movie[i].release()
    return True, "ok"


if __name__ == '__main__':
    arg = sys.argv
    if len(arg) > 3:
        tmp_bool, tmp_name = overlay_video(arg[1], arg)
        if tmp_bool:
            print("finished")
        else:
            print(tmp_name + " cannot be opened")

    else:
        print("augument error")
        print ("overlay_video.py output_path video_name1 video_name2 ...")