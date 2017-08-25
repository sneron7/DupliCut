import exception_utils
import os
import shutil

deleted_file_path = '/home/ron/Desktop/duplicut_tester/1/11/11.txt.duplicutted' # the XXX.duplicutted file


if __name__ == '__main__':
    try:
        deleted_file_path_splitted = deleted_file_path.split('/')[0:-1]
        file_name = deleted_file_path.split('/')[-1]
        file_name = file_name.replace('.duplicutted', '')
        dest_path = ''
        for txt in deleted_file_path_splitted:
            dest_path += txt + '/'

        is_done = False
        with open(deleted_file_path, "r") as fh:
            for line in fh:  # it supposed to be only one line
                recovery_file_path = line
                shutil.copy(r'' + recovery_file_path, dest_path + file_name)
                is_done = True

        if is_done:
            os.remove(r'' + deleted_file_path)

    except:
        exception_utils.print_exception()