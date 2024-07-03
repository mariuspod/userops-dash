from itertools import count
from ape import chain
from ape.logging import logger

BLOCK_TS = {}

def get_block_ts(block_num: str) -> int:
    if block_num not in BLOCK_TS:
        block = chain.provider._make_request(
            "eth_getBlockByNumber",
            [block_num, True]
        )
        ts = int(block["timestamp"], 16)
        BLOCK_TS[block_num] = ts

    return BLOCK_TS[block_num]


def get_ranges(start_block: int, steps: int):
    head = chain.blocks.head.number
    end = 0
    ranges = []
    for i in count():
        if end > head:
            break

        start = start_block + (i * steps)
        end = start_block + ((i+1) * steps)-1
        to = min(end, head)
        #logger.debug("[%d, %d]" % (min(start, to), to))
        ranges.append([min(start, to), to])

    return ranges
