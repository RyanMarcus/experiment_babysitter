#! /usr/bin/env python3
# < begin copyright > 
# Copyright Ryan Marcus 2019
# 
# This file is part of experiment_babysitter.
# 
# experiment_babysitter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# experiment_babysitter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with experiment_babysitter.  If not, see <http://www.gnu.org/licenses/>.
# 
# < end copyright > 

import http.client
import os
import subprocess
import sys
import time
import urllib

PUSHOVER_TOKEN = os.environ["PUSHOVER_TOKEN"]
PUSHOVER_USER = os.environ["PUSHOVER_USER"]

def notification(title, msg):
    try:
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request(
            "POST",
            "/1/messages.json",
            urllib.parse.urlencode(
                {
                    "token": PUSHOVER_TOKEN,
                    "user": PUSHOVER_USER,
                    "title": title,
                    "message": msg,
                }
            ),
            {"Content-type": "application/x-www-form-urlencoded"},
        )
    except:
        pass


def get_out_names():
    cnt = 0
    while os.path.exists(f"expr_stdout{cnt}") or os.path.exists(f"expr_stderr{cnt}"):
        cnt += 1

    return (f"expr_stdout{cnt}", f"expr_stderr{cnt}")


filenames = get_out_names()
stdout_f = open(filenames[0], "w")
stderr_f = open(filenames[1], "w")

os.environ["PYTHONUNBUFFERED"] = "TRUE"

cmd = " ".join(sys.argv[1:])
proc = subprocess.Popen(cmd, shell=True, stdout=stdout_f, stderr=stderr_f)
pid = proc.pid
hostname = os.uname().nodename
our_name = f"Babysitter on {hostname}"


time.sleep(1)
if proc.poll() is not None:
    print("Process terminated before 1 second elapsed!")
    exit(1)

print("Starting monitoring.")
print("stdout:", filenames[0])
print("stderr:", filenames[1])

notification(our_name, f"PID {pid} launched on {hostname}. Command: {cmd}")

last_notify = time.time()

while True:
    time.sleep(1)
    rc = proc.poll()

    if rc is None:
        # still running!
        continue

    curr_time = time.time()
    if curr_time - last_notify > 30 * 60:
        notification(our_name, f"Process {pid} still running...")

    # otherwise, the process has finished!
    notification(our_name, f"Process completed with return code {rc}")
    break
