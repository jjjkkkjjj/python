import cv2
import numpy as np
import glob
import sys

class crop:
    def __init__(self, dirpath, extension, rewrite=False, width=300, height=400):
        self.dirpath = dirpath
        self.extension = extension
        self.imgspath = sorted(glob.glob('{0}/*.{1}'.format(dirpath, extension)))
        self.rewrite = rewrite

        self.__rect = None
        self.__sx = 0
        self.__sy = 0
        self.__abs_x = 0
        self.__abs_y = 0
        self.__abs_sx = 0
        self.__abs_sy = 0
        self.__img_win = None
        self.__img = None
        self.__cropped = False
        self.__resize = (width, height)

    def set_cropsize(self):
        if len(self.imgspath) == 0:
            raise ValueError('path:{0} or extension:{1} you designated was invalid'.format(self.dirpath, self.extension))
        else:
            self.__img = cv2.imread(self.imgspath[0])
            self.__img = cv2.resize(self.__img, self.__resize)
            self.__rect = (0, 0, self.__img.shape[1], self.__img.shape[0])
            self.__img_win = self.__img.copy()

            cv2.namedWindow("cropping", cv2.WINDOW_NORMAL)
            cv2.setMouseCallback("cropping", self.__callback)

            while True:
                cv2.imshow("cropping", self.__img_win)
                k = cv2.waitKey(1)

                if k == ord('f'):
                    break

                if k == ord("r"):
                    self.__rect = (0, 0, self.__img.shape[1], self.__img.shape[0])
                    self.__img_win = self.__img.copy()

                if k == ord("q"):
                    exit()

            cv2.destroyAllWindows()

            self.yini = self.__rect[1]
            self.yfin = self.__rect[1] + self.__rect[3]
            self.xini = self.__rect[0]
            self.xfin = self.__rect[0] + self.__rect[2]

    def save(self):
        for imgpath in self.imgspath:
            img = cv2.imread(imgpath)
            img = cv2.resize(img, self.__resize)
            if self.rewrite:
                cv2.imwrite(imgpath, img[self.yini:self.yfin, self.xini:self.xfin])
            else:
                name = imgpath.split('/')[-1]
                cv2.imwrite('{0}/rewrite-{1}.{2}'.format(self.dirpath, name, self.extension), img[self.yini:self.yfin, self.xini:self.xfin])


    def __callback(self, event, x, y, flags, param):
        self.__abs_x, self.__abs_y = self.__rect[0] + x, self.__rect[1] + y
    
        if event == cv2.EVENT_LBUTTONDOWN:
            self.__sx, self.__sy = x, y
            self.__abs_sx, self.__abs_sy = self.__abs_x, self.__abs_y
        
            if flags == cv2.EVENT_FLAG_LBUTTON:
                self.__img_win = self.__img.copy()[self.__rect[1]:self.__rect[1] + self.__rect[3], self.__rect[0]:self.__rect[0] + self.__rect[2]]
                cv2.rectangle(self.__img_win, (self.__sx, self.__sy), (x, y), (255, 0, 0), 2)

        if event == cv2.EVENT_LBUTTONUP:
            rect_x = np.clip(min(self.__abs_sx, self.__abs_x), 0, self.__img.shape[1] - 2)
            rect_y = np.clip(min(self.__abs_sy, self.__abs_y), 0, self.__img.shape[0] - 2)
            rect_w = np.clip(abs(self.__abs_sx - self.__abs_x), 1, self.__img.shape[1] - rect_x)
            rect_h = np.clip(abs(self.__abs_sy - self.__abs_y), 1, self.__img.shape[0] - rect_y)
            self.__rect = (rect_x, rect_y, rect_w, rect_h)
            self.__img_win = self.__img.copy()[self.__rect[1]:self.__rect[1] + self.__rect[3], self.__rect[0]:self.__rect[0] + self.__rect[2]]


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 3:
        print '2 argument must be needed at least'
    else:
        trim = crop(args[1], args[2])
        trim.set_cropsize()
        trim.save()
