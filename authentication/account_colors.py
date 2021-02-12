import random

COLORS = {'#000000': 'black',
          '#FFFFFF': 'white'}


def random_color() -> str:
    return random.choice(list(COLORS.keys()))
