from os import path
from pyinfra import host, local

local.include("roles/bareos.py")
