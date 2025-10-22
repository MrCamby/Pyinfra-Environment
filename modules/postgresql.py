from pyinfra import host
from pyinfra.facts.files import File
from pyinfra.facts.server import LinuxDistribution
from pyinfra.facts.deb import DebPackage
from pyinfra.operations import apt, files, server, systemd

if host.get_fact(DebPackage, "postgresql") == None:
    version = "latest"
    if host.data.get("postgresql") != None and "version" in host.data.get("postgresql"):
        version = host.data.get("postgresql")["version"]

    apt.packages(
        name="Install ({})".format(", ".join(["curl", "gpg"])),
        packages=["curl", "gpg"],
        update=True
    )

    gpgFile = host.get_fact(File, "/etc/apt/keyrings/postgres.gpg")
    if gpgFile == None or gpgFile == False:
        server.shell(
            name="Add the PostgrSQL apt gpg key",
            commands=["curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo -H gpg --dearmor -o /etc/apt/keyrings/postgres.gpg"]
        )

    if version == "latest":
        version = "main"
    codename = host.get_fact(LinuxDistribution)["release_meta"]["CODENAME"]
    files.line(
        name="Add the PostgrSQL repository",
        path="/etc/apt/sources.list.d/pgdg.list",
        line="http://apt.postgresql.org/pub/repos/apt",
        replace="deb [signed-by=/etc/apt/keyrings/postgres.gpg] http://apt.postgresql.org/pub/repos/apt " + codename + "-pgdg main",
    )

    if version == "main":
        apt.packages(
            name="Install postgresql",
            packages="postgresql",
        )
    else: 
        apt.packages(
            name=f"Install postgresql-{version}",
            packages=f"postgresql-{version}",
        )

# TODO: The following will not be done during the first installation
if host.get_fact(DebPackage, "postgresql") != None:
    version = host.get_fact(DebPackage, "postgresql")
    version = version["version"].split('+')[0]
    restartRequired = False

    if host.data.get("postgresql") != None and "config" in host.data.get("postgresql"):
        for file in host.data.get("postgresql")["config"].items():
            filename = file[0]
            entries = file[1]
            for k, v in entries.items():
                modification = files.line(
                    name=f"Modify {filename} ({k} = {v})",
                    path=f"/etc/postgresql/{version}/main/{filename}",
                    line="^#\?" + k,
                    replace=k + " = " + v,
                    backup=True
                )
                if modification.changed:
                    restartRequired = True

    if restartRequired:
        version = host.data.get("postgresql")["version"]
        systemd.service(
            name=f"Restart and enable the PostgrSQL {version} service",
            service=f"postgresql@{version}-main.service",
            running=True,
            restarted=True,
            enabled=True,
        )