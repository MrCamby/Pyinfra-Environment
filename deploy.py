from os import path
from pyinfra import host, local

def include_module(module_name):
    local.include(filename=path.join("modules", f"{module_name}.py"))

if "bareos" in host.groups:
    local.include("modules/postgresql.py")
    local.include("roles/bareos.py")

# if "apt" in host.data.dict():
#     include_module("apt")

# if "ntp" in host.data.dict():
#     include_module("ntp")

# if "nfs" in host.data.dict():
#     include_module("nfs")

# if "mounts" in host.data.dict():
#     include_module("mounts")

# if "cron" in host.data.dict():
#     include_module("cron")

# if "postgresql" in host.data.dict():
#     include_module("postgresql")