from model.position import Position


def motion_progress(motion, current_time: int) -> float:
    if motion.duration <= 0:
        return 1.0
    elapsed = current_time - motion.start_time
    return max(0.0, min(1.0, elapsed / float(motion.duration)))


def motion_pixel_position(motion, current_time: int, cell_size: int):
    progress = motion_progress(motion, current_time)
    start_x = motion.from_col * cell_size
    start_y = motion.from_row * cell_size
    end_x = motion.to_col * cell_size
    end_y = motion.to_row * cell_size
    return (
        start_x + (end_x - start_x) * progress,
        start_y + (end_y - start_y) * progress,
    )


def motion_source_cells(motions):
    return {
        Position(motion.from_row, motion.from_col)
        for motion in motions
    }
