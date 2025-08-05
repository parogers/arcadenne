
import pygame


SPEED = 2000


class ImageCarousel:
    def __init__(self, images):
        self.images = images
        self.current_index = 0
        self.next_index = 0
        self.direction = 0
        self.offset = 0

    def shift_left(self):
        self.next_index = (self.current_index - 1 + len(self.images)) % len(self.images)
        self.direction = 1

    def shift_right(self):
        self.next_index = (self.current_index + 1) % len(self.images)
        self.direction = -1

    def update(self, dt):
        if self.direction:
            self.offset += SPEED*dt*self.direction
            img = self.images[self.current_index]
            if abs(self.offset) > img.get_width():
                self.direction = 0
                self.offset = 0
                self.current_index = self.next_index

    def render(self, target):
        img = self.images[self.current_index]
        area = pygame.Rect(0, 0, img.get_width(), img.get_height())
        area.center = (target.get_width()/2, target.get_height()/2)
        target.set_clip(area)
        target.fill((0, 0, 0))
        target.blit(
            img,
            (
                area.x + self.offset,
                area.y,
            )
        )
        if self.offset:
            next_img = self.images[self.next_index]
            target.blit(
                next_img,
                (
                    area.x + self.offset - self.direction*img.get_width(),
                    area.y,
                )
            )
