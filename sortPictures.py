import sys
import os
import platform
import re
import shutil
import time
#from PIL import Image

def modified_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getmtime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime

def main():
    if len(sys.argv) == 1:
        print('Error: No pictures directory specified.')
        exit(1)

    print(sys.argv)
        
    picsDir = sys.argv[1]

    print('Scanning pictures directory: ' + picsDir)

    pics = []
    for f in os.listdir(picsDir):
        if os.path.isfile(os.path.join(picsDir, f)):
            pics.append(f)

    print('Found '+str(len(pics))+' pictures')

    print('Moving pictures...')
    moved = 0

    # Handle all the files that have the date in the file name.
    do_by_date_in_file_name = True
    if do_by_date_in_file_name:
        for p in pics:
            x = re.search(r'(19|20|21)\d\d(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])', p)
            if x:
                dir = p[x.start():x.end()]
                dir = dir[0:4] + '-' + dir[4:6] + '-' + dir[6:8]
                destDir = os.path.join(os.path.join(picsDir, dir))
                if not os.path.exists(destDir):
                    os.makedirs(destDir)
                dest = os.path.join(destDir, p)
                #print(os.path.join(picsDir, p) + '  ==>  ' + dest)
                shutil.move(os.path.join(picsDir, p), dest)
                moved += 1
                pics.remove(p)

    do_by_exif_meta_data = False
    if do_by_exif_meta_data:
        # Handle any files without the date in the file name.
        # This will attempt to use the "date taken" EXIF meta data.
        start_count = moved
        end_count = -1
        while start_count != end_count:
            start_count = moved
            for p in pics:
                exif_data = None
                date = None
                try:
                    exif_data = Image.open(os.path.join(picsDir, p))._getexif()
                    date = str(exif_data[306]).split()[0]
                except OSError:
                    # Do nothing, the file was probably not an image with EXIF data.
                    continue
                except AttributeError:
                    # Do nothing, the file was probably not an image with EXIF data.
                    continue
                except KeyError:
                    # Do nothing, the EXIF meta data did not have the field we wanted.
                    continue
                except TypeError:
                    # Do nothing, the EXIF meta data was null.
                    continue
                if exif_data:
                    date_split = date.split(':')
                    dir = date_split[0] + '-' + date_split[1] + '-' + date_split[2]
                    destDir = os.path.join(os.path.join(picsDir, dir))
                    if not os.path.exists(destDir):
                        os.makedirs(destDir)
                    dest = os.path.join(destDir, p)
                    shutil.move(os.path.join(picsDir, p), dest)
                    moved += 1
                    pics.remove(p)
            end_count = moved

    do_by_created_data = False
    if do_by_created_data:
        # Handle any remaining files by looking at the "created" date.
        script_path = os.path.realpath(__file__)
        for p in pics:
            date = None
            date = modified_date(os.path.join(picsDir, p))
            dir = time.strftime('%Y-%m-%d', time.localtime(date))
            destDir = os.path.join(os.path.join(picsDir, dir))
            if not os.path.exists(destDir):
                os.makedirs(destDir)
            dest = os.path.join(destDir, p)
            shutil.move(os.path.join(picsDir, p), dest)
            moved += 1
            pics.remove(p)

    print('Moved ' + str(moved) + ' pictures.')
    print('Did not move ' + str(len(pics)) + ' pictures.')
    print('Done')

if __name__ == "__main__":
    main()
