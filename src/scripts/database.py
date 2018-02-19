import os
import sys
import json
import time
import fetch

from tqdm import tqdm 

cmd = sys.argv[1] # commands: build->(get samples, populate database), map->(populate/update database map)

# populate/update database map
def map_db():
    db_map = {"newest":0, "timestamp":0, "files":{}}

    # Populate database map
    for sample in samples:
        db_map["files"][sample] = {}

        db_path = "{0}/database/Run{1}/{2}".format(os.getcwd(), year, sample)
        database = os.listdir(db_path)

        newest = 0
        for f in database:
            last_mod = os.path.getmtime("{0}/{1}".format(db_path, f))
            if last_mod > newest:
                newest = last_mod

            db_map["files"][sample][f.split(".root")[0]] = last_mod

        db_map["newest"] = newest

    # Update database map timestamp
    db_map["timestamp"] = time.time()

    # Dump database map into json
    with open("{0}/db_map.json".format(os.getcwd()), "w") as fhout:
        json.dump(db_map, fhout, sort_keys = True, indent = 4, separators = (',',':'))

    # Ensure database map has proper permissions
    os.system("chmod 755 db_map.json")

    return

# get samples, populate/structure database
def build_db():
    # User input loop
    while True:
        print("Enter the number of files you would like downloaded (starting from the newest DQM file).")
        print("If you would like to download ALL files, enter 'all'")
        limit_inp = raw_input("Input: ")
        if limit_inp == "all":
            print("\nWARNING: This process may take some time.")
            confirm = raw_input("Continue? y/n: ")
            if confirm == "y":
                limit = False
                break
            else:
                print("\n")
                continue
        else:
            try:
                limit = int(limit_inp)
                break
            except ValueError:
                print("ERROR: Please enter a number or 'all'.\n")
                continue

    # Load configs
    with open("{0}/configs.json".format(os.getcwd())) as config_file:
        config = json.load(config_file)
    sample = config["sample"]
    year = config["year"]

    print("Building database...")
    files_found = 0
    for sample in tqdm(samples):
        print("Retrieving list of runs...")
        runs = fetch.get_runs(str(year), sample)
        print("\n\n\nRetrieved list of runs. There are {0} files available for download.".format(len(runs)))
        print("Downloading files...")
        for i in tqdm(range(0, limit)):
            run = runs[i]
            is_success, fail_reason = fetch.fetch(str(run), "")
            if not is_success:
                print("ERROR: {0}".format(fail_reason))
                return
            else:
                files_found += 1

        print("\n\nFinished combing {0}. Found: {1}/{2}".format(sample, files_found, limit))
    print("Finished building database.")
    return

if __name__ == "__main__":
    if cmd == "map": map_db()
    elif cmd == "build": build_db()