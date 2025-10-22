from pyinfra import host
from pyinfra.facts.deb import DebPackage
from pyinfra.operations import apt, files, server, python
from modules.apt import install

mounts = []
for mount in host.data.get("mounts"):
    type = mount["type"]
    match mount["type"]:
        case "nfs":
            install(["nfs-common"])
        case _:
            python.raise_exception(
                name="Raise NotImplementedError exception",
                exception=NotImplementedError,
                message="This mount option is not implemented",
            )
    
    files.directory(
        name="Ensure {} exists".format(mount["dst"]),
        path=mount["dst"],
        present=True,
    )

    mounts.append("{} {} {} {} 0 0".format(mount["src"], mount["dst"], type, ",".join(mount["options"])))

exportConfig = files.block(
    name="Setup /etc/fstab",
    path="/etc/fstab",
    present=True,
    content="\n".join(mounts),
    backup=True
)

if exportConfig.changed:
    server.shell(
        name="Reload mounts",
        commands=["mount -a"]
    )