import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
import cv2
import numpy as np
from utils import *
from annotation import Annotator


class QLabelWithClick(QLabel):
    def __init__(self, parent=None):
        super(QLabelWithClick, self).__init__(parent)
        self.setAlignment(QtCore.Qt.AlignTop)

        self.pixel_x = -1
        self.pixel_y = -1
        self.pixels_x = []
        self.pixels_y = []
        self.ratios_x = []
        self.ratios_y = []
        self.point_number = 0

        self.pixels = []
        self.ratios = []

        self.enabler = False
        self.hold = False

        self.window_geometry = (100, 100, 800, 600)
        self.first_click = False

        # self.finetune_window = FinetuneWindow(self.window_geometry)
        self.finetune_window = None

        self.image_path = ''
        self.cv_image = None

        self.new_width = -1
        self.new_height = -1

        self.contents = []

    def set_finetune_window(self, finetune_window):
        self.finetune_window = finetune_window

    def initilize(self):
        self.pixel_x = -1
        self.pixel_y = -1
        self.pixels_x = []
        self.pixels_y = []
        self.ratios_x = []
        self.ratios_y = []
        self.point_number = 0
        self.pixels = []
        self.ratios = []
        self.enabler = False
        self.hold = False
        # self.finetune_window = None
        self.first_click = False
        self.image_path = ''
        self.cv_image = None
        self.contents = []

    def get_annotation(self):
        assert self.pixels.__len__() == self.ratios.__len__()
        for i in range(self.pixels.__len__()):
            pixel = self.pixels[i]
            ratio = self.ratios[i]
            pixel_x = pixel[0]
            pixel_y = pixel[1]
            ratio_x = ratio[0]
            ratio_y = ratio[1]
            assert pixel_x.__len__() == pixel_y.__len__() and \
                   pixel_x.__len__() == ratio_x.__len__() and \
                   ratio_x.__len__() == ratio_y.__len__()
            for j in range(pixel_x.__len__()):
                r_x = ratio_x[j]
                r_y = ratio_y[j]
                self.pixels[i][0][j] = self.cv_image.shape[1] * r_x
                self.pixels[i][1][j] = self.cv_image.shape[0] * r_y
        pixels = self.pixels
        contents = self.contents
        self.initilize()
        return pixels, contents

    def set_image(self, image_path):
        # self.cv_image = cv2.imread(image_path)
        # g = self.geometry()
        # width = g.width()
        # height = g.height()
        # image_width = self.cv_image.shape[1]
        # image_height = self.cv_image.shape[0]
        # if image_height * (width / image_width) > height:
        #     new_width = image_width * (height / image_height)
        #     new_height = height
        # else:
        #     new_width = width
        #     new_height = image_height * (width / image_width)
        #
        # image = QtGui.QPixmap(image_path).scaled(new_width, new_height)
        # self.enabler = True
        # self.setPixmap(image)
        # self.repaint()
        self.image_path = image_path
        self.refresh_image()

    def refresh_image(self):
        if self.image_path == '':
            return
        self.cv_image = cv2.imread(self.image_path)
        g = self.geometry()
        width = g.width()
        height = g.height()

        width = max(64, width)
        height = max(64, height)

        image_width = self.cv_image.shape[1]
        image_height = self.cv_image.shape[0]
        if image_height * (width / image_width) > height:
            new_width = image_width * (height / image_height)
            new_height = height
        else:
            new_width = width
            new_height = image_height * (width / image_width)

        self.new_width = new_width
        self.new_height = new_height

        self.resize(new_width, new_height)
        image = QtGui.QPixmap(self.image_path).scaled(new_width, new_height)
        self.enabler = True
        self.setPixmap(image)

        assert self.pixels_x.__len__() == self.pixels_y.__len__() and \
               self.pixels_x.__len__() == self.ratios_x.__len__() and \
               self.ratios_x.__len__() == self.ratios_y.__len__()
        for i in range(self.pixels_x.__len__()):
            self.pixels_x[i] = new_width * self.ratios_x[i]
            self.pixels_y[i] = new_height * self.ratios_y[i]

        assert self.pixels.__len__() == self.ratios.__len__()
        for i in range(self.pixels.__len__()):
            pixel = self.pixels[i]
            ratio = self.ratios[i]
            pixel_x = pixel[0]
            pixel_y = pixel[1]
            ratio_x = ratio[0]
            ratio_y = ratio[1]
            assert pixel_x.__len__() == pixel_y.__len__() and \
                   pixel_x.__len__() == ratio_x.__len__() and \
                   ratio_x.__len__() == ratio_y.__len__()
            for j in range(pixel_x.__len__()):
                r_x = ratio_x[j]
                r_y = ratio_y[j]
                self.pixels[i][0][j] = new_width * r_x
                self.pixels[i][1][j] = new_height * r_y

        self.repaint()

    def paintEvent(self, e):
        if not self.enabler:
            return
        QLabel.paintEvent(self, e)
        if self.hold:
            self.point_number = 3
        painter = QtGui.QPainter()
        painter.begin(self)
        if self.pixel_x > 0 and self.pixel_y > 0:
            self.draw_points(painter)
        painter.end()

    def mousePressEvent(self, e):
        width = self.geometry().width()
        height = self.geometry().height()
        if not self.enabler:
            return
        if self.hold:
            return
        for i in range(self.pixels_x.__len__()):
            x = self.pixels_x[i]
            y = self.pixels_y[i]
            if x == e.x() and y == e.y():
                return
        if self.point_number < 4:
            self.pixel_x = e.x()
            self.pixel_y = e.y()
            ratio_x = self.pixel_x / width
            ratio_y = self.pixel_y / height
            self.pixels_x.append(self.pixel_x)
            self.pixels_y.append(self.pixel_y)
            self.ratios_x.append(ratio_x)
            self.ratios_y.append(ratio_y)
            self.first_click = True
            self.repaint()
            self.first_click = False
            self.point_number += 1
            if self.point_number == 4:
                self.hold = True
                w = self.cv_image.shape[1]
                h = self.cv_image.shape[0]
                self.finetune_window.set_parameters(self.window_geometry,
                                                    (round(self.ratios_x[0] * w), round(self.ratios_y[0] * h)),
                                                    (round(self.ratios_x[1] * w), round(self.ratios_y[1] * h)),
                                                    (round(self.ratios_x[2] * w), round(self.ratios_y[2] * h)),
                                                    (round(self.ratios_x[3] * w), round(self.ratios_y[3] * h)),
                                                    self.cv_image)
                self.finetune_window.activateWindow()
                self.finetune_window.exec()

                if self.finetune_window.annotation_finish:
                    finetuned_pixels = self.finetune_window.finetune_results
                    finetuned_ratios_x = (finetuned_pixels[0][0] / w, finetuned_pixels[1][0] / w,
                                          finetuned_pixels[2][0] / w, finetuned_pixels[3][0] / w)
                    finetuned_pixels_x = [finetuned_ratios_x[0] * self.new_width,
                                          finetuned_ratios_x[1] * self.new_width,
                                          finetuned_ratios_x[2] * self.new_width,
                                          finetuned_ratios_x[3] * self.new_width]

                    finetuned_ratios_y = (finetuned_pixels[0][1] / h, finetuned_pixels[1][1] / h,
                                          finetuned_pixels[2][1] / h, finetuned_pixels[3][1] / h)
                    finetuned_pixels_y = [finetuned_ratios_y[0] * self.new_height,
                                          finetuned_ratios_y[1] * self.new_height,
                                          finetuned_ratios_y[2] * self.new_height,
                                          finetuned_ratios_y[3] * self.new_height]

                    self.pixels.append([finetuned_pixels_x, finetuned_pixels_y])
                    self.ratios.append([finetuned_ratios_x, finetuned_ratios_y])
                    self.contents.append(self.finetune_window.content)
                self.point_number = 0
                self.pixels_x = []
                self.pixels_y = []
                self.ratios_x = []
                self.ratios_y = []
                self.hold = False
                # self.finish_paint = True
                self.repaint()
                # self.finish_paint = False
                self.window_geometry = self.finetune_window.get_geometry()
        else:
            pass

    def draw_points(self, painter):
        if self.pixels.__len__() != 0:
            for pixel in self.pixels:
                pixels_x = pixel[0]
                pixels_y = pixel[1]
                painter.setPen(QtGui.QPen(QtCore.Qt.green, 5))
                painter.drawPoint(pixels_x[0], pixels_y[0])
                painter.drawPoint(pixels_x[1], pixels_y[1])
                painter.drawPoint(pixels_x[2], pixels_y[2])
                painter.drawPoint(pixels_x[3], pixels_y[3])
                painter.drawLine(pixels_x[0], pixels_y[0], pixels_x[1], pixels_y[1])
                painter.drawLine(pixels_x[1], pixels_y[1], pixels_x[2], pixels_y[2])
                painter.drawLine(pixels_x[2], pixels_y[2], pixels_x[3], pixels_y[3])
                painter.drawLine(pixels_x[3], pixels_y[3], pixels_x[0], pixels_y[0])

        assert self.point_number < 4
        if self.point_number == 0 and self.first_click:
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 5))
            painter.drawPoint(self.pixel_x, self.pixel_y)
        elif self.point_number == 1:
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 5))
            painter.drawPoint(self.pixels_x[0], self.pixels_y[0])
            painter.drawPoint(self.pixel_x, self.pixel_y)
            painter.drawLine(self.pixels_x[0], self.pixels_y[0], self.pixel_x, self.pixel_y)
        elif self.point_number == 2:
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 5))
            painter.drawPoint(self.pixels_x[0], self.pixels_y[0])
            painter.drawPoint(self.pixels_x[1], self.pixels_y[1])
            painter.drawPoint(self.pixel_x, self.pixel_y)
            painter.drawLine(self.pixels_x[0], self.pixels_y[0], self.pixels_x[1], self.pixels_y[1])
            painter.drawLine(self.pixels_x[1], self.pixels_y[1], self.pixel_x, self.pixel_y)
        elif self.point_number == 3:
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 5))
            painter.drawPoint(self.pixels_x[0], self.pixels_y[0])
            painter.drawPoint(self.pixels_x[1], self.pixels_y[1])
            painter.drawPoint(self.pixels_x[2], self.pixels_y[2])
            painter.drawPoint(self.pixel_x, self.pixel_y)
            painter.drawLine(self.pixels_x[0], self.pixels_y[0], self.pixels_x[1], self.pixels_y[1])
            painter.drawLine(self.pixels_x[1], self.pixels_y[1], self.pixels_x[2], self.pixels_y[2])
            painter.drawLine(self.pixels_x[2], self.pixels_y[2], self.pixel_x, self.pixel_y)
            painter.drawLine(self.pixels_x[3], self.pixels_y[3], self.pixels_x[0], self.pixels_y[0])

    def clear_paint(self):
        self.pixel_x = -1
        self.pixel_y = -1
        self.pixels_x = []
        self.pixels_y = []
        self.point_number = 0
        self.repaint()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        desktop = QtWidgets.QApplication.desktop()
        screen_rect = desktop.screenGeometry()
        self.screen_height = screen_rect.height()
        self.screen_width = screen_rect.width()

        self.window_x = int(self.screen_width / 4)
        self.window_y = int(self.screen_height / 4)
        self.window_width = int(self.screen_width / 2)
        self.toolbar_width = min(240, int(self.screen_width / 4 - 5))
        self.window_height = int(self.screen_height / 2)

        self.image_x = min(40, int(self.window_width / 8))
        self.image_y = min(80, int(self.window_height / 8))
        self.image_width = max(1, int(self.window_width - 2 * self.image_x))
        self.image_height = max(1, int(self.window_height - self.image_y - min(40, int(self.window_height / 8))))

        self.setGeometry(self.window_x, self.window_y, self.window_width + self.toolbar_width, self.window_height)
        self.setWindowTitle('TITLE')

        self.label = QLabelWithClick(self)

        self.image_list = []
        self.image_order_number = 0

        self.annotations = []
        self.contents = []
        self.input_paths = []

        self.btn_prev = QPushButton(self)
        self.btn_prev.setText('Prev.')
        self.btn_prev.clicked.connect(self.show_prev)
        self.btn_prev.setEnabled(False)

        self.btn_next = QPushButton(self)
        self.btn_next.setText('Next')
        self.btn_next.clicked.connect(self.show_next)
        self.btn_next.setEnabled(False)

        self.initialize_label()

        self.btn_choose_folder = QPushButton(self)
        self.btn_choose_folder.setText('Choose folder...')
        self.btn_choose_folder.clicked.connect(self.choose_folder)

        self.btn_choose_files = QPushButton(self)
        self.btn_choose_files.setText('Choose files...')
        self.btn_choose_files.clicked.connect(self.choose_files)

        self.delete_box = QCheckBox(self)
        self.delete_box.setText('Delete images after annotating')
        self.delete_box.clicked.connect(self.warning_dialog)

        self.image_save_box = QCheckBox(self)
        self.image_save_box.setText('Save corresponding images with\nannotation files')
        self.image_save_box.setChecked(True)
        self.image_save_box.clicked.connect(self.warning_dialog)

        self.btn_choose_output_folder = QPushButton(self)
        self.btn_choose_output_folder.setText('Choose output path...')
        self.btn_choose_output_folder.clicked.connect(self.choose_output)

        self.output_path_text = QTextEdit(self)
        self.output_path_text.setEnabled(False)

        self.btn_save_mode1 = QRadioButton('Save each image after annotating', self)
        self.btn_save_mode1.setChecked(True)
        self.btn_save_mode2 = QRadioButton('Save all images after annotating\n(not recommend)', self)
        self.save_mode_group = QButtonGroup(self)
        self.save_mode_group.addButton(self.btn_save_mode1, 1)
        self.save_mode_group.addButton(self.btn_save_mode2, 2)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)

        self.warning_window = None
        self.finetune_window = FinetuneWindow((100, 100, 800, 600))
        self.finetune_window.setFocus()

        self.label.set_finetune_window(self.finetune_window)

        self.refresh_widgets()

    def refresh_widgets(self):
        self.image_x = min(40, int(self.window_width / 8))
        self.image_y = min(80, int(self.window_height / 8))
        self.image_width = max(1, int(self.window_width - 2 * self.image_x))
        self.image_height = max(1, int(self.window_height - self.image_y - min(40, int(self.window_height / 8))))

        self.label.resize(self.image_width, self.image_height)
        self.label.move(self.image_x, self.image_y)
        self.label.refresh_image()

        self.btn_prev.resize(int(self.window_width / 9), int(self.image_y / 2))
        self.btn_prev.move(int(self.window_width / 9), int(self.image_y / 4))

        self.btn_next.resize(int(self.window_width / 9), int(self.image_y / 2))
        self.btn_next.move(int(3 * self.window_width / 9), int(self.image_y / 4))

        self.btn_choose_folder.resize(int(self.window_width / 9), int(self.image_y / 2))
        self.btn_choose_folder.move(int(5 * self.window_width / 9), int(self.image_y / 4))

        self.btn_choose_files.resize(int(self.window_width / 9), int(self.image_y / 2))
        self.btn_choose_files.move(int(7 * self.window_width / 9), int(self.image_y / 4))

        self.btn_choose_output_folder.setGeometry(self.window_width, self.image_y,
                                                  self.toolbar_width - 45, int(self.window_height / 20))
        self.output_path_text.setGeometry(self.window_width,
                                          self.image_y + int(self.window_height / 20),
                                          self.toolbar_width - 45, int(self.window_height / 10))

        self.delete_box.setGeometry(self.window_width, self.image_y + int(self.window_height / 5),
                                    self.toolbar_width, int(self.window_height / 20))
        self.image_save_box.setGeometry(self.window_width, self.image_y + int(self.window_height / 4),
                                        self.toolbar_width, int(self.window_height / 20))

        self.btn_save_mode1.setGeometry(self.window_width,
                                        self.image_y + int(self.window_height * 2 / 5),
                                        self.toolbar_width - 15, int(self.window_height / 20))
        self.btn_save_mode2.setGeometry(self.window_width,
                                        self.image_y + int(self.window_height * 2 / 5) + int(self.window_height / 20),
                                        self.toolbar_width - 15, int(self.window_height / 20))

        self.progress_bar.setGeometry(self.window_width,
                                        self.image_y + int(self.window_height * 13 / 20),
                                        self.toolbar_width - 15, int(self.window_height / 20))

    def resizeEvent(self, e):
        self.window_width = e.size().width() - self.toolbar_width
        self.window_height = e.size().height()
        self.refresh_widgets()
        QtWidgets.QWidget.resizeEvent(self, e)

    def initialize_label(self):
        self.label.setText("Choose an Image Folder or image files")
        self.label.setStyleSheet("QLabel{background:white;}"
                                 "QLabel{color:black;font-size:10px;font-weight:bold;font-family:Times New Roman;}"
                                 )
        self.label.enabler = False
        self.btn_next.setEnabled(False)
        self.btn_next.setText('Next')
        self.btn_prev.setEnabled(False)
        self.btn_prev.setText('Prev.')
        self.image_list = []
        self.image_order_number = 0
        self.annotations = []
        self.contents = []
        self.input_paths = []

    def choose_folder(self):
        self.initialize_label()
        self.label.clear_paint()
        self.image_order_number = 0
        folder_name = QFileDialog.getExistingDirectory(self, "Choose Folder", "")
        if folder_name == '':
            return
        image_names = get_files(folder_name, format_=['jpg', 'png', 'bmp'])
        self.image_list = []
        for image_name in image_names:
            self.image_list.append(folder_name + '/' + image_name)
        if image_names.__len__() == 0:
            return
        # first_image = QtGui.QPixmap(folder_name + '/' + image_names[0]).
        # scaled(self.label.width(), self.label.height())
        # self.label.setPixmap(first_image)
        self.label.set_image(folder_name + '/' + image_names[0])
        self.btn_next.setEnabled(True)
        self.btn_next.setText('Next')
        if image_names.__len__() == 1:
            self.btn_next.setText('Finish')

    def choose_files(self):
        self.initialize_label()
        self.label.clear_paint()
        self.image_order_number = 0
        image_names, _ = QFileDialog.getOpenFileNames(self, "Choose Folder", "", "*.jpg;;*.png;;*.bmp;;All Files(*)")
        self.image_list = image_names
        if image_names.__len__() == 0:
            return
        # first_image = QtGui.QPixmap(image_names[0]).scaled(self.label.width(), self.label.height())
        # self.label.setPixmap(first_image)
        self.label.set_image(image_names[0])
        self.btn_next.setEnabled(True)
        self.btn_next.setText('Next')
        if image_names.__len__() == 1:
            self.btn_next.setText('Finish')

    def choose_output(self):
        folder_name = QFileDialog.getExistingDirectory(self, "Choose Output Folder", "")
        if folder_name == '':
            return
        self.output_path_text.setText(folder_name)

    def warning_dialog(self):
        if self.delete_box.isChecked() and not self.image_save_box.isChecked():
            self.warning_window = CheckBoxWarning(self.geometry())
            self.warning_window.exec_()
        if self.delete_box.isChecked():
            self.btn_prev.setEnabled(False)
        if not self.delete_box.isChecked():
            self.btn_prev.setEnabled(True)

    def show_prev(self):
        order_number = self.image_order_number
        order_number -= 1
        self.refresh_widgets()
        if self.image_list[order_number] is None:
            self.warning_window = DeleteWarning(self.geometry())
            self.warning_window.exec_()
            return
        if order_number < 0:
            pass
        else:
            self.label.clear_paint()
            # image = QtGui.QPixmap(self.image_list[order_number]).scaled(self.label.width(), self.label.height())
            # self.label.setPixmap(image)
            self.label.set_image(self.image_list[order_number])
            self.image_order_number = order_number
            if order_number == 0:
                self.btn_prev.setEnabled(False)
            if order_number < self.image_list.__len__() - 1:
                self.btn_next.setText('Next')

    def show_next(self):
        self.refresh_widgets()
        if self.output_path_text.toPlainText() == '':
            self.warning_window = OutputWarning(self.geometry())
            self.warning_window.exec_()
            return
        annotation, content = self.label.get_annotation()
        assert annotation.__len__() == content.__len__()
        checked_id = self.save_mode_group.checkedId()
        output_path = self.output_path_text.toPlainText()
        delete_images = self.delete_box.isChecked()
        save_images = self.image_save_box.isChecked()
        if checked_id == 1:
            self.annotations.append(annotation)
            self.contents.append(content)
            self.input_paths.append(self.image_list[self.image_order_number])
            annotator = Annotator(self.annotations, self.contents, self.input_paths,
                                  output_path, delete_images, save_images, self.progress_bar)
            annotator.annotate()
            self.annotations = []
            self.contents = []
            self.input_paths = []
            if self.image_order_number == self.image_list.__len__() - 1:
                self.initialize_label()
                self.refresh_widgets()
                # self.output_path_text.setText('')
        elif checked_id == 2:
            self.annotations.append(annotation)
            self.contents.append(content)
            self.input_paths.append(self.image_list[self.image_order_number])
            if self.image_order_number == self.image_list.__len__() - 1:
                annotator = Annotator(self.annotations, self.contents, self.input_paths,
                                      output_path, delete_images, save_images, self.progress_bar)

                annotator.annotate()
                self.initialize_label()
                self.refresh_widgets()
                # self.output_path_text.setText('')
        if delete_images:
            self.image_list[self.image_order_number] = None
        order_number = self.image_order_number
        order_number += 1
        if order_number >= self.image_list.__len__():
            pass
        else:
            self.label.clear_paint()
            # image = QtGui.QPixmap(self.image_list[order_number]).scaled(self.label.width(), self.label.height())
            # self.label.setPixmap(image)
            self.refresh_widgets()
            self.label.set_image(self.image_list[order_number])
            self.image_order_number = order_number
            if order_number != 0:
                self.btn_prev.setEnabled(True)
            if order_number == self.image_list.__len__() - 1:
                self.btn_next.setEnabled(True)
                self.btn_next.setText('Finish')


class QLabelWithAdjust(QLabel):
    def __init__(self, parent=None):
        super(QLabelWithAdjust, self).__init__(parent)
        self.point_processing = 0
        self.cv_image = None
        self.ratios = None
        self.points = None
        self.new_width = -1
        self.new_height = -1
        self.preview_label = None

        self.confirm_btn = None
        self.cancel_btn = None

    def set_buttons(self, confirm, cancel):
        self.confirm_btn = confirm
        self.cancel_btn = cancel

    def set_preview_label(self, preview_label):
        self.preview_label = preview_label

    def set_image(self, cv_image, ratios):
        self.cv_image = cv_image
        self.ratios = ratios
        self.refresh_image()

    def refresh_image(self):
        g = self.geometry()
        width = g.width()
        height = g.height()

        width = max(64, width)
        height = max(64, height)

        image_width = self.cv_image.shape[1]
        image_height = self.cv_image.shape[0]
        if image_height * (width / image_width) > height:
            new_width = image_width * (height / image_height)
            new_height = height
        else:
            new_width = width
            new_height = image_height * (width / image_width)

        new_width = round(new_width)
        new_height = round(new_height)

        self.new_width = new_width
        self.new_height = new_height

        self.resize(new_width, new_height)

        cv_image = cv2.resize(self.cv_image, (new_width, new_height))
        cv_cutted_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        qt_image = QtGui.QImage(cv_cutted_image,
                                cv_cutted_image.shape[1], cv_cutted_image.shape[0], cv_cutted_image.shape[1] * 3,
                                QtGui.QImage.Format_RGB888)
        image = QtGui.QPixmap.fromImage(qt_image)
        # self.resize(QtCore.QSize(cv_cutted_image.shape[1], cv_cutted_image.shape[0]))
        self.setPixmap(image)

        # g = self.geometry()
        p1 = [new_width * self.ratios[0][0], new_height * self.ratios[0][1]]
        p2 = [new_width * self.ratios[1][0], new_height * self.ratios[1][1]]
        p3 = [new_width * self.ratios[2][0], new_height * self.ratios[2][1]]
        p4 = [new_width * self.ratios[3][0], new_height * self.ratios[3][1]]
        self.points = [p1, p2, p3, p4]

        self.repaint()

    def paintEvent(self, e):
        QLabel.paintEvent(self, e)
        painter = QtGui.QPainter()
        painter.begin(self)
        self.draw_points(painter)
        painter.end()

    def draw_points(self, painter):
        if self.points is None:
            return
        p1 = self.points[0]
        p2 = self.points[1]
        p3 = self.points[2]
        p4 = self.points[3]
        painter.setPen(QtGui.QPen(QtCore.Qt.red, 5))
        painter.drawPoint(p1[0], p1[1])
        painter.drawPoint(p2[0], p2[1])
        painter.drawPoint(p3[0], p3[1])
        painter.drawPoint(p4[0], p4[1])
        painter.drawLine(p1[0], p1[1], p2[0], p2[1])
        painter.drawLine(p2[0], p2[1], p3[0], p3[1])
        painter.drawLine(p3[0], p3[1], p4[0], p4[1])
        painter.drawLine(p4[0], p4[1], p1[0], p1[1])

        painter.setPen(QtGui.QPen(QtCore.Qt.blue, 10))
        painter.drawPoint(self.points[self.point_processing][0], self.points[self.point_processing][1])

    def check_point(self):
        point = self.points[self.point_processing]
        if point[0] < 0:
            point[0] = 0
        if point[1] < 0:
            point[1] = 0

        if point[0] > self.new_width - 1:
            point[0] = self.new_width - 1
        if point[1] > self.new_height - 1:
            point[1] = self.new_height - 1

        self.points[self.point_processing] = point

    def keyPressEvent(self, e):
        w = self.cv_image.shape[1]
        h = self.cv_image.shape[0]
        k = e.key()
        if k == QtCore.Qt.Key_Space:
            self.point_processing = (self.point_processing + 1) % 4
            self.repaint()
        elif k == QtCore.Qt.Key_Up:
            self.points[self.point_processing][1] = self.points[self.point_processing][1] - 1
            self.check_point()
            self.repaint()
            self.ratios[self.point_processing][1] = self.points[self.point_processing][1] / self.new_height
            self.preview_label.refresh_points(((self.ratios[0][0] * w, self.ratios[0][1] * h),
                                               (self.ratios[1][0] * w, self.ratios[1][1] * h),
                                               (self.ratios[2][0] * w, self.ratios[2][1] * h),
                                               (self.ratios[3][0] * w, self.ratios[3][1] * h)))
        elif k == QtCore.Qt.Key_Down:
            self.points[self.point_processing][1] = self.points[self.point_processing][1] + 1
            self.check_point()
            self.repaint()
            self.ratios[self.point_processing][1] = self.points[self.point_processing][1] / self.new_height
            self.preview_label.refresh_points(((self.ratios[0][0] * w, self.ratios[0][1] * h),
                                               (self.ratios[1][0] * w, self.ratios[1][1] * h),
                                               (self.ratios[2][0] * w, self.ratios[2][1] * h),
                                               (self.ratios[3][0] * w, self.ratios[3][1] * h)))
        elif k == QtCore.Qt.Key_Left:
            self.points[self.point_processing][0] = self.points[self.point_processing][0] - 1
            self.check_point()
            self.repaint()
            self.ratios[self.point_processing][0] = self.points[self.point_processing][0] / self.new_width
            self.preview_label.refresh_points(((self.ratios[0][0] * w, self.ratios[0][1] * h),
                                               (self.ratios[1][0] * w, self.ratios[1][1] * h),
                                               (self.ratios[2][0] * w, self.ratios[2][1] * h),
                                               (self.ratios[3][0] * w, self.ratios[3][1] * h)))
        elif k == QtCore.Qt.Key_Right:
            self.points[self.point_processing][0] = self.points[self.point_processing][0] + 1
            self.check_point()
            self.repaint()
            self.ratios[self.point_processing][0] = self.points[self.point_processing][0] / self.new_width
            self.preview_label.refresh_points(((self.ratios[0][0] * w, self.ratios[0][1] * h),
                                               (self.ratios[1][0] * w, self.ratios[1][1] * h),
                                               (self.ratios[2][0] * w, self.ratios[2][1] * h),
                                               (self.ratios[3][0] * w, self.ratios[3][1] * h)))
        elif k == QtCore.Qt.Key_Enter - 1:
            self.confirm_btn.click()
        elif k == QtCore.Qt.Key_Escape or k == QtCore.Qt.Key_Delete:
            self.cancel_btn.click()

    def mousePressEvent(self, e):
        self.setFocus()


class QLabelPreview(QLabel):
    def __init__(self, parent=None):
        super(QLabelPreview, self).__init__(parent)
        self.point_processing = 0
        self.points = None
        self.cv_image = None
        self.lx = 0
        self.ty = 0
        self.geo = None

    def set_points(self, points):
        self.points = points

    def set_image(self, cv_image, geo):
        self.cv_image = cv_image
        self.refresh_image(geo)
        self.geo = geo

    def set_map(self, lx, ty):
        self.lx = lx
        self.ty = ty

    def refresh_points(self, _points):
        restored_points = []
        for point in _points:
            new_point = (point[0] + self.lx, point[1] + self.ty)
            restored_points.append(new_point)
        self.points = restored_points

        self.refresh_image(self.geometry())

    def refresh_image(self, geo):
        self.resize(geo.width(), geo.height())
        new_points = ((0, 0), (self.geometry().width(), 0), (self.geometry().width(), self.geometry().height()),
                      (0, self.geometry().height()))
        transformation_matrix = cv2.getPerspectiveTransform(np.float32(self.points), np.float32(new_points))

        transformed_image = cv2.warpPerspective(self.cv_image.copy(), transformation_matrix,
                                                (self.geometry().width(), self.geometry().height()))
        cv_transformed_image = cv2.cvtColor(transformed_image, cv2.COLOR_BGR2RGB)
        qt_transformed_image = QtGui.QImage(cv_transformed_image,
                                            cv_transformed_image.shape[1], cv_transformed_image.shape[0],
                                            cv_transformed_image.shape[1] * 3, QtGui.QImage.Format_RGB888)
        image_ = QtGui.QPixmap.fromImage(qt_transformed_image)
        self.resize(QtCore.QSize(cv_transformed_image.shape[1], cv_transformed_image.shape[0]))
        self.setPixmap(image_)


class FinetuneWindow(QDialog):
    def __init__(self, window_geometry):
        super(FinetuneWindow, self).__init__()

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)# |QtCore.Qt.WindowStaysOnTopHint)

        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.window_x = window_geometry[0]
        self.window_y = window_geometry[1]
        self.window_width = window_geometry[2]
        self.window_height = window_geometry[3]

        self.setGeometry(self.window_x, self.window_y, self.window_width, self.window_height)
        self.setWindowTitle('Finetune annotation')

        self.point1 = (-1, -1)
        self.point2 = (-1, -1)
        self.point3 = (-1, -1)
        self.point4 = (-1, -1)
        self.lx = 0
        self.ty = 0
        self.finetune_results = []
        self.content = ''

        self.btn_confirm = QPushButton(self)
        self.btn_confirm.setText('OK')
        self.btn_confirm.clicked.connect(self.close_with_saving)
        self.btn_cancel = QPushButton(self)
        self.btn_cancel.setText('Cancel')
        self.btn_cancel.clicked.connect(self.close_without_saving)

        self.btn_swith_point = QPushButton(self)
        self.btn_swith_point.setText('Switch Point')
        self.btn_swith_point.clicked.connect(self.switch_point)

        self.content_text_frame = QLineEdit(self)
        self.content_text_frame.setPlaceholderText('Input descriptions of this object')

        self.label = QLabelWithAdjust(self)
        self.preview_label = QLabelPreview(self)
        self.label.set_buttons(self.btn_confirm, self.btn_cancel)
        # self.label.set_preview_label(self.preview_label)

        self.setFocus()
        self.label.setFocus()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.annotation_finish = False

        self.cv_image = None

        self.refresh_widgets()

    def set_parameters(self, window_geometry, point1, point2, point3, point4, cv_image):
        self.window_x = window_geometry[0]
        self.window_y = window_geometry[1]
        self.window_width = window_geometry[2]
        self.window_height = window_geometry[3]

        self.setGeometry(self.window_x, self.window_y, self.window_width, self.window_height)

        self.point1 = point1
        self.point2 = point2
        self.point3 = point3
        self.point4 = point4

        self.cv_image = cv_image

        self.content_text_frame.setText('')

        points_ = (point1, point2, point3, point4)
        annotated_rect = cv2.boundingRect(np.array(points_))
        x = annotated_rect[0]
        y = annotated_rect[1]
        w = annotated_rect[2]
        h = annotated_rect[3]

        self.lx = max(0, x - w)
        self.lx = max(self.lx, x - 100)
        x_extension = x - self.lx
        self.ty = max(0, y - h)
        self.ty = max(self.ty, y - 100)
        y_extension = y - self.ty

        rx = min(x + w + x_extension, cv_image.shape[1] - 1)
        by = min(y + h + y_extension, cv_image.shape[0] - 1)

        cv_cut_image = cv_image[self.ty: by, self.lx: rx]
        cut_width = rx - self.lx
        cut_height = by - self.ty

        moved_ratios = [[(point1[0] - self.lx) / cut_width, (point1[1] - self.ty) / cut_height],
                        [(point2[0] - self.lx) / cut_width, (point2[1] - self.ty) / cut_height],
                        [(point3[0] - self.lx) / cut_width, (point3[1] - self.ty) / cut_height],
                        [(point4[0] - self.lx) / cut_width, (point4[1] - self.ty) / cut_height]]

        self.label.set_image(cv_cut_image, moved_ratios)

        self.preview_label.set_points(points_)
        self.preview_label.set_image(self.cv_image, self.label.geometry())
        self.preview_label.set_map(self.lx, self.ty)

        self.label.set_preview_label(self.preview_label)

        self.setFocus()
        self.label.setFocus()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.annotation_finish = False

        self.refresh_widgets()

    def refresh_widgets(self):
        image_x = min(40, int(self.window_width / 8))
        image_y = min(80, int(self.window_height / 8))
        image_width = max(1, int(self.window_width - 2 * image_x))
        image_height = max(1, int((self.window_height - image_y - min(40, int(self.window_height / 8))) / 2))

        self.label.setGeometry(image_x, image_y, image_width, image_height)
        self.preview_label.setGeometry(image_x, image_y + image_height + 10,
                                       image_width, image_height)

        if self.cv_image is not None:
            self.label.refresh_image()
            self.preview_label.refresh_image(self.label.geometry())

        self.btn_confirm.setGeometry(int(self.window_width * 12 / 18), int(image_y / 4),
                                     int(self.window_width / 9), int(image_y / 2))
        self.btn_cancel.setGeometry(int(self.window_width * 15 / 18), int(image_y / 4),
                                    int(self.window_width / 9), int(image_y / 2))

        self.btn_swith_point.setGeometry(int(self.window_width * 9 / 18), int(image_y / 4),
                                         int(self.window_width / 9), int(image_y / 2))

        self.content_text_frame.setGeometry(int(self.window_width / 18), int(image_y / 4),
                                            int(self.window_width * 3 / 9), int(image_y / 2))

    def resizeEvent(self, e):
        self.window_width = e.size().width()
        self.window_height = e.size().height()
        self.refresh_widgets()
        QtWidgets.QWidget.resizeEvent(self, e)

    def moveEvent(self, e):
        self.window_x = e.pos().x()
        self.window_y = e.pos().y()
        QtWidgets.QWidget.moveEvent(self, e)

    def get_geometry(self):
        return (self.window_x, self.window_y, self.window_width, self.window_height)

    def switch_point(self):
        self.label.point_processing = (self.label.point_processing + 1) % 4
        self.label.repaint()

    def close_without_saving(self):
        self.close()

    def close_with_saving(self):
        self.annotation_finish = True

        finetuned_points = []
        for ratio in self.label.ratios:
            h = self.label.cv_image.shape[0]
            w = self.label.cv_image.shape[1]
            new_point = (ratio[0] * w, ratio[1] * h)
            finetuned_points.append(new_point)

        restored_points = []
        for point in finetuned_points:
            restored_point = (point[0] + self.lx, point[1] + self.ty)
            restored_points.append(restored_point)

        self.finetune_results = restored_points
        self.content = self.content_text_frame.text()
        self.close()

    # def keyPressEvent(self, e):
    #     k = e.key()
    #     if k == QtCore.Qt.Key_Enter:
    #         print('enter')
    #         self.btn_confirm.click()
    #     elif k == QtCore.Qt.Key_Escape or k == QtCore.Qt.Key_Delete:
    #         print('cancel')
    #         self.btn_cancel.click()


class CheckBoxWarning(QDialog):
    def __init__(self, window_geometry):
        super(CheckBoxWarning, self).__init__()
        self.setWindowTitle('Warning')

        self.button = QPushButton('I know', self)
        self.button.setGeometry(75, 70, 50, 20)
        self.button.clicked.connect(self.close)

        self.text = QLineEdit('Initial image will be lost!', self)
        self.text.setGeometry(10, 30, 180, 20)
        self.text.setStyleSheet("background:transparent;border-width:0;border-style:outset")

        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
        self.setFixedSize(200, 100)
        self.move(window_geometry.x() + (window_geometry.width() / 2) - 100,
                  window_geometry.y() + (window_geometry.height() / 2) - 50)


class OutputWarning(QDialog):
    def __init__(self, window_geometry):
        super(OutputWarning, self).__init__()
        self.setWindowTitle('Warning')

        self.button = QPushButton('OK', self)
        self.button.setGeometry(75, 70, 50, 20)
        self.button.clicked.connect(self.close)

        self.text = QLineEdit('Output path must be provided!', self)
        self.text.setGeometry(10, 30, 180, 20)
        self.text.setStyleSheet("background:transparent;border-width:0;border-style:outset")

        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
        self.setFixedSize(200, 100)
        self.move(window_geometry.x() + (window_geometry.width() / 2) - 100,
                  window_geometry.y() + (window_geometry.height() / 2) - 50)


class DeleteWarning(QDialog):
    def __init__(self, window_geometry):
        super(DeleteWarning, self).__init__()
        self.setWindowTitle('Warning')

        self.button = QPushButton('OK', self)
        self.button.setGeometry(75, 70, 50, 20)
        self.button.clicked.connect(self.close)

        self.text = QLineEdit('Image has been deleted!', self)
        self.text.setGeometry(10, 30, 180, 20)
        self.text.setStyleSheet("background:transparent;border-width:0;border-style:outset")

        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
        self.setFixedSize(200, 100)
        self.move(window_geometry.x() + (window_geometry.width() / 2) - 100,
                  window_geometry.y() + (window_geometry.height() / 2) - 50)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
