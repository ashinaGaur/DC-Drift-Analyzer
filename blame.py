import csv
import io
import os
from datetime import datetime
from git import *

# PS Q:\src\Storage-SRP> git blame Q:\src\Storage-SRP\src\Service\PackageRoot\Config\SrpEncryptionConfig.ini^C

rootpath = "Q:\src\Storage-SRP"
repo_path = rootpath

# ini files path
fname = "\src\Service\PackageRoot\Config\SrpEncryptionConfig.ini"
unix_path_fname = "src/Service/PackageRoot/Config/SrpEncryptionConfig.ini"
repo = Repo(rootpath)

# location to create the directories
base_dir_for_repo = "Q:\src\Hack"
dc_name = fname.split('\\')[-1].split(".")[0]
root_folder_for_dc = os.path.join(base_dir_for_repo, dc_name)

# create a root directory
try:
    os.mkdir(root_folder_for_dc+ "_commit_metadata")
    os.mkdir(root_folder_for_dc)
except FileExistsError as ex:
    print(ex)

# fetches all the commits for a file till 50years ago :)
commits = repo.iter_commits('--all', max_count=500, since='50.years.ago',paths=rootpath+fname)
commit_metadata = [] # commit-id (PK kinda), commit-date, author

total_commits = 0
for commit in commits:
    total_commits += 1
    cmmt = repo.commit(commit)
    targetfile = cmmt.tree / unix_path_fname
    version_folder = str(datetime.fromtimestamp(repo.commit(commit).authored_date)).split(" ")[0] + "-" + str(commit)
    version_folder_path = os.path.join(base_dir_for_repo, dc_name, version_folder)

    commit_metadata.append([commit, datetime.fromtimestamp(cmmt.authored_date), cmmt.author])

    try:
        os.mkdir(version_folder_path)
    except FileExistsError as ex:
        print(ex)
    print(version_folder_path + "\\" + dc_name + ".ini")
    with open(version_folder_path + '\\' + dc_name + ".ini", "w+") as target_file:
        with io.BytesIO(targetfile.data_stream.read()) as f:
            for line in f:
                # target_file.write(line.decode('utf-8'))
                config = line.decode('utf-8-sig').strip()
                target_file.write(config)
                target_file.write("\n")

csv_file_path = root_folder_for_dc+ "_commit_metadata" + "\\" + "meta.csv"
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['commit_id','commit_time', 'author'])
    writer.writerows(commit_metadata)

print("Total commits are: ", total_commits)
