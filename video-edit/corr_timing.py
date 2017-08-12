import cv2 as cv
import numpy as np
import sys

def corr_timing(video_name):
    video_num = 2
    # keio
    #video_path = ['../data/video/%s' % video_name[i + 1] for i in range(video_num)]
    #output_path = ['../data/video/%s' % video_name[i + 3] for i in range(video_num)]

    # hisamitsu
    video_path = ['../../../Hisamitsu/%s' % video_name[i + 1] for i in range(video_num)]
    output_path = ['../../../Hisamitsu/%s' % video_name[i + 3] for i in range(video_num)]

    # initialization
    movie = [cv.VideoCapture(video_path[i]) for i in range(video_num)]
    frame_num = [0 for i in range(video_num)]
    frame_rate = [0 for i in range(video_num)]
    height = [0 for i in range(video_num)]
    width = [0 for i in range(video_num)]

    for i in range(video_num):
        if movie[i].isOpened() != True:
            return False, video_name[i + 1]
        frame_num[i] = int(movie[i].get(7))
        frame_rate[i] = movie[i].get(5)
        height[i] = int(movie[i].get(4))
        width[i] = int(movie[i].get(3))

    img0 = [np.zeros((height[0], width[0], 3), np.uint8) for i in range(frame_num[0])]
    img1 = [np.zeros((height[1], width[1], 3), np.uint8) for i in range(frame_num[1])]

    for i in range(frame_num[0]):
        ret, img0[i] = movie[0].read()
    for j in range(frame_num[1]):
        ret, img1[j] = movie[1].read()

    tmp0 = 0
    tmp1 =0
    choice = ord('a')
    while True:
        img = cv.hconcat([img0[tmp0], img1[tmp1]])
        cv.imshow(chr(choice), img)

        key = cv.waitKey()&0xff
        if key == 44:#leftkey
            if choice == ord('l'):
                if tmp0 != 0:
                    tmp0 += -1
            elif choice == ord('r'):
                if tmp1 != 0:
                    tmp1 += -1
            else:
                if tmp0 != 0:
                    tmp0 += -1
                if tmp1 != 0:
                    tmp1 += -1

        elif key == 46:#rightkey
            if choice == ord('l'):
                if tmp0 != frame_num[0]-1:
                    tmp0 += 1
            elif choice == ord('r'):
                if tmp1 != frame_num[1]-1:
                    tmp1 += 1
            else:
                if tmp0 != frame_num[0]-1:
                    tmp0 += 1
                if tmp1 != frame_num[1]-1:
                    tmp1 += 1
        else:
            if key == ord('a'):
                cv.destroyWindow(chr(choice))
                choice = ord('a')
            elif key == ord('l'):
                cv.destroyWindow(chr(choice))
                choice = ord('l')
            elif key == ord('r'):
                cv.destroyWindow(chr(choice))
                choice = ord('r')
            elif key == 13:
                break

    fourcc = cv.VideoWriter_fourcc(*'MPEG')
    out = [cv.VideoWriter(output_path[i], fourcc, frame_rate[i], (width[i], height[i])) for i in range(video_num)]

    diff_frame = tmp1 - tmp0
    if diff_frame > 0:
        for i in range(frame_num[0]):
            out[0].write(img0[i])
        for j in range(frame_num[1]-diff_frame):
            out[1].write(img1[j+diff_frame])
    else:
        diff_frame = -diff_frame
        for i in range(frame_num[0]-diff_frame):
            out[0].write(img0[i+diff_frame])
        for j in range(frame_num[1]):
            out[1].write(img1[j])

    for i in range(video_num):
        out[i].release()
        movie[i].release()
    cv.destroyAllWindows()

    return True, "ok"


if __name__ == '__main__':
    arg = sys.argv
    if len(arg) == 5:
        tmp_bool, tmp_name = corr_timing(arg)
        if tmp_bool:
            print("finished")
        else:
            print(tmp_name + " cannot be opened")
    elif len(arg) == 2 and arg[1] == "h":
        print(">: next frame")
        print("<: back frame")
        print("a: operate right and left frame")
        print("r: operate right frame only")
        print("l: operate left frame only")
        print("Enter: save video")
    else:
        print("augument error")
        print("corr_timing.py video1 video2 video1-output video2-output")
        print("corr_timing.py h -> help")