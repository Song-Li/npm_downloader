import csv
import subprocess
import json
import argparse
import string
import os
import logging
from tqdm import tqdm

fail_log = logging.getLogger('fail_logger')
fail_handler = logging.FileHandler(filename="fail.log")
fail_log.addHandler(fail_handler)

success_log = logging.getLogger('success_logger')
success_handler = logging.FileHandler(filename="success.log")
success_log.addHandler(success_handler)


def download_package(name, version):
    try:
        print("downloading {}@{}".format(name, version))
        dir_name = "{}@{}".format(name, version)

        archive = "{}-{}.tgz".format(name, version)
        curl_cmd = 'curl --silent --remote-name https://registry.npmjs.org/{}/-/{}'.format(
            name, archive)

        os.system(curl_cmd)
        os.system('mkdir {}'.format(
            dir_name))

        if archive[0] == '@':
            archive = archive.split('/')[1]
        os.system('tar xzf {} --strip-components 1 -C {}'.format(
            archive, dir_name))
        os.system('rm {}'.format(archive))

    except:
        fail_log.info('{}@{} failed \n'.format(name, version))
        return

    success_log.info('{}@{} success \n'.format(name, version))

def download_package_by_link(name, version, link):
    try:
        print("downloading {}".format(name, version))
        if name[0] == '@':
            name = name.replace('/', 'X')

        dir_name = "{}@{}".format(name, version)
        archive = "{}-{}.tgz".format(name, version)
        curl_cmd = 'curl -o {} --remote-name --silent {}'.format(archive, link)
        os.system(curl_cmd)
        if os.path.isdir(dir_name):
            # already downloaded
            fail_log.info('{}@{} skipped\n'.format(name, version))
            return 

        os.system('mkdir -p {}'.format(
            dir_name))

        os.system('tar xzf {} --strip-components 1 -C {}'.format(
            archive, dir_name))
        os.system('rm {}'.format(archive))

    except Exception as e:
        fail_log.info('{}@{} failed {}\n'.format(name, version, e))
        return

def download_latest_by_name(name):
    """
    download the latest version of a package by name
    """
    try:
        os.system("npm pack {}".format(name))
    except Exception as e:
        fail_log.error('{} failed {}\n'.format(name, e))
        return

def handle_json_download(raw_filename, finished_list=None, cut_all=None, cut_cur=None):
    """
    generate csv by raw file
    """
    package_list = []
    print(raw_filename)
    with open(raw_filename, 'r') as rf:
        os.system('mkdir -p packages')
        os.chdir("packages")
        name_list = json.load(rf)
        for line in name_list:
            package_name = line
            package_list.append(line)

        # split the packages
        block_size = int(len(package_list) / cut_all)
        print("block size: ", block_size)
        start_id = cut_cur * block_size
        if cut_cur == cut_all:
            end_id = len(package_list)
        else:
            end_id = (cut_cur + 1) * block_size
        package_list = package_list[start_id : end_id]
        for package_name in package_list:
            """
            print("Getting info for {}".format(package_name))
            download_link = get_download_link(package_name)
            print("download link: ", download_link)
            version_number = get_latest_version(package_name)
            print("link: {} version: {}".format(download_link, version_number))
            """
            if finished_list and package_name in finished_list:
                print("skip {}".format(package_name))
                continue
            try:
                download_latest_by_name(package_name)
                #download_package(package_name, version_number)
                success_log.error("{}".format(package_name))
            except Exception as e:
                fail_log.error("{}".format(package_name))
                print(e)

def handle_csv_downlaod(filename):
    with open(filename, 'r') as fp:
        os.system('mkdir -p packages')
        os.chdir("packages")
        reader = csv.reader(fp, dialect='excel')
        tqdm_bar = tqdm(list(reader))
        for row in tqdm_bar:
            tqdm_bar.set_description("Installing {}".format(row[0].strip()))
            try:
                package_name = row[0].strip()
                package_name = package_name.lower()
                package_version = row[1].strip()
            except:
                fail_log.info('failed to parse npm package')
            download_package(package_name, package_version)

def read_list(file_name):
    """
    read a list of names from a file
    """
    with open(file_name, 'r') as fp:
        package_list = [line.strip() for line in fp.readlines()]
    return package_list

def main():
    parser = argparse.ArgumentParser(
        description='Process some integers.')
    parser.add_argument('-f', help='csv file')
    parser.add_argument('-s', help='successfully finished packages')
    parser.add_argument('-r', help='raw file')
    parser.add_argument('-c', help='cut into n parts')
    parser.add_argument('-i', help='this thread is the ith part')
    args = parser.parse_args()
    filename = args.f  # "./test.csv"
    raw_filename = args.r
    finished_list = None

    if args.s:
        finished_list = read_list(args.s)

    if raw_filename:
        if args.c is not None:
            handle_json_download(raw_filename, finished_list=finished_list, cut_all=int(args.c), cut_cur=int(args.i))
    else:
        handle_csv_downlaod(filename)

def get_latest_version(name):
    out = subprocess.Popen(['npm', 'show', name, 'version'],
           stdout=subprocess.PIPE,
           stderr=subprocess.STDOUT)
    stdout,stderr = out.communicate()
    return stdout.decode('UTF-8').strip()

def get_download_link(name):
    out = subprocess.Popen(['npm', 'show', name, 'dist.tarball'],
           stdout=subprocess.PIPE,
           stderr=subprocess.STDOUT)
    stdout,stderr = out.communicate()
    return stdout.decode('UTF-8').strip()

if __name__ == "__main__":
    main()


