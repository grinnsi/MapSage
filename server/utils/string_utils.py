import re

_snake1 = re.compile(r'(.)([A-Z][a-z]+)')
_snake2 = re.compile(r'([a-z0-9])([A-Z])')

_kebab1 = re.compile(r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+")
_kebab2 = re.compile(r"(\s|_|-)+")

def camel_to_snake(name: str) -> str:
    name = _snake1.sub(r'\1_\2', name)
    name = _snake2.sub(r'\1_\2', name)
    return name.lower()

def snake_to_camel(name: str) -> str:
    return ''.join(word.title() for word in name.split('_'))

def string_to_kebab(name: str) -> str:
    name = _kebab1.sub(lambda mo: mo.group(0).lower(), name)
    name = _kebab2.sub(' ', name).split()
    return '-'.join(name)