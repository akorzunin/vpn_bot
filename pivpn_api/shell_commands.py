import subprocess
from typing import Sequence, Union


def run_shell_command(command: Sequence[str]) -> Union[str, Exception]:
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE)
    except Exception as e:
        return e
    return result.stdout.decode("utf-8")


whoami = [
    "whoami",
]

get_all_clients = ["pivpn", "-c"]

add_client = [
    "pivpn",
    "-a",
]  # prompt for client name

qr_client = [
    "pivpn",
    "-qr",
]  # prompt for client number

disable_client = [
    "pivpn",
    "-off",
]  # prompt for client number

enable_client = [
    "pivpn",
    "-on",
]  # prompt for client number

list_clients = [
    "pivpn",
    "-l",
]  # output list of clients w/ public keys and creation date

backup_clients = [
    "pivpn",
    "-bk",
]  # save files to /home/wirevpn/pivpnbackup/*.tgz
