import os
import logging
import subprocess
import traceback

class DaemonUtil(object):
    def __init__(self, key=None):
        self.key = key

    def __GetPidFile(self, key):
        new_key = key
        if self.key:
            new_key = self.key

        if not new_key:
            raise Exception, 'no key specified'

        pid_file = "%s/.pid.%s" % (os.getcwd(), new_key)
        return pid_file

    def IsRunning(self, key=None):
        pid_file = self.__GetPidFile(key)
        logging.info("Daemon: pid_file: %s" % pid_file)

        pid_file_flag = True
        try:
            obj = open(pid_file, "r")
            try:
                content = obj.read()
                file_pid = int(content.strip())
            except Exception, e:
                pid_file_flag = False
                logging.warn("Daemon: Exception: %s, for pid_file: %s" % (str(e), pid_file))
            obj.close()
        except Exception, e:
            pid_file_flag = False
            logging.warn("Daemon: Exception: %s, for pid_file: %s" % (str(e), pid_file))

        if pid_file_flag:
            cmd = "ps --no-heading -p %s " % file_pid
            logging.info("Daemon: cmd: %s" % cmd)
            cnt = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].strip()
            if len(cnt) > 0:
                logging.info("Daemon: program is running")
                return True

        return False


    def WritePidFile(self, key=None):
        pid_file = self.__GetPidFile(key)
        current_pid = os.getpid()
        try:
            obj = open(pid_file, "w")
            try:
                obj.write(str(current_pid))
            except Exception, e:
                logging.warn("Daemon: Exception: %s, traceback: %s" % (str(e), traceback.print_exc()))
                sys.exit()
            obj.close()
        except Exception, e:
            logging.warn("Daemon: Exception: %s, traceback: %s" % (str(e), traceback.print_exc()))
            sys.exit()

        logging.info("Daemon: WritePidFile: new process: %s" % str(current_pid))

    def RemovePidFile(self, key=None):
        pid_file = self.__GetPidFile(key)
        if os.access(pid_file, os.F_OK):
            os.remove(pid_file)


if __name__ == '__main__':
    FILE_PATH   = os.path.dirname(os.path.realpath(__file__))
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        filename="%s/a.log" %
                        (FILE_PATH),
                        filemode='a')

    t = DaemonUtil('ddd')
    t.IsRunning()
    t.WritePidFile()
