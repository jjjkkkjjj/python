import cv2 as cv
import numpy as np
import sys

def connect_video(output_path, video):
    video_num = len(video)-2
    # keio
    # video_path = ['../data/video/%s' % video[i + 2] for i in range(video_num)]

    # hisamitsu
    video_path = ['../../../../Hisamitsu/%s' % video[i + 2] for i in range(video_num)]

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

    div = int((video_num + 1)/2)
    tmp = 0

    while tmp < frame_num:

        himg = [np.zeros((int(width/2), int(height), 3), np.uint8) for i in range(div)]
        for i in range(div):
            ret0, img0 = movie[i*2].read()
            img0 = cv.resize(img0, (int(width / 2), int(height/div)))

            if i*2+1 == video_num:
                img1 = np.zeros((int(height/div), int(width/2), 3), np.uint8)
            else:
                ret1, img1 = movie[i*2 + 1].read()
                img1 = cv.resize(img1, (int(width / 2), int(height/div)))

            himg[i] = cv.hconcat([img0, img1])

            if i == 0:
                output_img = himg[0].copy()
                continue
            else:
                output_img = cv.vconcat([output_img, himg[i]])

        out.write(output_img)
        tmp += 1

    out.release()
    for i in range(video_num):
        movie[i].release()
    return True, "ok"

if __name__ == '__main__':
    arg = sys.argv
    if len(arg) > 3:
        tmp_bool, tmp_name = connect_video(arg[1], arg)
        if tmp_bool:
            print("finished")
        else:
            print(tmp_name + " cannot be opened")

    else:
        print("augument error")
        print ("connect_video.py output_path video_name1 video_name2 ...")