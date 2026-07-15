class ScriptParser:
    def __init__(self):
        self._parsers = {
            'click': self._parse_click,
            'wait': self._parse_wait,
            'jump': self._parse_jump,
            'print': self._parse_print,
        }

    def parse(self, command_line: str):
        parts = command_line.split()
        if not parts:
            return None
        parser = self._parsers.get(parts[0])
        if parser is None:
            return None
        return parser(parts)

    def _parse_click(self, parts):
        if len(parts) != 3:
            return None
        return ('click', int(parts[1]), int(parts[2]))

    def _parse_wait(self, parts):
        if len(parts) != 2:
            return None
        return ('wait', int(parts[1]))

    def _parse_jump(self, parts):
        if len(parts) != 3:
            return None
        return ('jump', int(parts[1]), int(parts[2]))

    def _parse_print(self, parts):
        if len(parts) != 2 or parts[1] != 'board':
            return None
        return ('print_board',)
