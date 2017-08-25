import exception_utils
import os
import shutil

deleted_folder_path = ['/home/ron/Desktop/duplicut_tester'] # contains the XXX.duplicutted files

if __name__ == '__main__':
    try:
        for path in deleted_folder_path:
            for (folder_path, folder_name, file_names) in os.walk(path):
                for f in file_names:
                    file_path = os.path.abspath(os.path.join(folder_path, f))
                    filename, file_extension = os.path.splitext(file_path)
                    file_extension = file_extension.replace('.', '')
                    if file_extension == 'duplicutted':
                        print file_path

                        deleted_file_path_splitted = file_path.split('/')[0:-1]
                        file_name = file_path.split('/')[-1]
                        file_name = file_name.replace('.duplicutted', '')
                        dest_path = ''
                        for txt in deleted_file_path_splitted:
                            dest_path += txt + '/'

                        is_done = False
                        with open(file_path, "r") as fh:
                            for line in fh:  # it supposed to be only one line
                                recovery_file_path = line
                                shutil.copy(r'' + recovery_file_path, dest_path + file_name)
                                is_done = True

                        if is_done:
                            os.remove(r'' + file_path)

    except:
        exception_utils.print_exception()