# -*- coding:Utf-8 -*-


import zipfile
import urllib.request
import io
import os
import shutil
import glob


def main():
    response = input('are you sure you want to update the game ? [Y]es/[N]o\n').upper()

    if response in ('Y', 'YES'):

        url = 'https://github.com/zalt00/Game2/archive/master.zip'

        print(f'getting sources from link "{url}"...')
        filedata = urllib.request.urlopen(url)

        print('reading data...')
        data = filedata.read()
        filelike = io.BytesIO(data)
        z = zipfile.ZipFile(filelike)

        print('extracting...')
        source_dir = os.path.normpath(z.namelist()[0])
        z.extractall()

        print('replacing old files...')

        files = glob.glob(os.path.join(source_dir, '**'), recursive=True)
        for i, file_path in enumerate(files):
            if os.path.isfile(file_path):
                file_path = os.path.normpath(file_path)
                split_path = file_path.split('\\')
                split_path.remove(source_dir)
                new_path = os.path.join(*split_path)

                dir_name = os.path.dirname(new_path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)

                os.replace(file_path, new_path)
                print(f'{i + 1}/{len(files)} done.     ', end='\r')

        print()
        print('cleaning temporary directories...')
        shutil.rmtree(source_dir)

        input('done.')


if __name__ == '__main__':
    main()



