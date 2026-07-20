import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from img import Img


from assets.piece_loader import PieceAssetLoader

class Renderer:
    def __init__(self, board_image_path: str = "board.png"):
        self.board_image_path = board_image_path
        # אתחול ה-Loader של הכלים (מגדיר שכל כלי יהיה בגודל של 100 על 100 פיקסלים)
        self.piece_loader = PieceAssetLoader("assets/pieces", cell_size=100)

    def render_board_with_piece(self, piece_color: str, piece_kind: str, x: int, y: int):
        # 1. טעינת הלוח
        board_canvas = Img().read(self.board_image_path)

        # 2. טעינת כלי מסוים (למשל צריח שחור או רגלי לבן) בעזרת ה-Loader
        piece_assets = self.piece_loader.load(piece_color, piece_kind)

        # לוקחים את התמונה הרגילה של הכלי (state רגיל)
        piece_img = piece_assets.get_state("normal").image

        # 3. ציור הכלי על גבי הלוח במיקום המבוקש (x, y)
        piece_img.draw_on(board_canvas, x, y)

        # 4. הצגת התוצאה הסופית למסך
        board_canvas.show()

        
if __name__ == "__main__":
    import os
    board_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets",
        "board.png",
    )
    renderer = Renderer(board_image_path=board_path)
    # ננסה למשל לצייר רגלי לבן (white, pawn) במיקום 100, 100 על הלוח
    renderer.render_board_with_piece("white", "pawn", 100, 100)