from img import Img


class ImageView:
    """Displays an image produced by the Renderer."""

    @staticmethod
    def show(image: Img):
        image.show()

    @staticmethod
    def run(image: Img, on_left_click):
        image.show_interactive(on_left_click, window_name='KungFuChess')
