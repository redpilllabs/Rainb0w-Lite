from rich import print

from utils.helper import load_yaml, save_yaml


def enable_porn_dns_blocking(blocky_conf_file):
    print("[bold green]>> Block Porn by DNS")
    blocky_conf = load_yaml(blocky_conf_file)
    blocky_conf["upstream"]["default"] = ["94.140.14.15", "2a10:50c0::bad1:ff"]
    # if "porn" not in blocky_conf["blocking"]["clientGroupsBlock"]["default"]:
    #     blocky_conf["blocking"]["clientGroupsBlock"]["default"].append("porn")

    save_yaml(blocky_conf, blocky_conf_file)


def disable_porn_dns_blocking(blocky_conf_file):
    print("[bold green]>> Unblock Porn by DNS")
    blocky_conf = load_yaml(blocky_conf_file)
    blocky_conf["upstream"]["default"] = ["94.140.14.14", "2a10:50c0::ad1:ff"]
    # if "porn" in blocky_conf["blocking"]["clientGroupsBlock"]["default"]:
    #     blocky_conf["blocking"]["clientGroupsBlock"]["default"].remove("porn")

    save_yaml(blocky_conf, blocky_conf_file)
