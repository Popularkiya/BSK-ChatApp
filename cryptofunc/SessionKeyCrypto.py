from secrets import token_bytes


def generate(length):
    return token_bytes(length)
