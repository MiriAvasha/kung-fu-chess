import sys

from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.input.controller import Controller
from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.io.board_printer import BoardPrinter
from kungfu_chess.texttests.script_parser import ScriptParser


class ScriptRunner:
    def __init__(self, engine: GameEngine, controller: Controller, printer: BoardPrinter):
        self.engine = engine
        self.controller = controller
        self.printer = printer
        self.parser = ScriptParser()

    def run(self, input_stream):
        parser = BoardParser()
        game_state = None

        for line in input_stream:
            cleaned_line = line.strip()
            if cleaned_line == "Commands:":
                break
            if not cleaned_line or cleaned_line.startswith("Board:"):
                continue
            game_state = parser.add_row(cleaned_line)

        self.engine.game_state = game_state
        self.controller.selected_cell = None

        for line in input_stream:
            cleaned_line = line.strip()
            if not cleaned_line:
                continue
            command = self.parser.parse(cleaned_line)
            if command is None:
                continue
            if command[0] == 'click':
                self.controller.click(command[1], command[2])
            elif command[0] == 'wait':
                self.engine.wait(command[1])
            elif command[0] == 'jump':
                self.controller.jump(command[1], command[2])
            elif command[0] == 'print_board':
                self.printer.print_board(self.engine.game_state)
