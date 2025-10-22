from pyinfra import host
from pyinfra.operations import files, systemd

if "servers" in host.data.get("ntp"):
    servers = host.data.get("ntp")['servers']
    if type(servers) == list:
        files.line(
            name="Add NTP servers",
            path="/etc/systemd/timesyncd.conf",
            line="^#\? \?NTP=",
            replace="NTP=" + " ".join(servers),
            present=True
        )
        
        systemd.service(
            name="Enable systemd-timesyncd.service",
            service="systemd-timesyncd.service",
            running=True,
            enabled=True
        )