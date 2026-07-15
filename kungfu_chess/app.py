import sys

from engine.game_engine import GameEngine
from input.controller import Controller
from board_io.board_printer import BoardPrinter
from model.game_state import GameState
from realtime.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import RuleEngine
from texttests.script_runner import ScriptRunner


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
