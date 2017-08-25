import exception_utils
import os
import time
import hashlib
import shutil
from operator import itemgetter

scan_path_list = None
delete_report_file = None
duplicates_report_file = None
moved_files_folder = None
ignore_suffixes_list = None

READ_BUFFER_SIZE = 65536
files_dict = {}  # every element contains list of file descriptors (file descriptor is a dictionary)
duplicates_list = []
duplicates_report_list = []
total_scanned_files = 0
total_scanned_size = 0
total_ignored_files_size = 0
total_size_bytes = 0
num_of_files_to_delete = 0
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
    global scan_path_list
    global total_scanned_files
    global total_scanned_size
    global total_ignored_files_size

    print 'Scanning the given folder...'

    for path in scan_path_list:
        for (folder_path, folder_name, file_names) in os.walk(path):
            for f in file_names:
                file_path = os.path.abspath(os.path.join(folder_path, f))
                filename, file_extension = os.path.splitext(file_path)
                try:
                    file_size = os.path.getsize(file_path)
                except OSError:
                    continue  # if permissions denided because of another user or group
                total_scanned_files += 1
                total_scanned_size += file_size
                file_extension = file_extension.replace('.','')
                if file_extension in ignore_suffixes_list:
                    total_ignored_files_size += file_size
                    continue
                stat = os.stat(file_path)
                file_last_modified = stat.st_mtime
                file_name = f
                desc = {'last_modified': file_last_modified, 'path': file_path, 'name': file_name, 'size': file_size}
                if file_size not in files_dict:
                    files_dict[file_size] = [desc]
                else:
                    files_dict[file_size].append(desc)
                    #print 'files dict: ', files_dict


def _find_duplicates():
    global duplicates_list
    global files_dict
    global duplicates_report_list

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
                    duplicates_list.extend(sorted_sha_list[0:-1]) # all elements in the list except the last one (the newest)
                    # print 'newest file - ' + sha + ' ' + str(sorted_sha_list[-1])
                    # print 'last updated:', str(sorted_sha_list[-1]['path']), '||| Duplicates: ==>> ', str(sorted_sha_list[0:-1])
                    _print_to_duplicates_report_file(str(sorted_sha_list[-1]['path']) + ':' + '\n' + '-' * len(str(sorted_sha_list[-1]['path'])) + '\n' + str(sorted_sha_list[0:-1]))
                    duplicates_report_list.append((sorted_sha_list[-1]['path'],sorted_sha_list[0:-1])) # newest file: duplicates_report_list[0][0], all the oldest files:duplicates_report_list[0][1][0 to N]['path']


def _create_delete_duplicates_report():
    global duplicates_list
    global total_size_bytes
    global num_of_files_to_delete

    print 'Creating duplicates report...'

    total_size_bytes = 0
    num_of_files_to_delete = 0
    for desc in duplicates_list:
        total_size_bytes += desc['size']
        num_of_files_to_delete += 1
        _print_to_delete_report_file(desc['path'] + ', ')  # + 'size: ' + str(desc['size']))


# list of files to be deleted (contains only the oldest files to be deleted)
def _print_to_delete_report_file(print_str):
    global delete_report_file
    fh = open(delete_report_file, "a")
    fh.write((print_str + '\n'))
    fh.close()


# each row is the newer file (not deleted) and a list of older files to delete
def _print_to_duplicates_report_file(print_str):
    global duplicates_report_file
    fh = open(duplicates_report_file, "a")
    fh.write((print_str + '\n\n'))
    fh.close()


def _do_move():
    global duplicates_report_list

    if not os.path.exists(moved_files_folder):
        os.mkdir(moved_files_folder)

    for dup_items in duplicates_report_list:
        newest_file_name = dup_items[0]
        oldest_files_list =  dup_items[1]
        for dup_file in oldest_files_list:
            file_name = dup_file['path'].split('/')[-1]
            # print dup_file['path'], '  ', moved_files_folder + file_name
            shutil.move(r'' + dup_file['path'], moved_files_folder + file_name)
            with open(dup_file['path'] + '.duplicutted', "w") as deleted_file_marker:
                deleted_file_marker.write(newest_file_name)


def _do_copy():
    global duplicates_report_list

    if not os.path.exists(moved_files_folder):
        os.mkdir(moved_files_folder)

    for dup_items in duplicates_report_list:
        newest_file_name = dup_items[0]
        oldest_files_list =  dup_items[1]
        for dup_file in oldest_files_list:
            file_name = dup_file['path'].split('/')[-1]
            # print dup_file['path'], '  ', moved_files_folder + file_name
            shutil.copy(r'' + dup_file['path'], moved_files_folder + file_name)
            with open(dup_file['path'] + '.duplicutted', "w") as deleted_file_marker:
                deleted_file_marker.write(newest_file_name)


def _do_delete():
    global duplicates_report_list

    if not os.path.exists(moved_files_folder):
        os.mkdir(moved_files_folder)

    for dup_items in duplicates_report_list:
        newest_file_name = dup_items[0]
        oldest_files_list =  dup_items[1]
        for dup_file in oldest_files_list:
            file_name = dup_file['path'].split('/')[-1]
            os.remove(r'' + dup_file['path'])
            with open(dup_file['path'] + '.duplicutted', "w") as deleted_file_marker:
                deleted_file_marker.write(newest_file_name)


def _print_report_summary():
    global total_scanned_files
    global total_scanned_size
    global total_size_bytes
    global num_of_files_to_delete
    global script_beginning_time
    global total_ignored_files_size

    print ''
    print 'Done!'
    print 'Total scanned files:', total_scanned_files
    print 'Total scanned size:', str(total_scanned_size/1024.0/1024.0), 'MB'
    print 'Size files to delete:', str(total_size_bytes/1024.0/1024.0), 'MB'
    print 'Ignored files size:', str(total_ignored_files_size/1024.0/1024.0), 'MB'
    print 'Number of files to delete:', num_of_files_to_delete
    print 'Run time:', str(time.time() - script_beginning_time), 'sec'


# working_mode: M = move, D = delete, P = print, C = copy
def run_dupli_cut(working_mode, scan_list, del_report_file, dup_report_file, moved_folder, ignore_suffixes):
    global script_beginning_time
    global scan_path_list
    global delete_report_file
    global duplicates_report_file
    global moved_files_folder
    global ignore_suffixes_list

    scan_path_list = scan_list
    delete_report_file = del_report_file
    duplicates_report_file = dup_report_file
    moved_files_folder = moved_folder
    ignore_suffixes_list = ignore_suffixes

    script_beginning_time = time.time()
    # TODO: delete prev report file
    _create_files_dict()
    _find_duplicates()
    _create_delete_duplicates_report()
    if working_mode == 'M':
        print 'Mode Mode!!!'
        _do_move()
    elif working_mode == 'C':
        print 'Copy Mode!!!'
        _do_copy()
    elif working_mode == 'P':
        print 'Print Mode!!!'
    elif working_mode == 'D':
        print 'Delete Mode!!!'
        _do_delete()
    _print_report_summary()


if '__main__' == __name__:
    try:
        mode = 'M'
        scan_list = ['/home/ron/Desktop/duplicut_tester']  # ['/home/ron/Dropbox/MyBackup']
        del_report_file = '/home/ron/Desktop/duplicut_delete_report.txt'
        dup_report_file = '/home/ron/Desktop/duplicut_duplacates_report.txt'
        moved_folder = '/home/ron/Desktop/Duplicut_moved_files/'
        ignore_suffixes = ['html', 'htm', 'py', 'java', 'h', 'hpp', 'cpp', 'c', 'duplicutted']

        run_dupli_cut(mode, scan_list, del_report_file, dup_report_file, moved_folder, ignore_suffixes)
    except:
        exception_utils.print_exception()


# TODO: add argv for paths, flags, ignore_list
# TODO: add argv for delete / move / copy / print the files
# TODO: add GUI
