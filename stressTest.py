import argparse
import subprocess
import time
import os
import sys
from config import Config


def run_stress_test(
    num_submissions,
    submission_delay,
    autograder_image,
    output_file,
    tango_port,
    tango_path,
    job_name,
    job_path,
):
    with open(output_file, "a") as f:
        f.write(f"Stress testing with {num_submissions} submissions\n")
        for i in range(1, num_submissions + 1):
            command = [
                "python3",
                os.path.join(tango_path, "clients/tango-cli.py"),
                "-P",
                str(tango_port),
                "-k",
                "test",
                "-l",
                job_name,
                "--runJob",
                job_path,
                "--image",
                autograder_image,
            ]
            subprocess.run(command, stdout=f, stderr=f)
            f.write(f"Submission {i} submitted \n")

            if submission_delay > 0:
                time.sleep(submission_delay)

    sys.exit()


def get_metrics(output_file):
    if Config.LOGFILE == None:
        print("Make sure logs are recorded in a log file")

    job_times = []
    with open(Config.LOGFILE, "r") as f:
        for line in f:
            if "finished after " in line:
                start = line.find("finished after ") + len("finished after ")
                seconds = int(line[start:].split()[0])
                job_times.append(seconds)

    with open(output_file, "a") as f:
        if len(job_times) == 0:
            print("No jobs have been completed")
        else:
            avg = sum(job_times) / len(job_times)
            f.write(f"Average job time is {avg} seconds \n")

    sys.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stress test script for Tango")
    parser.add_argument(
        "--num_submissions", type=int, default=10, help="Number of submissions"
    )
    parser.add_argument(
        "--submission_delay", type=float, default=1.0, help="Delay between submissions"
    )
    parser.add_argument(
        "--autograder_image", type=str, required=True, help="Autograder image"
    )
    parser.add_argument(
        "--output_file", type=str, default="stress_test.out", help="Output file"
    )
    parser.add_argument(
        "--tango_port", type=int, default=4567, help="Tango server port"
    )
    parser.add_argument("--tango_path", type=str, required=True, help="Path to Tango")
    parser.add_argument("--job_name", type=str, required=True, help="Name of the job")
    parser.add_argument("--job_path", type=str, required=True, help="Path to the job")
    parser.add_argument(
        "--get_metrics",
        type=bool,
        default=False,
        help="Set to true to get metrics, does not create new jobs",
    )

    args = parser.parse_args()

    if args.get_metrics:
        get_metrics(args.output_file)
    else:
        run_stress_test(
            args.num_submissions,
            args.submission_delay,
            args.autograder_image,
            args.output_file,
            args.tango_port,
            args.tango_path,
            args.job_name,
            args.job_path,
        )
