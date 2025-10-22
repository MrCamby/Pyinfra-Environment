# Option 1

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


# Option 2
# Unschön, wenn man einen Job entfernen möchte muss remove auf true gesetzt werden
# Hinterläst Kommentarreste in der Crontab

# from pyinfra import host
# from pyinfra.operations import crontab

# for jobs in host.data.get("cron"):
#     present = True
#     if "remove" in jobs and jobs["remove"] == True:
#         present = False
        
#     if "@" in jobs["schedule"]:
#         crontab.crontab(
#             name="Setup cron job: {}".format(jobs.get("description")),
#             present=present,
#             user=jobs["user"],
#             command=jobs["command"],
#             special_time=jobs["schedule"],
#             cron_name=jobs.get("description"),
#         )
#     else:
#         time = jobs["schedule"].split(" ")
#         minute = time[0]
#         hour = time[1]
#         day = time[2]
#         month = time[3]
#         weekday = time[4]
#         crontab.crontab(
#             name="Setup cron job: {}".format(jobs.get("description")),
#             present=present,
#             user=jobs["user"],
#             command=jobs["command"],
#             minute=minute,
#             hour=hour,
#             day_of_month=day,
#             month=month,
#             day_of_week=weekday,
#             cron_name=jobs.get("description"),
#         )