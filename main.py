import sys
from board.board import ChessBoard
from handlers.click import ClickHandler
from handlers.wait import WaitHandler
from handlers.jump import JumpHandler
from handlers.print_board import PrintBoardHandler

class CommandRegistry:
    """
    ספר הכתובות של הפקודות: מחזיק מילון שמקשר בין מילת הפקודה למטפל שלה.
    """
    _HANDLERS = {
        "click": ClickHandler,
        "wait": WaitHandler,
        "jump": JumpHandler,
        "print": PrintBoardHandler
    }

    @classmethod
    def get_handler(cls, command_line: str):
        parts = command_line.split()
        if not parts:
            return None
        return cls._HANDLERS.get(parts[0])

def main():
    board = ChessBoard()

    # שלב א': קריאת מבנה הלוח הראשוני מהקלט
    for line in sys.stdin:
        cleaned_line = line.strip()
        if cleaned_line == "Commands:":
            break
        if not cleaned_line or cleaned_line.startswith("Board:"):
            continue
        board.add_row(cleaned_line)

    # שלב ב': קריאת הפקודות והרצה אוטומטית דרך המילון
    for line in sys.stdin:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue

        handler = CommandRegistry.get_handler(cleaned_line)
        if handler:
            handler.execute(board, cleaned_line)

if __name__ == "__main__":
    main()