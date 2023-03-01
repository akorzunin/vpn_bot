import subprocess
from typing import Sequence, Union


def run_pipe_shell_command(command: Sequence[str]) -> Union[str, Exception]:
    try:
        result = subprocess.run(
            f'echo "{" ".join(command)}" > /pipes/pivpn_pipe && cat /pipes/pivpn_out',
            stdout=subprocess.PIPE,
            timeout=10,
            shell=True,
        )
    except subprocess.TimeoutExpired as e:
        return e
    except Exception as e:
        return e
    return result.stdout.decode("utf-8")


def run_shell_command(command: Sequence[str]) -> Union[str, Exception]:
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
        )
    except Exception as e:
        return e
    return result.stdout.decode("utf-8")


whoami = [
    "whoami",
]

get_all_clients = [
    "pivpn",
    "-c",
]

add_client = [
    "pivpn",
    "-a",
    "-n",
]  # prompt for client name

qr_client = [
    "pivpn",
    "-qr",
]  # prompt for client number

disable_client = [
    "pivpn",
    "-off",
    "-y",
]  # prompt for client number

enable_client = [
    "pivpn",
    "-on",
    "-y",
]  # prompt for client number


delete_client = [
    "pivpn",
    "-r",
    "-y",
]

list_clients = [
    "pivpn",
    "-l",
]  # output list of clients w/ public keys and creation date

backup_clients = [
    "pivpn",
    "-bk",
]  # save files to /home/wirevpn/pivpnbackup/*.tgz

speed_test = [
    "speedtest-cli",
]

get_config_by_filepath = [
    "cat",
]
