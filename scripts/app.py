
import time
import dask
import os
from ape import Contract, chain
from db import vicdb
from utils.constants import BICONOMY_BUNDLER_ADDRESSES
from utils.block import get_block_ts, get_ranges
from ape.logging import logger

ENTRYPOINT_CONTRACT = Contract("0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789")

def main():
    # backfilling
    backfill_start_block = os.getenv("BACKFILL_START_BLOCK")
    if backfill_start_block:
        logger.info("starting historical backfill from block %d" % int(backfill_start_block))
        start_backfill(int(backfill_start_block))

    # forward processing
    start_forward()


def start_backfill(start_block: int):
    log_range_size = os.getenv("LOG_RANGE_SIZE")
    if not log_range_size:
        log_range_size = 1000

    results = []
    for r in get_ranges(start_block, int(log_range_size)):
        results.append(
            dask.delayed(process_events)(r[0], r[1])
        )
    dask.compute(*results)


def start_forward():
    while True:
        try:
            for block in chain.blocks.poll_blocks():
                block_num = block.number
                process_events(block_num, block_num)
        except Exception as e:
            logger.error(e)
            time.sleep(.5)
            pass


def process_events(start_block: int, end_block: int):
    events = ENTRYPOINT_CONTRACT.UserOperationEvent.range(
        start_block,
        end_block+1,
    )
    metric_name = "UserOperationEvent"
    user_ops = {}
    has_data_for_ts = {}
    for event in events:
        tx = chain.provider._make_request(
            "eth_getTransactionByHash",
            [event.transaction_hash]
        )
        block_num = tx["blockNumber"]
        block_ts = get_block_ts(block_num)
        if block_ts not in has_data_for_ts:
            has_data_for_ts[block_ts] = vicdb.has_data(metric_name, block_ts)

        if has_data_for_ts[block_ts]:
            logger.info("data already exists for timestamp %d", block_ts)
            continue

        if block_ts not in user_ops:
            user_ops[block_ts] = {
                "biconomy": 0,
                "others": 0,
            }

        tx_from = tx["from"].lower()
        if tx_from in BICONOMY_BUNDLER_ADDRESSES:
            user_ops[block_ts]["biconomy"] += 1
        else:
            user_ops[block_ts]["others"] += 1

    vicdb.track(metric_name, user_ops, chain.chain_id)
    logger.info("done with range [%d-%d]" % (start_block, end_block))
