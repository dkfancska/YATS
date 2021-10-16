def get_version():
    import sys
    version = sys.version.split()[0]

    return version.split()[0].strip()

def datetime_to_datestr(date):
    if date:
        string = date.strftime('{"date": "%d %b %Y", "time": "%I:%M:%S %p", "utc_offset": "%z"}')
        # print("string:", string, type(string))
        return string
    else:
        return '{"date": "00 Xxx 0000", "time": "00:00:00 AM", "utc_offset": "+0000"}'

def datestr_to_datedict(date):
    import json
    return json.loads(date)

def datetime_to_datedict(date):
    datestr = datetime_to_datestr(date)
    datedict = datestr_to_datedict(datestr)

    return datedict

def get_platform():
    import platform
    
    return platform.system()

def check_requirements():
    Version = get_version()
    assert Version.startswith("3.8"), "\x1b[1msnscrape requires python version \x1b[0m\x1b[31;1m>= 3.8\x1b[0m\x1b[1m. Please create a conda/virtual environment with python version \x1b[0m\x1b[31;1m>= 3.8\x1b[0m"
    if get_platform() != "Linux":
        print("it seems you are not running this code on Linux. Please specify a path for storing backups (using the backup_folder argument) or disable backups by setting do_backup to false.")