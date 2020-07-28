from functools import reduce
ascii = reduce(lambda x, y: x + y, map(lambda x: chr(x), range(256)))
print(len(ascii.encode("utf-8")))