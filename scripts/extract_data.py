import os
import tarfile

from argparse import ArgumentParser

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-d", type=str, help="represents the directory ocntaining the zip files")
    args = parser.parse_args()
    
    # data directoyr entered by user
    DATA_DIR = args.d
    tar_files = os.listdir(DATA_DIR)

    print(len(tar_files))

    for tar_file in tar_files:
        # extract files from .tar file
        with tarfile.open(f'{DATA_DIR}/{tar_file}') as tar_ref:
            tar_ref.extractall(DATA_DIR)

        # delete .tar file after extraction
        path = os.path.join(DATA_DIR, tar_file)
        os.remove(path)


