import os
import pygame

BASE_IMG_PATH = os.path.join(os.getcwd(), 'Assets')

def LoadImage(path):
    img = pygame.image.load(os.path.join(BASE_IMG_PATH, path)).convert()
   # img.set_colorkey((0, 0, 0))
    return img

def LoadImages(path):
    images = []
    for ImgName in os.listdir(BASE_IMG_PATH + path):
        images.append(LoadImage(path + '/' + ImgName))
    return images


class Animation:
    def __init__(self, images, ImgDur=5, loop=True):
        self.images = images
        self.loop = loop
        self.ImgDuration = ImgDur
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.ImgDuration, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.ImgDuration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.ImgDuration * len(self.images) - 1)
            if self.frame >= self.ImgDuration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.ImgDuration)]