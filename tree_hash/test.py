from hashlib import blake2b


def blake(x):
    h = blake2b(x).digest()[0:32]
    print("{}".format(h))
    return h


class SSZObject:
    def __init__(self, x):
        self.x = x


def hash_ssz_object(obj):
    if isinstance(obj, list):
        objhashes = [hash_ssz_object(o) for o in obj]
        return merkle_root(objhashes)
    elif not isinstance(obj, SSZObject):
        return hash(obj)
    else:
        o = b''
        for f in obj.fields:
            val = getattr(obj, f)
            o += hash_ssz_object(val)
        return hash(o)


def merkle_root(objs):
    # print(objs)
    min_pow_of_2 = 1
    while min_pow_of_2 <= len(objs):
        min_pow_of_2 *= 2
    o = [0] * min_pow_of_2 + [len(objs).to_bytes(32, 'big')] + objs + [b'\x00'*32] * (min_pow_of_2 - len(objs))
    # print(o)
    for i in range(min_pow_of_2 - 1, 0, -1):
        o[i] = hash(o[i*2] + o[i*2+1])
    return o

print(hash(b"lol"))

x = hash_ssz_object([b"\x42"] * 8)
print(x)
