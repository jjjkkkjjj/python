import cv2 as cv
import numpy as np
import sys

def corr_timing(video_name):
    video_num = len(video_name) - 2
    # keio
    #video_path = ['../data/video/%s' % video_name[i + 1] for i in range(video_num)]
    #output_path = ['../data/video/%s' % video_name[i + 3] for i in range(video_num)]

    # hisamitsu
    video_path = ['../../../Hisamitsu/%s' % video_name[i + 2] for i in range(video_num)]
    output_path = [video_name[1] for i in range(video_num)]
    for i in range(video_num):
        tmp_name = video_name[i + 2].split("/")
        output_path[i] += tmp_name[len(tmp_name)-1][:tmp_name[len(tmp_name)-1].index('.')] + '.MP4'

    # initialization
    movie = [cv.VideoCapture(video_path[i]) for i in range(video_num)]
    frame_num = [0 for i in range(video_num)]
    frame_rate = [0 for i in range(video_num)]
    height = [0 for i in range(video_num)]
    width = [0 for i in range(video_num)]
    MAX_FRAMENUM = 0
    HEIGHT = 720
    WIDTH = 1280

    for i in range(video_num):
        if movie[i].isOpened() != True:
            return False, video_name[i + 2]
        frame_num[i] = int(movie[i].get(7))
        if frame_num[i] > MAX_FRAMENUM:
            MAX_FRAMENUM = frame_num[i]
        frame_rate[i] = movie[i].get(5)
        height[i] = int(movie[i].get(4))
        width[i] = int(movie[i].get(3))

    img = []
    div = int((video_num + 2) / 3)
    for i in range(video_num):
        img.append([np.zeros((height[i], width[i], 3), np.uint8) for j in range(frame_num[i])])
        for k in range(frame_num[i]):
            ret, img[i][k] = movie[i].read()
            img[i][k] = cv.resize(img[i][k], (int(WIDTH / 3), int(HEIGHT / div)))
    tmp = [0 for i in range(video_num)]
    while len(img)%3 != 0:
        img.append([np.zeros((int(HEIGHT / div), int(WIDTH / 3), 3), np.uint8)])
        tmp.append(0)

    #confirm here

    choice = ord('a')
    ASCii = [ord(str(i)) for i in range(video_num)]
    while True:
        himg = [np.zeros((int(WIDTH/3), int(HEIGHT), 3), np.uint8) for i in range(div)]
        for i in range(div):
            himg_tmp = cv.hconcat([img[i*3][tmp[i*3]], img[i*3 + 1][tmp[i*3 + 1]]])
            himg[i] = cv.hconcat([himg_tmp, img[i*3 + 2][tmp[i*3 + 2]]])
            if i == 0:
                show_img = himg[0].copy()
                continue
            else:
                show_img = cv.vconcat([show_img, himg[i]])

        cv.imshow(chr(choice), show_img)
        key = cv.waitKey()&0xff
        if key == 44:#leftkey
            try:
                INdex_l = ASCii.index(choice)
                if tmp[INdex_l] != 0:
                    tmp[INdex_l] += -1
            except ValueError:
                if choice == ord('a'):
                    for i in range(video_num):
                        if tmp[i] != 0:
                            tmp[i] += -1
        elif key == 46:#rightkey
            try:
                INdex_r = ASCii.index(choice)
                if tmp[INdex_r] != frame_num[INdex_r] - 1:
                    tmp[INdex_r] += 1
            except ValueError:
                if choice == ord('a'):
                    for i in range(video_num):
                        if tmp[i] != frame_num[i] - 1:
                            tmp[i] += 1
        else:
            if key == ord('a'):
                cv.destroyWindow(chr(choice))
                choice = ord('a')
            elif key == 13:
                break
            else:
                try:
                    INdex = ASCii.index(key)
                    cv.destroyWindow(chr(choice))
                    choice = ord(str(INdex))
                except ValueError:
                    continue

    fourcc = cv.VideoWriter_fourcc(*'MPEG')
    out = [cv.VideoWriter(output_path[i], fourcc, frame_rate[i], (int(width[i]), int(height[i]))) for i in range(video_num)]

    del tmp[video_num:]
    MIN = tmp.index(min(tmp))
    for i in range(video_num):
        diff_frame = tmp[i] - tmp[MIN]
        TMP = 0
        movie[i].set(1, diff_frame)
        while TMP < frame_num[i] - diff_frame:
            ret, TMP_img = movie[i].read()
            out[i].write(TMP_img)
            TMP += 1

    for i in range(video_num):
        out[i].release()
        movie[i].release()
    cv.destroyAllWindows()

    return True, "ok"


if __name__ == '__main__':
    arg = sys.argv
    if len(arg) > 3:
        tmp_bool, tmp_name = corr_timing(arg)
        if tmp_bool:
            print("finished")
        else:
            print(tmp_name + " cannot be opened")
    elif len(arg) == 2 and arg[1] == "h":
        print(">: next frame")
        print("<: back frame")
        print("a: operate all videos")
        print("video number: operate [number]-th video only")
        print("example 4: operate 4th video only")
        print("n: choose next digit")
        print("Enter: save video")
    else:
        print("augument error")
        print("corr_timing_plural.py output-path video1 video2 ...")
        print("corr_timing_plural.py h -> help")