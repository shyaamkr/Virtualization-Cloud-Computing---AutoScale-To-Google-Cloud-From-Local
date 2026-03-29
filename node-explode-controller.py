import time
import subprocess
from collections import deque
import psutil

CPU_LIMIT=80.0
RAM_LIMIT=85.0
CHECK_INTERVAL=10
WINDOW_PERIOD=2
COOLING_PERIOD=10


GCPROJECT_ZONE="asia-south1-a"
GCBUCKET="vcc-assignment3-from-host"

sample_duration=int((WINDOW_PERIOD * 60) / CHECK_INTERVAL)
cpu_window = deque(maxlen=sample_duration)
ram_window = deque(maxlen=sample_duration)

last_trigger_time = 0

def fn_avg(values):
    return sum(values) / len(values) if values else 0.0


def trigger_gcp_instance():
    instance_name = f"vcc3-explode-node-{int(time.time())}"
    cmd = f"""
    gcloud compute instances create {instance_name} \
            --zone={GCPROJECT_ZONE} \
            --machine-type=e2-micro \
            --image-family=ubuntu-2204-lts \
            --image-project=ubuntu-os-cloud \
            --metadata=startup-script-url=gs://{GCBUCKET}/scripts/startup.sh
    """
    print(f"\n[ALERT] Launching Additional Explode Node in Cloud : {instance_name} \n")
    subprocess.run(["bash","-lc",cmd], check=False)


while True:
    cpu=psutil.cpu_percent(interval=1)
    ram=psutil.virtual_memory().percent

    cpu_window.append(cpu)
    ram_window.append(ram)

    cpu_avg = fn_avg(cpu_window)
    ram_avg = fn_avg(ram_window)

    print(f"CPU now={cpu:.1f}% avg={cpu_avg:.1f}% | RAM now={ram:.1f}% avg={ram_avg:.1f}%")


    now = time.time()
    cooldown_ok = (now - last_trigger_time) > (COOLING_PERIOD * 60) 

    if len(cpu_window) == sample_duration and cooldown_ok:
        if cpu_avg > CPU_LIMIT or ram_avg > RAM_LIMIT:
            trigger_gcp_instance()
            last_trigger_time = now
            cpu_window.clear()
            ram_window.clear()

    time.sleep(CHECK_INTERVAL)
