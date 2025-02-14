import re

_snake1 = re.compile(r'(.)([A-Z][a-z]+)')
_snake2 = re.compile(r'([a-z0-9])([A-Z])')

def camel_to_snake(name: str) -> str:
    name = _snake1.sub(r'\1_\2', name)
    name = _snake2.sub(r'\1_\2', name)
    return name.lower()

def snake_to_camel(name: str) -> str:
    return ''.join(word.title() for word in name.split('_'))