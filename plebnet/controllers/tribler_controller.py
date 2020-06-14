"""
This file is used to control all dependencies with Tribler.

Other files should never have a direct import from Tribler, as this reduces the maintainability of this code.
If Tribler alters its call methods, this should be the only file which needs to be updated in PlebNet.
"""

import os
import subprocess
import requests

from requests.exceptions import ConnectionError

from plebnet.utilities import logger
from plebnet.settings import plebnet_settings

setup = plebnet_settings.get_instance()


def running():
    """
    Checks if Tribler is running.
    :return: True if twistd.pid exists in /root/tribler and a process with the same pid is running.
    """
    path = os.path.join(setup.plebnet_home(), 'plebnet', setup.tribler_pid())

    if not os.path.isfile(path):
        return False

    pid = open(path, "r").read()
    exitcode = os.system("ps -p " + pid + " > /dev/null")
    process_running = (exitcode == 0)

    # If the process is not running, remove the twistd.pid file
    if not process_running:
        os.remove(path)

    return process_running


def start():
    """
    Starts Tribler by using the twistd plugin.
    :return: boolean representing the success of starting Tribler
    """
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.join(setup.plebnet_home(), 'plebnet') + ":"
    #env['PYTHONPATH'] += os.path.join(setup.plebnet_home(), 'plebnet/twisted/plugins') + ":"
    env['PYTHONPATH'] += os.path.join(setup.plebnet_home(), 'tribler/src/pyipv8') + ":"
    env['PYTHONPATH'] += os.path.join(setup.plebnet_home(), 'tribler/src/anydex') + ":"
    env['PYTHONPATH'] += os.path.join(setup.plebnet_home(), 'tribler/src/tribler-common') + ":"
    env['PYTHONPATH'] += os.path.join(setup.plebnet_home(), 'tribler/src/tribler-core')
    
    #print(env['PYTHONPATH'])

    command = ['twistd', '--pidfile='+setup.tribler_pid(), 'plebnet', '-p', '8085']

    if setup.wallets_testnet():
        command.append('--testnet')

    if setup.tribler_exitnode():
        command.append('--exitnode')

    try:
        exitcode = subprocess.call(command, cwd=os.path.join(setup.plebnet_home(), 'plebnet'), env=env)

        if exitcode != 0:
            logger.error('Failed to start Tribler', "tribler_controller")
            return False
        logger.success('Tribler is started', "tribler_controller")
        logger.log('testnet: ' + str(setup.wallets_testnet()))
        return True
    except subprocess.CalledProcessError as e:
        logger.error(e.output, "tribler_controller")
        return False


def get_uploaded():
    return 0
    # try:
    #     tu = requests.get('http://localhost:8085/trustchain/statistics').json()['statistics']['total_up']
    #     tu = int(tu)/1024.0/1024.0
    #     return tu
    # except ConnectionError:
    #     return "Unable to retrieve amount of uploaded data"


def get_helped_by():
    return "dfsljdfs"
    # try:
    #     return requests.get('http://localhost:8085/trustchain/statistics').json()['statistics']['peers_that_helped_pk']
    # except ConnectionError:
    #     return "Unable to retrieve amount of peers that helped this agent"


def get_helped():
    return 0
    # try:
    #     return requests.get('http://localhost:8085/trustchain/statistics').json()['statistics']['peers_that_pk_helped']
    # except ConnectionError:
    #     return "Unable to retrieve amount of peers helped by this agent"


def get_downloaded():
    return 0
    # try:
    #     td = requests.get('http://localhost:8085/trustchain/statistics').json()['statistics']['total_down']
    #     td = int(td)/1024.0/1024.0
    #     return td
    # except ConnectionError:
    #     return "Unable to retrieve amount of downloaded data"
