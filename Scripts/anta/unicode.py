from pyparsing import unichr


def translate(i:str):
    char = i
    try:
        uChar = unichr(int(char.lstrip(r"\u"), 16))
        print(uChar)
    except ValueError as e:
        print(str(e).split(' ')[7])



