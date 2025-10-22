example = [
    ("10.0.30.244", {"ssh_user": "root"})
]

example_override = [
    ("10.0.30.244", {
        "ssh_user": "root",
        "apt": {
            "auto_upgrade": ["tcpdump"],
            "install": ["qemu-guest-agent"],
            "mark": ["postgresql-common"],
        },
        # Option 1
        "cron": [
            {"user": "root", "command": "date", "schedule": "*/5 * * * *"},
            {"user": "root", "command": "cat /etc/os-release", "schedule": "*/5 * * * *"},
        ],
        # Option 2
        # "cron": [
        #     {"description": "Test 1", "user": "root", "command": "date", "schedule": "*/5 * * * *"},
        #     {"description": "Test 2", "user": "root", "command": "cat /etc/os-release", "schedule": "*/5 * * * *", "remove": True},
        # ],
        "iptables": {
            "v4": [
                {"table"}
            ]
        },
        "mounts": [
            {"src": "127.0.0.1:/nfs-share" , "dst": "/nfs-test", "type": "nfs", "options": ["rw"]},
        ],
        "nfs": [
            {"path": "/nfs-share", "clients": [
                {"remote": "127.0.0.1", "options": "rw"}
            ]}
        ],
        "postgresql": {
            "version": "14",
            "config": {
                "postgresql.conf": {
                    "max_connections": "40",
                    "shared_buffers": "3GB",
                    "effective_cache_size": "9GB",
                }
            }
        }
    })
]