from io import StringIO
from pyinfra import host, inventory
from pyinfra.api import deploy
from pyinfra.operations import apt, files, server, systemd
from pyinfra.facts.deb import DebArch
from pyinfra.facts.files import File, FindInFile
from pyinfra.facts.server import LinuxDistribution

osVersion = host.get_fact(LinuxDistribution)["release_meta"]["VERSION_ID"]
osName = host.get_fact(LinuxDistribution)["release_meta"]["NAME"]
osCodename = host.get_fact(LinuxDistribution)["release_meta"]["CODENAME"]
osArch = host.get_fact(DebArch)

dbPassword = "demoPassword"
uiPassword = "demoPassword"

bareos_server = "bareos" in host.groups
bareos_client = host.data.get("bareos_client")

# region Install postgresql
@deploy ("Install Postgresql")
def install_postgresql():
    files.download(
        name="Add gpg key",
        src="https://www.postgresql.org/media/keys/ACCC4CF8.asc",
        dest="/etc/apt/keyrings/apt.postgresql.org.asc"
    )
    
    files.block(
        name="Add repository",
        path="/etc/apt/sources.list.d/pgdg.sources",
        content=f"Types: deb\n\
URIs: https://apt.postgresql.org/pub/repos/apt\n\
Suites: {osCodename}-pgdg\n\
Architectures: {osArch}\n\
Components: main\n\
Signed-By: /etc/apt/keyrings/apt.postgresql.org.asc",
    )
    
    apt.packages(
        name="Install",
        packages=["postgresql", "postgresql-client"],
        update=True
    )
# endregion

# region Add bareos repo
@deploy("Add Bareos repository")
def add_bareosRepo():
    URL=f"https://download.bareos.org/current/x{osName}_{osVersion}"
    files.download(
        name="Add the Bareos apt pg key",
        src=f"{URL}/bareos-keyring.gpg",
        dest="/etc/apt/keyrings/bareos-experimental.gpg"
    )

    files.block(
        name="Add repository",
        path="/etc/apt/sources.list.d/bareos.sources",
        content=f"Types: deb deb-src\n\
URIs: {URL}\n\
Suites: /\n\
Architectures: {osArch}\n\
Signed-By: /etc/apt/keyrings/bareos-experimental.gpg",
    )
# endregion

# region Install/Configure Bareos client
@deploy("Install Bareos Client")
def install_bareosClient():
    apt.packages(
        name="Install",
        packages=["bareos-client"],
        update=True
    )

    files.line(
        name="Modify myself.conf",
        path="/etc/bareos/bareos-fd.d/client/myself.conf",
        line="Name = ",
        replace=f"  Name = {host.name}"
    )
# endregion

# region Install/Configure Bareos server
@deploy("Install Bareos Server")
def install_bareosServer():
    apt.packages(
        name="Install",
        packages=["bareos"],
        update=True,
        _env={"db_password": dbPassword}
    )

    services = ["bareos-director", "bareos-storage", "bareos-filedaemon"]
    for service in services:
        systemd.service(
            name=f"Enbale/Start {service} Service",
            service=f"{service}.service",
            running=True,
            enabled=True
        )
        
    # TODO: Install Bareos WebUI
    apt.packages(
        name="Install WebUI",
        packages=["bareos-webui"]
    )
    
    server.shell(
        name="Enable php-fpm",
        commands=["a2enmod proxy proxy_fcgi", "a2enconf php*"],
    )
    
    files.template(
        name="Create WebUI Admin",
        src=StringIO("""Console {
  Name = "admin"
  Password = "{{password}}"
  Profile = "webui-admin"
  TlsEnable = false
}"""),
        dest="/etc/bareos/bareos-dir.d/console/admin.conf",
        user="bareos",
        group="bareos",
        mode="0640",
        password=uiPassword
    )
    
    services = ["bareos-director", "apache2"]
    for service in services:
        systemd.service(
            name=f"Reload {service}",
            service=f"{service}.service",
            reloaded=True
        )
# endregion

# region Setup Bareos clients
@deploy("Get Bareos Client password")
def getClientPassword(host):
    if host.get_fact(File, "/etc/bareos/bareos-fd.d/director/bareos-dir.conf"):
        return host.get_fact(FindInFile, "/etc/bareos/bareos-fd.d/director/bareos-dir.conf", "Password = ")[0].split('"')[1]
    return False

@deploy("Configure Bareos Clients")
def configure_bareosClients():
    clientTemplate = StringIO("""Client {
    Name = {{host}}
    Address = {{address}}
    Password = {{password}}
    }
    """)
    
    # TODO: Remove client when it gets deleted or disabled
    clientChanged = False
    for host in inventory.hosts:
        host = inventory.get_host(host)
        if host.data.get("bareos_client"):
            password = getClientPassword(host)
            if password != None and password != False:
                x = files.template(
                    name=f"Add Bareos Client config ({host.name})",
                    src=clientTemplate,
                    dest=f"/etc/bareos/bareos-dir.d/client/{host.name}.conf",
                    user="bareos",
                    group="bareos",
                    mode="0640",
                    host = host.name,
                    address = host.name,
                    password = getClientPassword(host)
                )
                if x.changed:
                    clientChanged = True

    if clientChanged:
        systemd.service(
            name=f"Reload bareos-director Service",
            service="bareos-director.service",
            reloaded=True
        )
# endregion

if bareos_client or bareos_server:
    add_bareosRepo()
    install_bareosClient()

if bareos_server:
    install_postgresql()
    install_bareosServer()
    configure_bareosClients()