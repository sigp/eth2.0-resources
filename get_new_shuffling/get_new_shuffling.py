from hashlib import blake2b

VALIDATOR_COUNT = 100
CYCLE_LENGTH = 20
MIN_COMMITTEE_SIZE = 10
SHARD_COUNT = 10


class ShardAndCommittee():
    def __init__(self, shard_id, committee):
        self.shard_id = shard_id
        self.committee = committee


class ValidatorRecord():
    def __init__(self, start_dynasty, end_dynasty):
        self.start_dynasty = start_dynasty
        self.end_dynasty = end_dynasty


def split(lst, N):
    return [lst[len(lst)*i//N: len(lst)*(i+1)//N] for i in range(N)]


def blake(x):
    return blake2b(x).digest()[:32]


def get_active_validator_indices(validators, dynasty):
    o = []
    for i in range(len(validators)):
        if validators[i].start_dynasty <= dynasty < \
                validators[i].end_dynasty:
            o.append(i)
    return o


def shuffle(lst, seed):
    assert len(lst) <= 16777216
    o = [x for x in lst]
    source = seed
    i = 0
    while i < len(lst):
        source = blake(source)
        for pos in range(0, 30, 3):
            m = int.from_bytes(source[pos:pos+3], 'big')
            remaining = len(lst) - i
            if remaining == 0:
                break
            rand_max = 16777216 - 16777216 % remaining
            if m < rand_max:
                replacement_pos = (m % remaining) + i
                o[i], o[replacement_pos] = o[replacement_pos], o[i]
                i += 1
    return o


def get_new_shuffling(seed, validators, dynasty, crosslinking_start_shard):
    avs = get_active_validator_indices(validators, dynasty)
    if len(avs) >= CYCLE_LENGTH * MIN_COMMITTEE_SIZE:
        committees_per_slot = len(avs) // CYCLE_LENGTH // (MIN_COMMITTEE_SIZE * 2) + 1
        slots_per_committee = 1
    else:
        committees_per_slot = 1
        slots_per_committee = 1
        while len(avs) * slots_per_committee < CYCLE_LENGTH * MIN_COMMITTEE_SIZE \
                and slots_per_committee < CYCLE_LENGTH:
            slots_per_committee *= 2
    o = []
    for i, slot_indices in enumerate(split(shuffle(avs, seed), CYCLE_LENGTH)):
        shard_indices = split(slot_indices, committees_per_slot)
        shard_id_start = crosslinking_start_shard + \
            i * committees_per_slot // slots_per_committee
        o.append([ShardAndCommittee(
            shard_id=(shard_id_start + j) % SHARD_COUNT,
            committee=indices
        ) for j, indices in enumerate(shard_indices)])
    return o


"""
Start actually testing stuff
"""
seed = b"\x00" * 32
validators = [ValidatorRecord(0, 10) for _ in range(VALIDATOR_COUNT)]
dynasty = 1
crosslinking_start_shard = 0


cycle = get_new_shuffling(
    seed,
    validators,
    dynasty,
    crosslinking_start_shard)

print("Configuration:")
print("VALIDATOR_COUNT={}".format(VALIDATOR_COUNT))
print("CYCLE_LENGTH={}".format(CYCLE_LENGTH))
print("MIN_COMMITTEE_SIZE={}".format(MIN_COMMITTEE_SIZE))
print("SHARD_COUNT={}".format(SHARD_COUNT))

print("---------")
for (i, slot) in enumerate(cycle):
    print("Slot {}".format(i))
    for (i, sac) in enumerate(slot):
        print(("    Index {}:"
               "ShardAndCommittee(shard_id={}, committee_len={})")
              .format(i, sac.shard_id, len(sac.committee)))
