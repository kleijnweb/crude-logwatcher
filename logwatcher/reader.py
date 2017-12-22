import glob
import json
import os
from typing import List

from logwatcher.output import OutputBuffer
from logwatcher.parser import LineParser


class LogReader(object):
    def __init__(self, paths: List[str], parser: LineParser, buffer: OutputBuffer, work_file_path: str = None):
        self.work_file_path = work_file_path
        self.paths = paths
        self.buffer = buffer
        self.parser = parser
        self.work_file = None

    def read(self):

        if self.work_file_path:
            self.work_file = open(self.work_file_path, os.O_EXCL | os.O_RDWR)
        else:
            import tempfile
            self.work_file = tempfile.TemporaryFile()

        s = self.work_file.read()
        self.work_file.truncate(0)
        old_work = json.loads(s) if s else {}
        new_work = {}

        try:
            log_paths = filter(None, self.paths)
            for path_glob in log_paths:
                files = glob.glob(path_glob)
                files.sort(key=os.path.getmtime, reverse=True)
                try:
                    logfile = files[0]
                except KeyError:
                    continue

                fpos = old_work.get(logfile, 0)
                try:
                    f = open(logfile)
                    if fpos > 0:
                        f.seek(fpos)
                    while True:
                        try:
                            line = f.readline()
                            fpos += len(line)
                            new_work[logfile] = fpos
                            line = line.rstrip()
                            if not line:
                                break
                            record = self.parser.parse(line, logfile)
                            if record:
                                self.buffer.add(record)
                        except Exception as error:
                            raise RuntimeError(
                                "Processing line '{0}' from file '{1}' at pos '{2}' failed".format(line, logfile, fpos),
                            ) from error
                finally:
                    f.close()

                self.buffer.flush()
        finally:
            self.work_file.write(json.dumps(new_work))
            self.work_file.close()
