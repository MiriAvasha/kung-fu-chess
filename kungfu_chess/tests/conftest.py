import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.game_engine import GameEngine
from model.board import board_from_token_rows
from model.game_state import GameState
from model.position import Position
from realtime.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import RuleEngine


def make_board(rows):
    """Build a board from token rows. Use '.' for empty."""
    return board_from_token_rows(rows)


def make_engine(rows=None):
    if rows is None:
        rows = [['.']]
    game_state = GameState()
    game_state.board = make_board(rows)
    engine = GameEngine(game_state, RuleEngine(), RealTimeArbiter())
    return engine


def cell(row, col):
    return Position(row, col)


@pytest.fixture
def empty_8x8():
    return make_board([['.'] * 8 for _ in range(8)])
