import os
import sys
import json
import time
import requests
import subprocess

def main(current_dir, target_dir):

    # Change to the specified directory
    os.chdir(target_dir)

    # delete changeset.json if present
    if os.path.exists("changeset.json"):
        os.remove("changeset.json")

    print("Starting mitm proxy with the addon...")
    # Run the first command in the background and capture stdout and stderr to files
    background_process = subprocess.Popen(f"mitmdump -s {current_dir}/addon.py", shell=True, stdout=open("stdout.log", "w"), stderr=open("stderr.log", "w"))
    print("Done.")

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

    print("Running terraform and intercepting calls to the provider...")
    # Run the second command and capture stdout and stderr to files
    subprocess.run(["terraform", "apply", "-state-out=foo", "-auto-approve"], stdout=open("stdout-tf.log", "w"), stderr=open("stderr-tf.log", "w"))
    print("Done.")
    if os.path.exists("foo"):
        os.remove("foo")

    if os.path.exists("foo.backup"):
        os.remove("foo.backup")

    # Terminate the background process gracefully
    background_process.send_signal(subprocess.signal.SIGINT)

    # Wait for the background process to finish
    background_process.wait()

    # pretty print json in changeset.json
    changeset = {}
    if os.path.exists("changeset.json"):
        with open("changeset.json", "r") as f:
            changeset = json.loads(f.read())

    if changeset.get('assets') != []:
        os.environ["HTTPS_PROXY"] = ""
        os.environ["HTTP_PROXY"] = ""
        changeset["threat"] = 0.900
        caizen_url = "http://localhost:8000/changeset"
        print("Sending changeset to CAIZEN...")
        response = requests.post(caizen_url, data=json.dumps(changeset), headers={'Content-type': 'application/json'}) 
        print("Done.")
        time.sleep(1)
        print("Printing attack paths...")
        time.sleep(1)
        # print(json.dumps(response.json(), indent=2))
        with open('response.json', 'w') as file:
            json.dump(response.json(), file)

        os.system("cat response.json | jq -r '.result'")
    else:
        print("No terraform changes captured")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python psychiac.py <terraform directory>")
        sys.exit(1)
    main(os.getcwd(), sys.argv[1])
