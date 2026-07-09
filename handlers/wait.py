class WaitHandler:
    """
    המטפל של פקודת ההמתנה (wait).
    מקבל שורה כמו "wait 500" ומקדם את השעון של הלוח.
    """
    @staticmethod
    def execute(board, command_line: str):
        # מפרקים את השורה: ["wait", "500"]
        parts = command_line.split()

        # לוקחים את האיבר השני (המספר) והופכים אותו למספר שלם (int)
        ms = int(parts[1])

        # אומרים ללוח לקדם את השעון שלו במספר הזה
        board.advance_clock(ms)