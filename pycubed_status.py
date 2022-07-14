"""
CircuitPython driver for PyCubed satellite board status
PyCubed Mini mainboard-v02 for Pocketqube Mission
* Author(s): Max Holliday, Yashika Batra
"""
from pycubed import pocketqube as cubesat
from pycubed import _BOOTCNT, _FLAG, _RSTERRS, _DWNLINK, _DCOUNT


def status():
    """
    return a dictionary with the following:
    1. NVM registers(boot count, flags, counters)
    2. Time (seconds) since boot/hard reset
    3. Battery voltage as % of full
    """

    cubesat._stat.update({
        'boot-time': cubesat.BOOTTIME,
        'boot-count': cubesat.c_boot,
        'time-on': cubesat.timeon,
        'fuel-gauge': cubesat.fuel_gauge,
        'flags': {
            'deploy': cubesat.f_deploy,
            'mid-deploy': cubesat.f_mdeploy,
            'burn1': cubesat.f_burn1,
            'burn2': cubesat.f_burn2
        },
        'counters': {
            'state-errors': cubesat.c_state_err,
            'vbus-resets': cubesat.c_vbus_rst,
            'deploy': cubesat.c_deploy,
            'downlink': cubesat.c_downlink,
        },
    })

    cubesat._stat.update({
        'raw': bytes
        ([
            cubesat.micro.nvm[_BOOTCNT],
            cubesat.micro.nvm[_FLAG],
            cubesat.micro.nvm[_RSTERRS],
            cubesat.micro.nvm[_DWNLINK],
            cubesat.micro.nvm[_DCOUNT]
        ]) +
        cubesat.BOOTTIME.to_bytes(3, 'big') +
        cubesat._stat['time-on'].to_bytes(4, 'big') +
        int(cubesat._stat['fuel-gauge']).to_bytes(1, 'big')
    })

    return cubesat._stat
