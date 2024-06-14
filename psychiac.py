import os
import sys
import json
import subprocess

def main(current_dir, target_dir):

    # Change to the specified directory
    os.chdir(target_dir)

    # delete changeset.json if present
    if os.path.exists("changeset.json"):
        os.remove("changeset.json")

    # Run the first command in the background and capture stdout and stderr to files
    background_process = subprocess.Popen(f"mitmdump -s {current_dir}/addon.py", shell=True, stdout=open("stdout.log", "w"), stderr=open("stderr.log", "w"))

    # wait until mitmproxy is up by checking if localhost:8080 is up
    while True:
        try:
            subprocess.run(["curl", "localhost:8080"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            break
        except subprocess.CalledProcessError:
            continue

    # Set environment variables for the second command
    os.environ["HTTPS_PROXY"] = "localhost:8080"
    os.environ["HTTP_PROXY"] = "localhost:8080"

    # Run the second command and capture stdout and stderr to files
    subprocess.run(["terraform", "apply", "-state-out=foo", "-auto-approve"], stdout=open("stdout-tf.log", "w"), stderr=open("stderr-tf.log", "w"))
    if os.path.exists("foo"):
        os.remove("foo")

    # Terminate the background process gracefully
    background_process.send_signal(subprocess.signal.SIGINT)

    # Wait for the background process to finish
    background_process.wait()

    # pretty print json in changeset.json
    if os.path.exists("changeset.json"):
        with open("changeset.json", "r") as f:
            print(json.dumps(json.loads(f.read()), indent=4))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python psychiac.py <terraform directory>")
        sys.exit(1)
    main(os.getcwd(), sys.argv[1])
