class ScriptParser:
    def parse(self, command_line: str):
        parts = command_line.split()
        if not parts:
            return None
        name = parts[0]
        if name == 'click' and len(parts) == 3:
            return ('click', int(parts[1]), int(parts[2]))
        if name == 'wait' and len(parts) == 2:
            return ('wait', int(parts[1]))
        if name == 'jump' and len(parts) == 3:
            return ('jump', int(parts[1]), int(parts[2]))
        if name == 'print' and len(parts) == 2 and parts[1] == 'board':
            return ('print_board',)
        return None
