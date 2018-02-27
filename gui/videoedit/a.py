import cv2


def video(path="/Users/junkadonosuke/Desktop/baseball/video/2-24/C0357.MP4"):
    video = cv2.VideoCapture(path)

    while video.isOpened():
        ret, frame = video.read()

        cv2.imshow("a", frame)
        cv2.waitKey(30)

    return

if __name__ == '__main__':
    video()