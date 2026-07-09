class PrintBoardHandler:
    """
    המטפל של פקודת ההדפסה (print board).
    מבקש מהלוח להדפיס את עצמו למסך.
    """
    @staticmethod
    def execute(board, command_line: str):
        # פשוט קורא לפונקציית ההדפסה שכבר קיימת בלוח
        board.print_board()
        