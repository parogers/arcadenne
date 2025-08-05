
class ImageCarousel:
    def __init__(self, images):
        self.images = images
        self.current_index = 0

    def shift_left(self):
        self.current_index = (self.current_index - 1 + len(self.images)) % len(self.images)

    def shift_right(self):
        self.current_index = (self.current_index + 1) % len(self.images)

    def render(self, target):
        img = self.images[self.current_index]
        target.blit(
            img,
            (
                target.get_width()/2 - img.get_width()/2,
                target.get_height()/2 - img.get_height()/2
            )
        )
