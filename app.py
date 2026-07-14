import sys

from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.input.controller import Controller
from kungfu_chess.io.board_printer import BoardPrinter
from kungfu_chess.model.game_state import GameState
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.rules.rule_engine import RuleEngine
from kungfu_chess.texttests.script_runner import ScriptRunner


def main():
    game_state = GameState()
    rule_engine = RuleEngine()
    arbiter = RealTimeArbiter()
    engine = GameEngine(game_state, rule_engine, arbiter)
    controller = Controller(engine)
    printer = BoardPrinter()
    runner = ScriptRunner(engine, controller, printer)
    runner.run(sys.stdin)


if __name__ == '__main__':
    main()
