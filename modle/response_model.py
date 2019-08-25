from threading import Thread

import psycopg2
import datetime

#connect to data using psycopg2 library
conn = psycopg2.connect("host='localhost' port='5432' dbname='postgres' user='postgres' password='root'")
import sys
import os
import time

cur = conn.cursor()

if sys.version_info >= (3,):
    import urllib.request as urllib2
    import urllib.parse as urlparse
else:
    import urllib2
    import urlparse


class Compute(Thread):
    def __init__(self, request, url, id):
        Thread.__init__(self)
        self.request = request
        self.url = url
        self.id = id
    def run(self):
        """
        Download and save a file specified by url to dest directory,
        """

        u = urllib2.urlopen(self.url)
        dest = None
        scheme, netloc, path, query, fragment = urlparse.urlsplit(self.url)
        filename = os.path.basename(path)
        print("file name---------",filename)
        if not filename:
            filename = 'downloaded.file'
        if dest:
            filename = os.path.join(dest, filename)

        with open(filename, 'wb') as f:
            meta = u.info()

            meta_func = meta.getheaders if hasattr(meta, 'getheaders') else meta.get_all # get all meta data from url
            meta_length = meta_func("Content-Length")  # find out the lenght of header
            file_size = None
            if meta_length:
                file_size = int(meta_length[0]) # total file size
            print("Downloading: {0} Bytes: {1}".format(self.url, file_size))

            file_size_dl = 0
            block_sz = 8192 # divide block size(how may block you want to dowlonad file at the time)

            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer) # store the file to file directory or remote directory

                status = "{0:16}".format(file_size_dl)
                start = time.time()
                if file_size:
                    status += "   [{0:6.2f}%]".format(file_size_dl * 100 / file_size) # measure status every time
                    percentage_complete = "   {0:6.2f}".format(file_size_dl * 100 / file_size)  # complate percentage

                    estimate_time_to_complate = str(datetime.timedelta(seconds=((time.time()-start) * (100-float(percentage_complete)))))  # calculate estimate time for downloading

                    # save details to database
                    """
                    store file data based on file name
                    """
                    exe = """select file_name from downloadFileData where file_name = '{0}';""".format(filename)
                    cur.execute(exe)
                    response = cur.fetchall()

                    #if len(response) != 0:
                    reamaning_file_size = file_size - file_size_dl
                    if len(response) == 0:
                        # insert data to database first time
                        exe = """INSERT INTO downloadFileData (id, total_file_size, download_file_size, remaning_file_size, status, eta, file_name) VALUES ({0}, '{1} bytes', '{2} bytes', '{3} bytes', '{4}', '{5}', '{6}');""".format(self.id,file_size, file_size_dl, reamaning_file_size, 'downloading', estimate_time_to_complate, filename)

                        cur.execute(exe)
                        conn.commit()
                    elif filename in response:
                        # update data every time(every buffer downloading)
                        exe ="""UPDATE downloadFileData SET download_file_size='{0} bytes',remaning_file_size='{1} bytes',status='{2}',eta='{3}' WHERE file_name = '{4}';""".format(file_size_dl, reamaning_file_size, "downloading",estimate_time_to_complate, filename)
                        cur.execute(exe)
                        conn.commit()
                    elif file_size == file_size_dl:
                        # finish dwonload then update complete status
                        exe = """UPDATE downloadFileData SET download_file_size='{0} bytes',remaning_file_size='{1} bytes',status='{2}',eta='{3}' WHERE file_name = '{4}';""".format(
                            file_size_dl, reamaning_file_size, "finished", estimate_time_to_complate, filename)
                        cur.execute(exe)
                        conn.commit()
                    print("every time status", "{0:16}".format(file_size_dl),"  [{0:6.2f}%]".format(file_size_dl * 100 / file_size),  file_size_dl/ 1024, "Kb")
                status += chr(13)
                print(status, end="")
            print( )

        return filename


# check file exist in database for not
"""
this function check if file already downloaded or not
"""
def fileExist(filename):
    exe = """select file_name from downloadFileData where file_name = '{0}';""".format(filename)
    cur.execute(exe)
    response = cur.fetchall()
    if len(response)==0:
        return False
    else:
        return True


# check if
"""
this is used for checking id(if id exist or not for checking status)
"""
def checkid(id):
    exe = """select file_name from downloadFileData where id = '{0}';""".format(id)
    cur.execute(exe)
    response = cur.fetchall()
    if len(response)==0:
        return False
    else:
        return True


# check status for file based on id
"""
check file(download) status
"""
def status(id):
    exe = """select * from downloadFileData where id = {0};""".format(id)
    cur.execute(exe)
    response = cur.fetchall()
    return response


