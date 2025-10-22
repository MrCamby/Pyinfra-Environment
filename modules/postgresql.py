from pyinfra import host
from pyinfra.facts.files import File
from pyinfra.facts.server import LinuxDistribution
from pyinfra.operations import files, server, systemd
from modules.apt import install


if "version" in host.data.get("postgresql"):
    install(["curl", "gpg"])

    gpgFile = host.get_fact(File, "/etc/apt/keyrings/postgres.gpg")
    if gpgFile == None or gpgFile == False:
        server.shell(
            name="Add the PostgrSQL apt gpg key",
            commands=["curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo -H gpg --dearmor -o /etc/apt/keyrings/postgres.gpg"]   
        )
        
    version = host.data.get("postgresql")["version"]
    if version == "latest":
        version = "main"
    codename = host.get_fact(LinuxDistribution)["release_meta"]["CODENAME"]
    files.line(
        name="Add the PostgrSQL repository",
        path="/etc/apt/sources.list.d/pgdg.list", 
        line="http://apt.postgresql.org/pub/repos/apt",
        replace="deb [signed-by=/etc/apt/keyrings/postgres.gpg] http://apt.postgresql.org/pub/repos/apt " + codename + "-pgdg main", 
    )
    
    version = "-" + version
    install(["postgresql" + version]),

restartRequired = False
if "config" in host.data.get("postgresql"):
    for file in host.data.get("postgresql")["config"].items():
        filename = file[0]
        entries = file[1]
        for k, v in entries.items():
            modification = files.line(
                name="Modify {} ({} = {})".format(filename, k, v),
                path="/etc/postgresql/{}/main/{}".format(version, filename),
                line="^#\?" + k,
                replace=k + " = " + v,
                backup=True
            )
            if modification.changed:
                restartRequired = True

if restartRequired:
    version = host.data.get("postgresql")["version"]
    systemd.service(
        name="Restart and enable the PostgrSQL {} service".format(version),
        service="postgresql@{}-main.service".format(version),
        running=True,
        restarted=True,
        enabled=True,
    )