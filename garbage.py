import random

GARBAGE_FRAMES = [
    "  ____  \n /####\\ \n|######|\n \\####/ ",
    " .-\"\"-. \n(  ==  )\n '-..-' ",
    "  _[]_  \n [____] \n  /__\\  ",
    "  .--.  \n / __ \\ \n| |  | |\n \\ '--/ ",
    "  ___   \n [_*_]  \n  /_\\   ",
    "  __    \n /o \\   \n| o |   \n \\__/   ",
]


def random_garbage_frame():
    return random.choice(GARBAGE_FRAMES)
