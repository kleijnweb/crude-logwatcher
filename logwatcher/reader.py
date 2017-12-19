import glob
import json
import os
from typing import List

from logwatcher.parser import LineParser
from logwatcher.output import OutputBuffer


class LogReader(object):
    def __init__(self, workfile: str, paths: List[str], parser: LineParser, buffer: OutputBuffer):
        self.workfile = workfile
        self.paths = paths
        self.buffer = buffer
        self.parser = parser

    def read(self):
        work_file = open(self.workfile, 'a+')
        s = work_file.read()
        work_file.truncate(0)
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
                            if not line: break
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
            work_file.write(json.dumps(new_work))
            work_file.close()