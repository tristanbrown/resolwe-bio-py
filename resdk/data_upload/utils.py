"""Uploads utility functions."""
from __future__ import absolute_import, division, print_function, unicode_literals

import time


def wait_process_complete(data, recheck_interval, abort=2600000):
    """Suspend until the data is finished processing."""
    basetime = time.time()
    current = time.time() - basetime
    while not process_complete(data) and current < abort:
        time.sleep(recheck_interval)
        data.update()
        current = time.time() - basetime


def process_complete(data):
    """Check the processing status of a data object."""
    busy = ['UP', 'RE', 'WT', 'PR']
    data.update()
    if data.status == 'OK':
        return True
    elif data.status in busy:
        return False
    elif data.status == 'ER':
        raise ValueError('Problem processing data object: {}'.format(data.name))
