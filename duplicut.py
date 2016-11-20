import exception_utils
import os
import time
import hashlib
from operator import itemgetter

path = 'your_folder_path'
report_file = 'report_folder_path/duplicut_report.txt'
ignore_suffixes_list = ['html', 'htm', 'py', 'java', 'h', 'cpp', 'c']
READ_BUFFER_SIZE = 65536
files_dict = {}  # every element contains list of file descriptors (dictionaries)
duplicates_list = []
total_scanned_files = 0
total_scanned_size = 0
total_size_bytes = 0
num_of_deleted_files = 0
script_beginning_time = 0


def _get_sha(file_name):
    sha1 = hashlib.sha1()
    with open(file_name, 'rb') as f:
        while True:
            data = f.read(READ_BUFFER_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def _create_files_dict():
    global files_dict
    global path
    global total_scanned_files
    global total_scanned_size

    print 'Scanning the given folder...'

    for (folder_path, folder_name, file_names) in os.walk(path):
        for f in file_names:
            file_path = os.path.abspath(os.path.join(folder_path, f))
            filename, file_extension = os.path.splitext(file_path)
            file_size = os.path.getsize(file_path)
            total_scanned_files += 1
            total_scanned_size += file_size
            if file_extension in ignore_suffixes_list:
                continue
            stat = os.stat(file_path)
            file_last_modified = stat.st_mtime
            file_name = f
            desc = {'last_modified': file_last_modified, 'path': file_path, 'name': file_name, 'size': file_size}
            if file_size not in files_dict:
                files_dict[file_size] = [desc]
            else:
                files_dict[file_size].append(desc)
                # print 'files dict: ', files_dict


def _find_duplicates():
    global duplicates_list
    global files_dict

    print 'Searching for duplicates...'

    for size in files_dict:  # iterates on all the lists in the files_dict
        lst = files_dict[size]
        if len(lst) > 1:  # make sure that there is a list in the dict and the list size is above 1
            sha_dict = {}  # dictionary of lists (key = sha, list of file descriptors)
            for fdec in lst:  # iterates on all the file descriptors in the list (all with the same size)
                sha = _get_sha(fdec['path'])
                if sha not in sha_dict:
                    sha_dict[sha] = [fdec]
                else:
                    sha_dict[sha].append(fdec)
            for sha in sha_dict:  # iterates on all the lists in the sha dictionary
                sha_list = sha_dict[sha]
                if len(sha_list) > 1:  # only if the list size is above 1
                    sorted_sha_list = sorted(sha_list, key=itemgetter('last_modified'))
                    _print_to_report_file(sha + ' ' + str(sorted_sha_list))
                    duplicates_list.extend(sorted_sha_list[0:-1])


def _delete_duplicates():
    global duplicates_list
    global total_size_bytes
    global num_of_deleted_files

    print 'Deleting duplicates...'

    total_size_bytes = 0
    num_of_deleted_files = 0
    _print_to_report_file('The following files will be deleted:')
    for desc in duplicates_list:
        total_size_bytes += desc['size']
        num_of_deleted_files += 1
        _print_to_report_file('path: ' + desc['path'] + ', ' + 'size: ' + str(desc['size']))
        # TODO: delete the file


def _print_to_report_file(print_str):
    global report_file
    fh = open(report_file, "a")
    fh.write((print_str + '\n'))
    fh.close()


def _print_report_summary():
    print ''
    print 'Done!'
    print 'Total scanned files:', total_scanned_files
    print 'Total scanned size:', str(total_scanned_size/1024.0/1024.0), 'MB'
    print 'Size of deleted files:', str(total_size_bytes/1024.0/1024.0), 'MB'
    print 'Number of deleted files:', num_of_deleted_files
    print 'Script time:', str(time.time() - script_beginning_time), 'sec'


if '__main__' == __name__:
    try:
        script_beginning_time = time.time()
        # TODO: delete prev report file
        _create_files_dict()
        _find_duplicates()
        _delete_duplicates()
        _print_report_summary()
    except:
        exception_utils.print_exception()


# TODO: add flag for delete or just print the files
# TODO: add flag and folder to move the files instead of delete
# TODO: add GUI
