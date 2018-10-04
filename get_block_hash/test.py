CYCLE_LENGTH = 4


# Heavily simplified
class ActiveState:
    def __init__(self, hashes):
        self.recent_block_hashes = hashes


# Heavily simplified
class Block:
    def __init__(self, slot):
        self.slot = slot


# Copied directly from the spec
def get_block_hash(active_state, curblock, slot):
    earliest_slot_in_array = curblock.slot - CYCLE_LENGTH * 2
    assert earliest_slot_in_array <= slot < earliest_slot_in_array + CYCLE_LENGTH * 2
    return active_state.recent_block_hashes[slot - earliest_slot_in_array]


# ActiveState stores hashes, but this makes the example simpler.
active_state = ActiveState([
    Block(100),
    Block(101),
    Block(102),
    Block(103),
    Block(104),
    Block(105),
    Block(200),
    Block(201),
])

block_slot = 201
desired_slot = 201 - CYCLE_LENGTH
block = get_block_hash(
    active_state,
    Block(block_slot),
    desired_slot
)

# prints: desired_slot: 197
print("desired_slot: {}".format(desired_slot))
# prints: returned_slot: 104
print("returned_slot: {}".format(block.slot))
