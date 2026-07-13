class JumpHandler:
    @staticmethod
    def execute(board, command_line: str):
        parts = command_line.split()
        x = int(parts[1])
        y = int(parts[2])
        board.handle_jump(x, y)
