import json
import os
from typing import Dict, List, Optional

import pygame


def asset_folder_for(color: str, kind: str) -> str:
    color_letter = 'W' if color == 'w' else 'B'
    return kind + color_letter


class StateAssets:
    def __init__(self, name: str, config: dict, sprites: List[pygame.Surface]):
        self.name = name
        self.config = config
        self.sprites = sprites
        physics = config.get('physics', {})
        graphics = config.get('graphics', {})
        self.speed_m_per_sec = float(physics.get('speed_m_per_sec', 0.0))
        self.next_state = physics.get('next_state_when_finished', 'idle')
        self.frames_per_sec = float(graphics.get('frames_per_sec', 6))
        self.is_loop = bool(graphics.get('is_loop', True))

    @property
    def animation_duration_ms(self) -> int:
        if not self.sprites or self.frames_per_sec <= 0:
            return 500
        return int(round(len(self.sprites) / self.frames_per_sec * 1000))


class PieceAssets:
    def __init__(self, folder_name: str, states: Dict[str, StateAssets]):
        self.folder_name = folder_name
        self.states = states

    def get_state(self, state_name: str) -> Optional[StateAssets]:
        return self.states.get(state_name)


class PieceAssetLoader:
    def __init__(self, pieces_root: str, cell_size: int = 100):
        self.pieces_root = pieces_root
        self.cell_size = cell_size
        self._cache = {}

    def load(self, color: str, kind: str) -> PieceAssets:
        key = (color, kind)
        if key in self._cache:
            return self._cache[key]

        folder = asset_folder_for(color, kind)
        piece_dir = os.path.join(self.pieces_root, folder)
        states = {}
        states_dir = os.path.join(piece_dir, 'states')
        if os.path.isdir(states_dir):
            for state_name in os.listdir(states_dir):
                state_path = os.path.join(states_dir, state_name)
                if not os.path.isdir(state_path):
                    continue
                config_path = os.path.join(state_path, 'config.json')
                with open(config_path, 'r', encoding='utf-8') as handle:
                    config = json.load(handle)
                sprites_dir = os.path.join(state_path, 'sprites')
                sprites = self._load_sprites(sprites_dir)
                states[state_name] = StateAssets(state_name, config, sprites)

        assets = PieceAssets(folder, states)
        self._cache[key] = assets
        return assets

    def _load_sprites(self, sprites_dir: str) -> List[pygame.Surface]:
        if not os.path.isdir(sprites_dir):
            return []
        names = sorted(
            [name for name in os.listdir(sprites_dir) if name.lower().endswith('.png')],
            key=lambda name: int(os.path.splitext(name)[0])
        )
        sprites = []
        for name in names:
            path = os.path.join(sprites_dir, name)
            image = pygame.image.load(path)
            if pygame.display.get_surface() is not None:
                image = image.convert_alpha()
            sprites.append(pygame.transform.smoothscale(image, (self.cell_size, self.cell_size)))
        return sprites
