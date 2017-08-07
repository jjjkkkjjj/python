import cv2 as cv
import numpy as np
import sys

def corr_timing(video_name):
    video_num = 3
    # keio
    # video_path = ['../data/video/%s' % video_name[i + 1] for i in range(video_num)]
    # output_path = ['../data/video/%s' % video_name[i + 3] for i in range(video_num)]

    # hisamitsu
    video_path = ['../../../../Hisamitsu/%s' % video_name[i + 1] for i in range(video_num)]
    output_path = ['../../../../Hisamitsu/%s' % video_name[i + 4] for i in range(video_num)]

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
    img2 = [np.zeros((height[2], width[2], 3), np.uint8) for i in range(frame_num[2])]

    for i in range(frame_num[0]):
        ret, img0[i] = movie[0].read()
    for j in range(frame_num[1]):
        ret, img1[j] = movie[1].read()
    for k in range(frame_num[2]):
        ret, img2[k] = movie[2].read()

    tmp0 = 0
    tmp1 = 0
    tmp2 = 0
    choice = ord('a')
    while True:
        imgt = cv.hconcat([img0[tmp0], img1[tmp1]])
        img = cv.hconcat([imgt, img2[tmp2]])
        cv.imshow(chr(choice), img)

        key = cv.waitKey()&0xff
        if key == 44:#leftkey
            if choice == ord('l'):
                if tmp0 != 0:
                    tmp0 += -1
            elif choice == ord('c'):
                if tmp1 != 0:
                    tmp1 += -1
            elif choice == ord('r'):
                if tmp2 != 0:
                    tmp2 += -1
            else:
                if tmp0 != 0:
                    tmp0 += -1
                if tmp1 != 0:
                    tmp1 += -1
                if tmp2 != 0:
                    tmp2 += -1

        elif key == 46:#rightkey
            if choice == ord('l'):
                if tmp0 != frame_num[0]-1:
                    tmp0 += 1
            elif choice == ord('c'):
                if tmp1 != frame_num[1]-1:
                    tmp1 += 1
            elif choice == ord('r'):
                if tmp2 != frame_num[2]-1:
                    tmp2 += 1
            else:
                if tmp0 != frame_num[0]-1:
                    tmp0 += 1
                if tmp1 != frame_num[1]-1:
                    tmp1 += 1
                if tmp2 != frame_num[2]-1:
                    tmp2 += 1
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
            elif key == ord('c'):
                cv.destroyWindow(chr(choice))
                choice = ord('c')
            elif key == 13:
                break

    fourcc = cv.VideoWriter_fourcc(*'MPEG')
    out = [cv.VideoWriter(output_path[i], fourcc, frame_rate[i], (width[i], height[i])) for i in range(video_num)]

    min = 999999
    minnum = 0

    if min > tmp0:
        min = tmp0
    if min > tmp1:
        min = tmp1
        minnum = 1
    if min > tmp2:
        minnum = 2

    if minnum == 0:
        for i in range(frame_num[0]):
            out[0].write(img0[i])
        diff_frame = tmp1 -tmp0
        for j in range(frame_num[1]-diff_frame):
            out[1].write(img1[j+diff_frame])
        diff_frame = tmp2 - tmp0
        for k in range(frame_num[2]-diff_frame):
            out[2].write(img2[k+diff_frame])
    elif minnum == 1:
        diff_frame = tmp0 - tmp1
        for i in range(frame_num[0]-diff_frame):
            out[0].write(img0[i+diff_frame])
        for j in range(frame_num[1]):
            out[1].write(img1[j])
        diff_frame = tmp2 - tmp1
        for k in range(frame_num[2]-diff_frame):
            out[2].write(img2[k+diff_frame])
    else:
        diff_frame = tmp0 - tmp2
        for i in range(frame_num[0] - diff_frame):
            out[0].write(img0[i + diff_frame])
        diff_frame = tmp1 - tmp2
        for j in range(frame_num[1]-diff_frame):
            out[1].write(img1[j+diff_frame])
        for k in range(frame_num[2]):
            out[2].write(img2[k])

    for i in range(video_num):
        out[i].release()
        movie[i].release()
    cv.destroyAllWindows()

    return True, "ok"


if __name__ == '__main__':
    arg = sys.argv
    if len(arg) == 7:
        tmp_bool, tmp_name = corr_timing(arg)
        if tmp_bool:
            print("finished")
        else:
            print(tmp_name + " cannot be opened")
    elif len(arg) == 2 and arg[1] == "h":
        print(">: next frame")
        print("<: back frame")
        print("a: operate right,center and left frame")
        print("c: operate center frame only")
        print("r: operate right frame only")
        print("l: operate left frame only")
        print("Enter: save video")
    else:
        print("augument error")
        print("corr_timing.py video1 video2 video3 video1-output video2-output video3-output")
        print("corr_timing.py h -> help")