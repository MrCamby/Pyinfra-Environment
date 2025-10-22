from pyinfra import host
from pyinfra.facts.files import File
from pyinfra.operations import files

jobsPerUser = {}
for jobs in host.data.get("cron"):
    if jobs["user"] not in jobsPerUser:
        jobsPerUser[jobs["user"]] = []
    jobsPerUser[jobs["user"]].append(jobs)

for user in jobsPerUser:
    cronFile = host.get_fact(File, "/var/spool/cron/crontabs/{}".format(user))
    if cronFile == False or cronFile == None:
        files.file(
            name="Create cron job file for {}".format(user),
            path="/var/spool/cron/crontabs/{}".format(user),
            user=user,
            group="crontab",
            mode="600",
            touch=True
        )
    
    cronFile = []
    for jobs in jobsPerUser[user]:
        cronFile.append(f"{jobs["schedule"]} {jobs["command"]}")

    files.block(
        name="Setup cron jobs for user {}".format(jobs["user"]),
        path="/var/spool/cron/crontabs/{}".format(jobs["user"]),
        content="\n".join(cronFile), 
)