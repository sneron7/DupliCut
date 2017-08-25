import os
import shutil

delete_report_file = '/home/ron/Desktop/duplicut_delete_report.txt'
files_list_to_delete = []
moved_files_folder = '/home/ron/Desktop/Duplicut_moved_files/'

if __name__ == '__main__':
    with open(delete_report_file, "r") as fh:
        for line in fh:
            curr_file = line.replace('\r', '').replace('\n', '').replace(',', '').strip(' ')
            files_list_to_delete.append(curr_file)
            print curr_file

    print '\n\n\n'
    print files_list_to_delete

    if not os.path.exists(moved_files_folder):
        os.mkdir(moved_files_folder)

    for file_to_move in files_list_to_delete:
        file_name = file_to_move.split('/')[-1]
        print file_to_move, '  ', moved_files_folder + file_name
        shutil.move(r'' + file_to_move, moved_files_folder + file_name)
        #shutil.copy(r'' + file_to_move, output_folder + file_name)

