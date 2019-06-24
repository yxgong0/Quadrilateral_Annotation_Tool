from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import QBasicTimer

import cv2
import os


class Annotator:
    def __init__(self, annotations, contents, input_paths, output_path, delete_images, save_images, progress_bar):
        super(Annotator, self).__init__()
        self.annotations = annotations
        self.contents = contents
        self.input_paths = input_paths
        self.output_path = output_path + '/'
        self.delete_images = delete_images
        self.save_images = save_images
        self.progress_bar = progress_bar

        assert annotations.__len__() == contents.__len__()
        assert annotations.__len__() == input_paths.__len__()

        try:
            os.makedirs(output_path)
        except OSError:
            pass

    def annotate(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(self.annotations.__len__())
        for i in range(self.annotations.__len__()):
            self.progress_bar.setValue(i)
            annotation = self.annotations[i]
            content = self.contents[i]
            input_path = self.input_paths[i]

            items = input_path.split('/')
            if items.__len__() == 1:
                items = input_path.split('\\')
            image_name = items[-1]
            items_ = image_name.split('.')
            txt_name = items_[0]
            for j in range(1, items_.__len__() - 1, 1):
                txt_name += '.' + items_[j]
            txt_name += '.txt'

            gt = open(self.output_path + txt_name, 'w+')
            for j in range(annotation.__len__()):
                pixel = annotation[j]
                c = content[j]
                pixels_x = pixel[0]
                pixels_y = pixel[1]
                assert pixels_x.__len__() == pixels_y.__len__()
                gt.write(str(round(pixels_x[0])) + ' ' + str(round(pixels_y[0])) + ' ' +
                         str(round(pixels_x[1])) + ' ' + str(round(pixels_y[1])) + ' ' +
                         str(round(pixels_x[2])) + ' ' + str(round(pixels_y[2])) + ' ' +
                         str(round(pixels_x[3])) + ' ' + str(round(pixels_y[3])) + ' ' + c + '\n')

            gt.close()
            if self.save_images:
                image = cv2.imread(input_path)
                cv2.imwrite(self.output_path + image_name, image)
            if self.delete_images:
                os.remove(input_path)
        self.progress_bar.setVisible(False)