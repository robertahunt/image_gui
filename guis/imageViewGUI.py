#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 20:43:32 2018

@author: robertahunt
"""
import os
import cv2
import rawpy
import numpy as np

from pyzbar import pyzbar
from PyQt5 import QtWidgets, QtCore, QtGui
from basicGUI import basicGUI, ClickableIMG

class imageViewGUI(basicGUI):
    def __init__(self):
        super(imageViewGUI, self).__init__()
        self.IMG_WIDTH = 1024//2
        self.IMG_HEIGHT = 680//2
        
        self.IMG_FOLDER = 'images'
        self.IMG_FILEFOLDER = self.getLatestImageName(self.IMG_FOLDER)
        self.IMG = self.getIMG()
        self.initUI()

    def getIMG(self):
        IMG_FORMAT = self.IMG_FILEFOLDER.split('.')[-1]
        if IMG_FORMAT == 'jpg':
            return cv2.imread(self.IMG_FILEFOLDER)
        elif IMG_FORMAT == 'arw':
            with rawpy.imread(self.IMG_FILEFOLDER) as raw:
                return raw.postprocess()
        else:
            self.warn('Image format in folder not understood.%s'%self.IMG_FORMAT)
    
    def initUI(self):
        self.img = ClickableIMG(self)
        self.img.setMinimumSize(self.IMG_WIDTH, self.IMG_HEIGHT)
        self.img.clicked.connect(self.openIMG)
        
        img_title = self.headerLabel('Latest image')
        img_desc = QtWidgets.QLabel('Latest image in folder: %s'%os.path.join(os.getcwd(),self.IMG_FOLDER))
        self.img_name = QtWidgets.QLabel('Image Name: ' + self.IMG_FILEFOLDER)
        self.takePhotoButton = QtWidgets.QPushButton("Take New Photo")
        self.takePhotoButton.clicked.connect(self.takePhoto)
        sendButton = QtWidgets.QPushButton("Send to Datastorage")
        sendButton.clicked.connect(self.send)
        self.QRCode = QtWidgets.QLabel()
        
        self.QRCodeManual = QtWidgets.QLabel('Manual Catalog Number Entry (used only if QR Code not found): ')
        self.QRCodeManualEdit = QtWidgets.QLineEdit()
        
        self.grid.addWidget(img_title, 0, 0, 1, 2)
        self.grid.addWidget(img_desc, 1, 0, 1, 2)
        self.grid.addWidget(self.img_name, 2, 0, 1, 2)
        self.grid.addWidget(self.QRCode, 3, 0, 1, 2)
        self.grid.addWidget(self.QRCodeManual, 4, 0, 1, 1)
        self.grid.addWidget(self.QRCodeManualEdit, 4, 1, 1, 1)
        self.grid.addWidget(self.img, 5, 0, 1, 2)
        self.grid.addWidget(sendButton, 6, 0, 1, 2)
        self.displayLatestImg()
        self.setLayout(self.grid)
        
    def send(self):    
        pass
        
    
    def getQRCode(self, img_path):
        IMG_FORMAT = img_path.split('.')[-1]
        #if IMG_FORMAT == 'arw':
            
        #elif IMG_FORMAT == 'jpg':
            
        decoded_list = pyzbar.decode(cv2.resize(self.IMG,(1024,680)))
        for decoded in decoded_list:
            if decoded.type == 'QRCODE':
                return decoded.data
        else:
            return 'XXXXXX'
        
    def openIMG(self):
        self.commandLine(['open', self.IMG_FILEFOLDER])
        
    def getLatestImageName(self, image_folder):
        images = [image for image in os.listdir(image_folder) if image.split('.')[-1] in ['jpg','arw']]
        latest_image_name = max([os.path.join(image_folder, image) for image in images], key=os.path.getctime)
        return latest_image_name
    
    def displayLatestImg(self):
        self.IMG_FILEFOLDER = self.getLatestImageName(self.IMG_FOLDER)
        IMG_FORMAT = self.IMG_FILEFOLDER.split('.')[-1]
        self.IMG = self.getIMG()
        if IMG_FORMAT == 'arw':
            img_resized = QtGui.QImage(self.IMG.data, self.IMG.shape[1], self.IMG.shape[0],
                                   self.IMG.shape[1]*3, QtGui.QImage.Format_RGB888)
            img_resized = QtGui.QPixmap.fromImage(img_resized).scaled(self.IMG_WIDTH, self.IMG_HEIGHT, 
                                                       QtCore.Qt.KeepAspectRatio)
        elif IMG_FORMAT == 'jpg':
            img_resized = QtGui.QPixmap(self.IMG_FILEFOLDER).scaled(self.IMG_WIDTH, self.IMG_HEIGHT, 
                                                       QtCore.Qt.KeepAspectRatio)
        self.img.setPixmap(img_resized)
        
        
        QRCode_text = self.getQRCode(self.IMG_FILEFOLDER)
        self.img_name.setText('Image Name: ' + QRCode_text + '_' + self.IMG_FILEFOLDER.split('/')[-1])            
        
        self.QRCode.setText('QR Code / Catalog Number: ' + QRCode_text)
        
    def takePhoto(self):
        IMG_QUALITY_SETTINGS = self.commandLine(['gphoto2','--get-config','/main/capturesettings/imagequality'])
        IMG_QUALITY = IMG_QUALITY_SETTINGS.split('\n')[3][9:]
        if IMG_QUALITY in ['Standard','Fine','Extra Fine']:
            IMG_FORMAT = 'jpg'
        else:
            IMG_FORMAT = 'arw'
        self.commandLine(['gphoto2', '--capture-image-and-download', '--filename', 
                          'images/%y-%m-%d_%H%M%S.' + IMG_FORMAT, '--force-overwrite'])
        self.displayLatestImg()
                