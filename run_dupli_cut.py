from dupli_cut import run_dupli_cut
import exception_utils

if '__main__' == __name__:
    try:
        mode = 'M'
        scan_list = ['/home/ron/Desktop/duplicut_tester']
        del_report_file = '/home/ron/Desktop/duplicut_delete_report.txt'
        dup_report_file = '/home/ron/Desktop/duplicut_duplacates_report.txt'
        moved_folder = '/home/ron/Desktop/Duplicut_moved_files/'
        ignore_suffixes = ['html', 'htm', 'py', 'java', 'h', 'hpp', 'cpp', 'c', 'duplicutted']

        run_dupli_cut(mode, scan_list, del_report_file, dup_report_file, moved_folder, ignore_suffixes)
    except:
        exception_utils.print_exception()