bareos = [
    ("10.0.30.244", {
        "ssh_user": "root",
        "bareos": {
            "db": {
                "db_name": "bareos",
                "db_user": "bareos",
                "db_password": "bareos"
            },
            "catalogs": [
                "1234"
            ],
            "director_tag": "dir0",
            "devices": 256,
            "mountpoint": "/mnt/nfs",
            "storage_daemon_tag": "sd0",
            "storage_address": "bareos.local"
        }
    })
]

example = [
    ("10.0.30.244", {"ssh_user": "root"})
]

# example_override = [
#     ("10.0.30.244", {
#         "ssh_user": "root",
#         "apt": {
#             "auto_upgrade": ["tcpdump"],
#             "install": ["qemu-guest-agent"],
#             "mark": ["postgresql-common"],
#         },
#         "cron": [
#             {"user": "root", "command": "date", "schedule": "*/5 * * * *"},
#             {"user": "root", "command": "cat /etc/os-release", "schedule": "*/5 * * * *"},
#         ],
#         "iptables": {
#             "v4": [
#                 {"table"}
#             ]
#         },
#         "mounts": [
#             {"src": "127.0.0.1:/nfs-share" , "dst": "/nfs-test", "type": "nfs", "options": ["rw"]},
#         ],
#         "nfs": [
#             {"path": "/nfs-share", "clients": [
#                 {"remote": "127.0.0.1", "options": "rw"}
#             ]}
#         ],
#         "postgresql": {
#             "version": "14",
#             "config": {
#                 "postgresql.conf": {
#                     "max_connections": "40",
#                     "shared_buffers": "3GB",
#                     "effective_cache_size": "9GB",
#                 }
#             }
#         }
#     })
# ]