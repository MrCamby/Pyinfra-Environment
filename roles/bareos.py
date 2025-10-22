from pyinfra import host
from pyinfra.facts.deb import DebPackage
from pyinfra.facts.postgresql import PostgresqlDatabases
from pyinfra.facts.server import LinuxDistribution, Hostname
from pyinfra.operations import apt, files, server, systemd


# region Install & Configure
if host.get_fact(DebPackage, "bareos") == None:
        
    osVersion = host.get_fact(LinuxDistribution)["release_meta"]["VERSION_ID"]
    osCodename = host.get_fact(LinuxDistribution)["release_meta"]["CODENAME"]
    URL="https://download.bareos.org/current/xUbuntu_" + osVersion

    server.shell(
        name="Add the Bareos apt gpg key",
        commands=[f"wget -O /etc/apt/keyrings/bareos-experimental.gpg {URL}/bareos-keyring.gpg"]   
    )
    
    files.block(
        name="Add the Bareos repository",
        path="/etc/apt/sources.list.d/bareos.sources",
        content=f"Types: deb deb-src\n\
URIs: {URL}\n\
Suites: /\n\
Architectures: amd64\n\
Signed-By: /etc/apt/keyrings/bareos-experimental.gpg",
    )
    
    apt.packages(
        name="Install Bareos",
        packages="bareos",
        update=True,
    )
    
    server.shell(
        name="Create bareos database",
        commands=[" ".join(host.data.get("bareos")["db"].items()) + "/usr/lib/bareos/scripts/create_bareos_database"],
        _su_user="postgres"
    )
    
    server.shell(
        name="Create bareos tables",
        commands=[" ".join(host.data.get("bareos")["db"].items()) + "/usr/lib/bareos/scripts/make_bareos_tables"],
        _su_user="postgres"
    )
    
    server.shell(
        name="Grant bareos privileges",
        commands=[" ".join(host.data.get("bareos")["db"].items()) + "/usr/lib/bareos/scripts/grant_bareos_privileges"],
        _su_user="postgres"
    )

    services = ["bareos-director", "bareos-storage", "bareos-filedaemon"]
    for service in services:
        systemd.service(
            name=f"Enabel & Start {service}.service",
            service=service,
            enabled=True
        )
# endregion

# TODO SSL Certificate
# region Configure Director
# TODO directory_password
files.put(
    name="Upload bareos-dir.conf",
    src="files/bareos/bareos-dir.conf",
    dest="/etc/bareos/bareos-dir.conf",
    user="bareos",
    group="bareos",
    mode="0600",
    force=True
)

content = []
for catalog in [*host.data.get("bareos")["catalogs"], "director"]:
    content.append("Catalog {")
    content.append(f"  Name = catalog_{catalog}")
    content.append("  DB Driver = postgresql")
    content.append(f"  DB Name = catalog_{catalog}")
    content.append("  DB Address = 127.0.0.1")
    content.append("  DB Password = ") # TODO
    content.append(f"  DB User = catalog_{catalog}")
    content.append("}")
files.block(
    name=f"Setup Catalogs (bareos-dir.conf)",
    path="/etc/bareos/bareos-dir.conf",
    content="\n".join(content),
    marker="# {mark} PYINFRA BLOCK Catalogs",
    before=True,
    line="Director {"
)

content = []
for i in range(host.data.get("bareos")["devices"]):
    content.append("Storage {")
    content.append(f"  Name = device{i}")
    content.append(f"  Address = {host.data.get("bareos")["storage_address"]}")
    content.append(f"  Device = device{i}")
    content.append("  Media Type = File")
    content.append("  Password = ") # TODO
    content.append("  Heartbeat Interval = 300")
    content.append("  Maximum Concurrent Jobs = 20")
    content.append("}")
files.block(
    name=f"Setup Storages (bareos-dir.conf)",
    path="/etc/bareos/bareos-dir.conf",
    content="\n".join(content),
    marker="# {mark} PYINFRA BLOCK Storages",
    before=True,
    line="Director {"
)
# endregion

# region Configure Storage Daemon
files.put(
    name="Upload bareos-sd.conf",
    src="files/bareos/bareos-sd.conf",
    dest="/etc/bareos/bareos-sd.conf",
    user="bareos",
    group="bareos",
    mode="0600",
    force=True
)

files.line(
    name="Modify Director name (bareos-sd.conf)",
    path="/etc/bareos/bareos-sd.conf",
    line="director_name",
    replace=f"  Name = {host.data.get("bareos")["director_tag"]}"
)

# TODO
# files.line(
#     name="Modify Director password (bareos-sd.conf)",
#     path="/etc/bareos/bareos-sd.conf",
#     line="director_password",
#     replace=f"  Password = director_password"
# )

files.line(
    name="Modify Message Director (bareos-sd.conf)",
    path="/etc/bareos/bareos-sd.conf",
    line="messages_director",
    replace=f"  Director = {host.data.get("bareos")["director_tag"]} = all"
)

files.line(
    name="Modify Storage name (bareos-sd.conf)",
    path="/etc/bareos/bareos-sd.conf",
    line="storage_name",
    replace=f"  Name = {host.data.get("bareos")["storage_daemon_tag"]}"
)

content = []
for i in range(host.data.get("bareos")["devices"]):
    content.append("Device {")
    content.append(f"  Archive Deivce = {host.data.get("bareos")["mountpoint"]}")
    content.append("  Media Type = File")
    content.append(f"  Name = device{i}")
    content.append("  Always Open = no")
    content.append("  Automatic Mount = yes")
    content.append("  Label Media = yes")
    content.append("  Random Access = yes")
    content.append("  Removable Media = no")
    content.append("}")
files.block(
    name=f"Setup Devices (bareos-sd.conf)",
    path="/etc/bareos/bareos-sd.conf",
    content="\n".join(content),
    marker="# {mark} PYINFRA BLOCK Devices",
)
# endregion

# region Configure File Daemon
files.put(
    name="Upload bareos-fd.conf",
    src="files/bareos/bareos-fd.conf",
    dest="/etc/bareos/bareos-fd.conf",
    user="bareos",
    group="bareos",
    mode="0600",
    force=True
)

# TODO
# files.line(
#     name="Modify Filedaemon name (bareos-fd.conf)",
#     path="/etc/bareos/bareos-fd.conf",
#     line="filedeamon_name",
#     replace=f"  Name = filedeamon_name"
# )

# TODO
files.line(
    name="Modify Director password (bareos-fd.conf)",
    path="/etc/bareos/bareos-fd.conf",
    line="director_password",
    replace=f"  Password = director_password"
)

files.line(
    name="Modify Director name (bareos-fd.conf)",
    path="/etc/bareos/bareos-fd.conf",
    line="director_name",
    replace=f"  Name = {host.data.get("bareos")["director_tag"]}"
)

files.line(
    name="Modify Message Director (bareos-fd.conf)",
    path="/etc/bareos/bareos-fd.conf",
    line="messages_director",
    replace=f"  Director = {host.data.get("bareos")["director_tag"]} = all, !skipped, !restored"
)
# endregion

# region Configure BConsole
files.put(
    name="Upload bconsole.conf",
    src="files/bareos/bconsole.conf",
    dest="/etc/bareos/bconsole.conf",
    user="bareos",
    group="bareos",
    mode="0600",
    force=True
)

files.line(
    name="Modify Director name (bareos-fd.conf)",
    path="/etc/bareos/bareos-fd.conf",
    line="director_name",
    replace=f"  Name = {host.data.get("bareos")["director_tag"]}"
)
# endregion