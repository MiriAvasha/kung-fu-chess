# KungFuChess — GAME RULES PROMPT (source of truth for rebuilding / client)
# Repo: https://github.com/MiriamAvasha/kung-fu-chess
#
# Use this prompt when implementing the real client/UI so no rule is lost.
# Canonical engine path: GameEngine + RuleEngine + RealTimeArbiter
# (DemoController duplicates some realtime logic and also adds rest cooldowns / different speeds.)

"""
You are implementing KungFuChess (real-time chess without turns). Follow these rules exactly.

## Core concept
- No turns. Both colors may move at any time.
- Pieces travel over time (ms). Conflicts resolve by arrival time and move order.
- Board tokens: empty `.`, pieces `{w|b}{K|Q|R|B|N|P}`.
- Default board is 8x8. Engine supports arbitrary parsed sizes.

## Classic movement (static legality — RuleEngine)
Reject reasons: outside_board, empty_source, friendly_destination, illegal_piece_move, same source==dest.

### Pawn
- White moves row-1, black row+1.
- One forward if empty; double forward from start row if both squares empty.
- Start rows on HxW: white = height-1-1, black = 1 (on 8x8: white rank 6, black rank 1).
- Diagonal capture only onto enemy. NO en passant.

### Rook / Bishop / Queen
- Sliding rays. Empty squares along path + enemy capture square. Blocked by any piece.

### Knight
- 8 L-shapes. May leap. Empty or enemy destination. Ally blocked.

### King
- One square any direction. Empty or enemy. NO castling. NO check / checkmate / stalemate.

## Move duration (engine)
duration_ms = max(|dRow|, |dCol|) * PIECE_SPEED (all pieces currently 1000 ms per Chebyshev cell).
Jump duration = 1000 ms, stays on same square (airborne).

## Request-time opposite-color route conflict (engine only)
If an enemy is already moving on the SAME row (both horizontal) or SAME col (both vertical)
and intermediate route columns/rows overlap → reject with route_conflict.
Exception: mutual head-on swap (A→B's start and B→A's start) is NOT a route_conflict.

## Same-color path blocks (near-meet) — while motions active
1. Find shared path cells (ignore pure start-square overlap).
2. Compare arrival times; move order breaks ties (earlier order wins).
3. If later arrives before earlier LEAVES that cell (leave=None means stays forever),
   truncate later motion to the square BEFORE the shared cell.
4. Truncation scales duration: original_duration * stop_index / steps.
5. Also: static piece already sitting on path → stop before it
   (ally always; enemy only on intermediate squares, not final capture dest).

## Captures on arrival
- Due motions applied in order of (arrival_time, order).
- Opposite-color head-on swap: earlier cancelled (stays); later eats them on their square.
- Same color on destination: NEVER capture — stop on square before meeting cell.
- Enemy on destination: later arriver always eats whoever is there (idle or earlier arriver).
- Capturing a King → game_over=True, clear motions.

## Jumps (airborne)
- Piece stays on cell for JUMP_DURATION.
- Cannot jump if already moving or already jumping from that cell.
- If attacker lands on airborne ENEMY defender → defender eats attacker (attacker removed).
- If that attacker was a King → game_over.

## Promotion
- Only pawn → queen.
- White promotes on row 0; black on row height-1.
- Applied on successful landing (including truncated stop if that stop is last rank).

## Game over
- Only when a King is captured (or king-attacker eaten by airborne defender).
- No checkmate/stalemate. When game_over, further moves/jumps rejected.

## Explicitly NOT in the game
Castling, en passant, check, checkmate, stalemate, underpromotion, turn order,
50-move rule, repetition, draw offers.

## Demo-only extras (NOT in texttest/engine unless you add them)
- Piece FSM: idle → move → long_rest → idle; idle → jump → short_rest → idle.
- Only idle pieces can be selected in the pygame demo.
- Demo move speed comes from asset speed_m_per_sec (often ~1.5), not PIECE_SPEEDS.
- Demo does not enforce route_conflict.
- Demo UX: second click on selected square = jump; +/- resize board.

## Architecture reminder for client work
- Prefer RealTimeArbiter rules as source of truth for gameplay.
- Keep RuleEngine for static legality.
- Keep PromotionService pluggable (PawnToQueenPromotion today).
- Pixel mapping: cell = (y // CELL_SIZE, x // CELL_SIZE); CELL_SIZE default 100.
"""
