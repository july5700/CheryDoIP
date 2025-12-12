from loguru import logger
from datetime import datetime
import os
import sys


"""
situation1：不做任何记录，和输出
situation2：只记录到log，不输出到控制台
situation3：只输出到控制台，不记录到log
situation4：既输出到控制台，也记录到log
"""

class OutPutMode(object):
    no_log = 0  # 无输出，静默
    log_open = 1  # 输出到控制台
    log_to_file = 2  # 输出到文件
    log_to_stdout_file = 3  # 输出到控制台+文件

"""
20251227: 1. 增加log level控制参数
"""
class Log(object):
    def __init__(self, debug_mode=7, log_folder='output', log_level='TRACE'):
        self.debug_mode = debug_mode
        # print(f"at init self.debug_Mode is {self.debug_mode}")
        # if self.debug.lower() == 'true' or self.debug.lower() == '1':
        self.log_folder = log_folder  # log文件存储的路径
        self.log_level = log_level
        self.log_path = ''
        # self.log_sample = self.create_log_sample()

    def create_log_folder(self):
        if not os.path.exists(self.log_folder):
            os.mkdir(self.log_folder)
            # print("文件夹: {}已创建".format(self.log_folder))
        day = datetime.now().strftime("%Y%m%d")
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        sub_log_folder = os.path.join(self.log_folder, day)  # 日期子目录
        self.log_path = os.path.join(sub_log_folder, now + "_output.log")
        print("Log Path: ", self.log_path)
        if not os.path.exists(sub_log_folder):
            os.mkdir(sub_log_folder)
            # print("文件夹: {}已创建".format(sub_log_folder))
        else:
            # print("文件夹: {}已存在".format(self.path))
            pass

    def create_log_sample(self):
        """
        根据debug level给出logger实体
        3--输出到文件+控制台输出
        2--输出到文件
        1--控制台输出
        0--无输出
        :return: loguru._logger.Logger
        Notes: stdout will print twice if you add anthor sink
        """
        log = logger
        # log.remove(handler_id=None)
        match self.debug_mode:
            case 3:
                print(f"Debug Mode Level: {self.debug_mode}")
                self.create_log_folder()
                log.remove()
                log.add(self.log_path, format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}: {function}:{line} - "
                                    "{message}", level=self.log_level, backtrace=True, diagnose=True)
                # print(f"logger.level = {logger.level.__name__}")
                log.add(sys.stdout)

                return log
            case 2:
                print(f"Debug Mode Level: {self.debug_mode}")
                self.create_log_folder()
                log.remove()
                log.add(self.log_path, format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}: {function}:{line} - "
                                              "{message}", level=self.log_level, backtrace=True, diagnose=True)
                # log.add(sys.stdout)

                return log
            case 1:
                log.remove()
                # logger.add(sys.stdout, level=self.log_level)
                # log.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <cyan>{name}: {function}:{line}</cyan> - "
                #                            "{message}", level=self.log_level, backtrace=True, diagnose=True)
                log.add(sys.stdout, level=self.log_level)
                # print(type(log))
                # print(f"logger.level = {logger.level.__name__}")
                # print("当前 sink 数量:", len(logger._core.handlers))
                for handler_id, handler in logger._core.handlers.items():
                    print(f"ID: {handler_id}, Sink: {handler._name}")
                return log
            case 0:
                log.remove()
                return log
            case _:
                print(f"Debug Mode Level: {self.debug_mode}")
                print("查看log debug level规则，并选择一个level:")


        # 将自定义处理程序添加到日志器



        #
        # if self.debug_mode == 7:
        #     l.add(self.log_path, format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}: {function}:{line} - "
        #                                 "{message}", level="INFO", backtrace=False, diagnose=False)
        #
        #     # 将自定义处理程序添加到日志器
        #
        #     l.add(sys.stdout)
        # else:
        #     if sys.stdout in l.handlers:
        #         l.remove(sys.stdout)
        return log


if __name__ == "__main__":
    l = Log(1,log_level='CRITICAL')
    # l.debug_mode=3
    b = l.create_log_sample()
    folder = l.log_folder
    log_path = l.log_path
    b.info(f"look at me,once,folder = {folder}")
    b.critical(f"look at me,twice,log_path = {log_path}")

    try:
        # 模拟抛出异常
        raise ValueError("This is a sample exception")
    except ValueError:
        # 记录异常信息
        b.exception("An error occurred")
    b.debug("This is a debug message")
    b.info("This is an info message")
    b.warning("This is a warning message")
    b.error("This is an error message")
    b.critical("This is a critical message")
