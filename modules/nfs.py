from pyinfra import host
from pyinfra.facts.deb import DebPackage
from pyinfra.operations import files, server, systemd
from modules.apt import install

        
install(["nfs-kernel-server"])

systemd.service(
    name="Ensure nfs-kernel-server is running",
    service="nfs-kernel-server",
    running=True,
    enabled=True,
)

exports = []

for share in host.data.get("nfs"):
    files.directory(
        name="Ensure {} exists".format(share["path"]),
        path=share["path"],
        present=True,
    )
    for client in share["clients"]:
        exports.append("{} {}({})".format(share["path"], client["remote"], client["options"]))

exportConfig = files.block(
    name="Setup /etc/exports",
    path="/etc/exports",
    present=True,
    content="\n".join(exports),
    backup=True
)

if exportConfig.changed:
    server.shell(
        name="Export NFS shares",
        commands=["exportfs -ra"]
    )