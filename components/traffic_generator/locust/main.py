
from os import environ
from subprocess import getstatusoutput
from signal import signal, SIGTERM


OUTPUT = "shared/locust-$HOSTNAME.csv"
LOCUSTFILE = "locustfile.py"


def conf_locust():

    # arguments
    dest = environ.get("DESTINATION_IP")
    proto = environ.get("PROTOCOL")
    pages = environ.get("PAGES").split(",")

    between_min = environ.get("WAIT_BETWEEN_PAGES_MIN")
    between_min = float(between_min)

    between_max = environ.get("WAIT_BETWEEN_PAGES_MAX")
    between_max = float(between_max)

    # write locust configuration
    with open(LOCUSTFILE, "w") as file:
        file.write("from locust import FastHttpUser, between, task\n")
        file.write("class WebsiteUser(FastHttpUser):\n")
        file.write(f"\thost = '{proto}://{dest}'\n")
        file.write(f"\twait_time = between({between_min},{between_max})\n")

        for i in range(len(pages)):
            page = pages[i]

            file.write("\t@task\n")
            file.write(f"\tdef page{i}(self):\n")
            file.write(f"\t\tself.client.get('/{page}')\n")


def run_locust():

    # arguments
    connection_max = environ.get("MAX_CONNECTIONS")
    connection_max = int(connection_max)

    connection_rate = environ.get("RATE_OF_NEW_CONNECTIONS")
    connection_rate = int(connection_rate)

    signal(SIGTERM, stop)  # successful exit

    # run locust
    command = f"locust -f {LOCUSTFILE} --headless -u {connection_max} -r {connection_rate} "
    command += "--csv-full-history --csv csv/results 1> /dev/null"
    getstatusoutput(command)

    stop(None, None)  # unsuccessful exit


def stop(signal, frame):
    s, _ = getstatusoutput("pkill locust")
    getstatusoutput(f"cp csv/results_stats_history.csv {OUTPUT}")
    exit(s)


if __name__ == "__main__":
    conf_locust()
    run_locust()
