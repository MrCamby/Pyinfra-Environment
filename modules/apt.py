from pyinfra import host
from pyinfra.operations import apt, server

def install(packages: list[str]):
    apt.packages(
        name="Install ({})".format(", ".join(host.data.get("apt")["install"])),
        packages=packages,
    )

if "install" in host.data.get("apt"):
    install(host.data.get("apt")["install"])

if "auto_upgrade" in host.data.get("apt"):
    apt.packages(
        name="Update ({})".format(", ".join(host.data.get("apt")["auto_upgrade"])),
        packages=host.data.get("apt")["auto_upgrade"],
        latest=True,
        update=True,
    )

if "mark" in host.data.get("apt"):
    server.shell(
        name="Hold ({})".format(", ".join(host.data.get("apt")["mark"])),
        commands=[
            "apt-mark hold {}".format(" ".join(host.data.get("apt")["mark"]))
        ],
    )