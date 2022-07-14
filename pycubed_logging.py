from pycubed import pocketqube as cubesat
import pycubed
from os import listdir, stat, mkdir, statvfs, exists
import time

filename = "/sd/default.txt"
logfile = "/sd/logs/log000.txt"


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
        'time-on': pycubed.timeon(),
        'fuel-gauge': pycubed.fuel_gauge(),
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
            cubesat.micro.nvm[cubesat._BOOTCNT],
            cubesat.micro.nvm[cubesat._FLAG],
            cubesat.micro.nvm[cubesat._RSTERRS],
            cubesat.micro.nvm[cubesat._DWNLINK],
            cubesat.micro.nvm[cubesat._DCOUNT]
        ]) +
        cubesat.BOOTTIME.to_bytes(3, 'big') +
        cubesat._stat['time-on'].to_bytes(4, 'big') +
        int(cubesat._stat['fuel-gauge']).to_bytes(1, 'big')
    })

    return cubesat._stat


def new_file(substring, binary=False):
    """
    create a new file on the SD card
    substring example: '/data/DATA_'
    int padded with zeroes will be appended to the last found file
    """

    n = 0
    folder = substring[: substring.rfind('/') + 1]
    filen = substring[substring.rfind('/') + 1:]
    info_fp = "info.txt"

    print('Creating new file in directory: /sd{} \
        with file prefix: {}'.format(folder, filen))

    # if the folder name is not currently in the sd directory,
    # create the directory and filename
    # also create the info.txt file, and write 1 to the file
    if folder.strip('/') not in listdir('/sd/'):
        print('Directory /sd{} not found. Creating...'.format(folder))
        mkdir('/sd' + folder)
        filename = '/sd' + folder + filen + '000.txt'
        info_file = open(info_fp)
        n += 1
        info_file.write(str(n))

    # if the folder name is currently in the sd directory
    else:
        # if the info file exists, use its contents to find n
        if exists(info_fp):
            info_file = open(info_fp)
            info_file_arr = []
            for line in info_file:
                info_file_arr.append(line.strip())
            n = int(info_file_arr[0])
            n += 1
            # find a way to replace current n with new n
            info_file.write(str(n))
            # create new filepath in sd directory, using given folder/file name
            filename = ('/sd' + folder + filen +
                                "{:03}".format(n) + ".txt")

        # else, create an info file and initialize n
        else:
            info_file = open(info_fp)
            n += 1
            info_file.write(str(n))

    # create new file with open, write timestamp and status
    with open(filename, "a") as f:
        f.write(
            '# Created: {:.0f}\r\n# Status: {}\r\n'.format(
                time.monotonic(), status()))

    # print a confirmation that this new file was created
    print('New filename:', filename)
    return filename


def new_log():
    """
    create a new log file
    """
    n = 0

    # check /sd/logs/info.txt
    # if info.txt doesn't exist, create it with n = 1, use n = 0 for filename
    # else, rewrite it with n + 1, use n for filename

    # iterate through all files in the logs folder
    for f in listdir('/sd/logs/'):
        # if the file number is greater than n, set n to file number
        if int(f[3: -4]) > n:
            n = int(f[3: -4])

    # the new log file has number n + 1; n is the current
    # greatest file number
    logfile = "/sd/logs/log" + "{:03}".format(n + 1) + ".txt"

    # open the new logfile and write the time it was created +
    # the current status
    with open(logfile, "a") as log:
        log.write('# Created: {:.0f}\r\n# Status: {}\r\n'.format(
            time.monotonic(), status()))

    # print a confirmation message that a new logfile was created
    print('New log file:', logfile)


def log(msg):
    """
    create/open file and write logs
    """
    # if size of current open logfile > 100MB, create new log file
    if stat(logfile)[6] > 1E8:
        new_log()

    # open the current logfile and write message msg with a timestamp
    if cubesat.hardware['SDcard']:
        with open(logfile, "a+") as file:
            file.write('{:.1f},{}\r\n'.format(time.monotonic(), msg))


def save(dataset, savefile=None):
    """
    save the passed dataset to the passed savefile
    dataset should be a set of lists; each line is a list:
        save(([line1],[line2]))
    to save a string, make it an item in a list:
        save(['This is my string'])
    by default, savefile is not passed
    """
    # if no savefile is passed, use the current filename attribute
    # by default
    if savefile is None:
        savefile = filename

    # open save file
    try:
        with open(savefile, "a") as file:
            for item in dataset:
                # if the item is a list or tuple
                if isinstance(item, (list, tuple)):
                    # iterate through item
                    for i in item:
                        # format based on whether i is a float or not
                        try:
                            if isinstance(i, float):
                                file.write('{:.9g},'.format(i))
                            else:
                                file.write('{:G},'.format(i))
                        except Exception:
                            file.write('{},'.format(i))
                # if the item is not a list or tuple, format
                else:
                    file.write('{},'.format(item))

                # write a newline to the file
                file.write('\n')

    # catch exception
    except Exception as e:
        # print SD save error message with exception
        print('[ERROR] SD Save:', e)
        pycubed.set_RGB(255, 0, 0)  # set RGB to red
        return False


def storage_stats():
    """
    return the storage statistics about the SD card and
    mainboard file system
    """
    sd = 0
    if cubesat.hardware['SDcard']:
        # statvfs returns info about SD card (mounted file system)
        sd = statvfs('/sd/')
        sd_storage_used = sd[3]
        sd_storage_total = sd[2]
        sd = int(100 * sd_storage_used / sd_storage_total)

    # returns information about the overall file system
    fs = statvfs('/')
    fs_storage_used = fs[3]
    fs_storage_total = fs[2]
    fs = int(100 * fs_storage_used / fs_storage_total)

    # return both sets of information
    return (fs, sd)
