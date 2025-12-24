import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QComboBox
from PySide6.QtCore import QObject, Signal, Slot, QEventLoop, QTimer
# 导入你由 .ui 文件生成的 UI 类
# from ui_DoIP import Ui_Dialog  # 假设你的 UI 类叫 Ui_MainWindow
import ui_DoIP
# from Lib.Log import Log
from function import DoIPMessage, DataHandle
# from loguru import logger
from Lib.Log import Log
from Lib.ConfigCache import TomlConfig
from history_input import HistoryManager
import re
from dtc import DTCParser
from chery_dict import RoutineDID, DTCNumber, CodingDID

debug_mode = TomlConfig('config.toml').get('current.debug_mode')
logger = Log(debug_mode).create_log_sample()

def ansi_to_html(text):
    """
    将 ANSI 转义序列转换为简单 HTML（支持 loguru 常用颜色）
    """
    # 先处理重置
    text = re.sub(r'\x1b\[0m', '</span>', text)

    # 前景色（30-37, 90-97）
    color_map = {
        '31': 'red',
        '32': 'green',
        '33': 'orange',
        '34': 'blue',
        '35': 'magenta',
        '36': 'cyan',
        '37': 'lightgray',
        '90': 'darkgray',
        '91': 'lightred',
        '92': 'lightgreen',
        '93': 'yellow',
        '94': 'lightblue',
        '95': 'pink',
        '96': 'lightcyan',
    }

    for code, color in color_map.items():
        text = re.sub(rf'\x1b\[{code}m', f'<span style="color:{color};">', text)

    # 可选：处理加粗（1m）—— loguru 有时会用 \x1b[1;32m 这种组合
    # 简单起见，我们忽略加粗，或统一用 font-weight
    text = re.sub(r'\x1b\[1m', '<b>', text)
    text = re.sub(r'\x1b\[22m', '</b>', text)  # 关闭加粗（非标准，可选）

    return text


class LogHandler(QObject):
    log_signal = Signal(str)  # 定义一个信号，传递字符串

    def __init__(self):
        super().__init__()

    def write(self, message):
        # message 是 loguru 传入的日志记录（带格式）
        # 去掉末尾换行（可选）
        log_msg = message.strip()
        self.log_signal.emit(log_msg)

    def flush(self):
        pass  # 必须实现，但通常为空


class MainWindow(QMainWindow, ui_DoIP.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.frame = DoIPMessage()
        self.data = DataHandle()
        self.conf = TomlConfig('config.toml' )
        self.log_level = self.conf.get("current.log_level")
        self.activate_type = 0x00

        self.f011 = "62 F0 11 00 80 00 40 FE 40 00 00 00 00 00 08 40 00 00 00 00 00 60 21 C2 54 AA 67 80 08 00 C9 00 00 00 00 00 00 18 06 00 00 00 00 00 00 00 08 00 20 0F 00 00 00 00 00 00 00 00 00 20 40 00 00 00 00 40 F4 00 91 1F 60 00 00 00 00 02 04 08 08 00 05 00 00 00 00 00 00 00 00 00 00 0E 02 00 00 00 00 08 00 20 00 00 00 00 00 00 00 00 00 00 40 00 00 00 8A F9 4F 53 01 00 D4 50 6D C9 2D E4 00 A0 A1 03 E0 81 80 A9 00 41 00 00 00 00 00 00 00 00 00 00 00 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 95"
        self.res_f011 = self.f011.replace(" ", "").lower()
        self.log_handler = LogHandler()
        self.log_handler.log_signal.connect(self.append_log)

        self.dtc = DTCParser

        # 移除默认的 stderr 输出（可选）
        # logger.remove()
        # 添加自定义 sink, log level在此处修改
        logger.add(self.log_handler.write, level=self.log_level, enqueue=True, colorize=True)

        # all button init
        self.application_service_init()
        self.system_did_init()
        self.eol_init()
        self.dtc_init()
        self.ecu_did_init()
        self.coding_did_init()
        self.io_control_did_init()
        self.undefined_button_init()

        self.pushButton_send.clicked.connect(self.send_free_input)
        self.pushButton_send.clicked.connect(self.save_current_input)
        self.pushButton_clear_log.clicked.connect(self.clear_log)
        self.pushButton_save_log.clicked.connect(self.save_log)

        self.history_manager = HistoryManager(
            combo=self.comboBox,
            history_key="signal_history",
            max_history=20
        )
        self.comboBox.currentTextChanged.connect(self.on_history_selected)

        self.timer_3e = QTimer()
        self.timer_3e.timeout.connect(self.send_3e_once)
        self.is_sending_3e = False

        self.timer_3e_eol = QTimer()
        self.timer_3e_eol.timeout.connect(self.send_3e_eol_once)
        self.is_sending_3e_eol = False

        self.history_key = "signal_history"
        self.max_history = 20
        self.comboBox.setEditable(False)
        self.comboBox.currentTextChanged.connect(self.on_history_selected)

        self.address = self.conf.get("current.ecu_logical_address")
        self.radioButton_physical.setChecked(True)
        self.radioButton_functional.toggled.connect(self.on_mode_changed)

        self.radioButton_physical.toggled.connect(self.on_mode_changed)
        # self.load_history()

    def application_service_init(self):
        # 10 服务
        self.pushButton_defaultSession.clicked.connect(lambda: self.frame.positive_response('1001'))
        self.pushButton_extendedDiagnosticSession.clicked.connect(lambda: self.frame.positive_response('1003'))

        # 27 服务
        self.pushButton_SecurityAccess.clicked.connect(self.frame.send_security_access_2701)
        self.pushButton_SecurityAccess_0506.clicked.connect(self.frame.send_security_access_2705)

        # 11 服务，被ECU拒绝
        self.pushButton_hardReset.clicked.connect(lambda: self.frame.positive_response('1101'))
        self.pushButton_softReset.clicked.connect(lambda: self.frame.positive_response('1103'))

        # 28 服务，被ECU拒绝
        # self.pushButton_enableRxAndTx.clicked.connect(lambda: self.frame.positive_response('2800'))
        # self.pushButton_disableRxAndTx.clicked.connect(lambda: self.frame.positive_response('2803'))
        self.comboBox_CommunicationControl = self.findChild(QComboBox, "comboBox_CommunicationControl")
        self.comboBox_CommunicationControl.clear()  # 清除 Designer 中可能预设的内容（可选）
        self.comboBox_CommunicationControl.addItems([
            "select a message", "28 00 01", "28 00 02", "28 00 03", "28 03 01", "28 03 02", "28 03 03"
        ])
        self.comboBox_CommunicationControl.currentTextChanged.connect(self.send_28_combobox)

        # self.comboBox_routine_activate_type = self.findChild(QComboBox, "comboBox_routine_activate_type")
        self.comboBox_routine_did.clear()  # 清除 Designer 中可能预设的内容（可选）
        self.comboBox_routine_did.addItems(
            [key for key in RoutineDID().routine_did.keys()])

        self.pushButton_StartRoutine.clicked.connect(lambda: self.frame.positive_response(
            '3101' + self.comboBox_routine_did.currentText()[2:6]))
        self.pushButton_stopRoutine.clicked.connect(lambda: self.frame.positive_response(
            '3102' + self.comboBox_routine_did.currentText()[2:6]))
        self.pushButton_RequestRoutineResults.clicked.connect(lambda: self.frame.positive_response(
            '3103' + self.comboBox_routine_did.currentText()[2:6]))

        # 85 服务
        self.pushButton_ControlDTCSetting_On.clicked.connect(lambda: self.frame.positive_response('8501'))
        self.pushButton_ControlDTCSetting_Off.clicked.connect(lambda: self.frame.positive_response('8502'))

        # 3E 服务
        self.pushButton_TesterPresent.clicked.connect(self.toggle_send_3e)

        # 19 服务
        self.pushButton_ReadDTCInformation.clicked.connect(lambda: self.frame.positive_response('1902ff'))

    def system_did_init(self):
        self.pushButton_f180.clicked.connect(lambda: self.frame.positive_response('22f180'))
        self.pushButton_f187.clicked.connect(lambda: self.frame.positive_response('22f187'))
        self.pushButton_f189.clicked.connect(lambda: self.frame.positive_response('22f189'))
        self.pushButton_f089.clicked.connect(lambda: self.frame.positive_response('22f089'))
        self.pushButton_f013.clicked.connect(lambda: self.frame.positive_response('22f013'))
        self.pushButton_f18a.clicked.connect(lambda: self.frame.positive_response('22f18a'))
        self.pushButton_f18b.clicked.connect(lambda: self.frame.positive_response('22f18b'))
        self.pushButton_f18c.clicked.connect(lambda: self.frame.positive_response('22f18c'))
        self.pushButton_f186.clicked.connect(lambda: self.frame.positive_response('22f186'))
        self.pushButton_f160.clicked.connect(lambda: self.frame.positive_response('22f160'))
        self.pushButton_f190_read.clicked.connect(lambda: self.frame.positive_response('22f190'))
        # self.pushButton_f190_write.clicked.connect(lambda: send_all_in_one('2ef190', 3, 1, self.lineEdit_f190))
        # f190 写入
        self.pushButton_f190_write.clicked.connect(lambda: self.frame.positive_response('1003'))
        self.pushButton_f190_write.clicked.connect(self.frame.send_security_access_2701)
        self.pushButton_f190_write.clicked.connect(
            lambda: self.frame.positive_response('2ef190' + self.data.wash_input(self.lineEdit_f190.text())))

        self.pushButton_f0fe_read.clicked.connect(lambda: self.frame.positive_response('22f0fe'))
        # f0fe 写入
        self.pushButton_f0fe_write.clicked.connect(lambda: self.frame.positive_response('1003'))
        self.pushButton_f0fe_write.clicked.connect(self.frame.send_security_access_2701)
        self.pushButton_f0fe_write.clicked.connect(
            lambda: self.frame.positive_response('2ef0fe' + self.data.wash_input(self.lineEdit_f0fe.text())))

        self.pushButton_f161.clicked.connect(lambda: self.frame.positive_response('22f161'))
        self.pushButton_f091.clicked.connect(lambda: self.frame.positive_response('22f091'))
        self.pushButton_f083.clicked.connect(lambda: self.frame.positive_response('22f083'))
        self.pushButton_f084.clicked.connect(lambda: self.frame.positive_response('22f084'))
        self.pushButton_f086.clicked.connect(lambda: self.frame.positive_response('22f086'))
        self.pushButton_f087.clicked.connect(lambda: self.frame.positive_response('22f087'))
        self.pushButton_f08b.clicked.connect(lambda: self.frame.positive_response('22f08b'))



    def eol_init(self):
        self.pushButton_1060.clicked.connect(lambda: self.frame.positive_response('1060'))
        # 1060无法3e维持，不过当前状态下不需要维持也可以发送eol did
        self.pushButton_1060.clicked.connect(self.toggle_send_3e_eol)

        self.pushButton_eol_f187.clicked.connect(lambda: self.frame.positive_response('22f187'))
        self.pushButton_eol_f189.clicked.connect(lambda: self.frame.positive_response('22f189'))
        self.pushButton_eol_f089.clicked.connect(lambda: self.frame.positive_response('22f089'))
        self.pushButton_eol_f013.clicked.connect(lambda: self.frame.positive_response('22f013'))
        self.pushButton_eol_f18a.clicked.connect(lambda: self.frame.positive_response('22F18A'))
        self.pushButton_eol_f18b.clicked.connect(lambda: self.frame.positive_response('22f18b'))
        self.pushButton_eol_f18c.clicked.connect(lambda: self.frame.positive_response('22f18c'))

        self.pushButton_eol_f1ae.clicked.connect(lambda: self.frame.positive_response('22f1ae'))
        self.pushButton_eol_da10.clicked.connect(lambda: self.frame.positive_response('22da10'))
        self.pushButton_eol_f195.clicked.connect(lambda: self.frame.positive_response('22f195'))

        self.pushButton_eol_fd98.clicked.connect(lambda: self.frame.positive_response('22fd98'))
        self.pushButton_eol_fd00.clicked.connect(lambda: self.frame.positive_response('22fd00'))
        self.pushButton_eol_f193.clicked.connect(lambda: self.frame.positive_response('22f193'))
        self.pushButton_eol_fdf6.clicked.connect(lambda: self.frame.positive_response('22fdf6'))
        self.pushButton_eol_fdf7.clicked.connect(lambda: self.frame.positive_response('22fdf7'))

        self.pushButton_eol_da21.clicked.connect(lambda: self.frame.positive_response('22da21'))
        self.pushButton_eol_fd89.clicked.connect(lambda: self.frame.positive_response('22fd89'))
        self.pushButton_eol_fd15.clicked.connect(lambda: self.frame.positive_response('22fd15'))
        self.pushButton_eol_f116.clicked.connect(lambda: self.frame.positive_response('22f116'))
        self.pushButton_eol_fd0c.clicked.connect(lambda: self.frame.positive_response('22fd0c'))

        self.pushButton_eol_fd1c.clicked.connect(lambda: self.frame.positive_response('22fd1c'))
        self.pushButton_eol_fd0b.clicked.connect(lambda: self.frame.positive_response('22fd0b'))
        self.pushButton_eol_fd51.clicked.connect(lambda: self.frame.positive_response('22fd51'))
        self.pushButton_eol_fd53.clicked.connect(lambda: self.frame.positive_response('22fd53'))
        self.pushButton_eol_fd61.clicked.connect(lambda: self.frame.positive_response('22fd61'))

        self.pushButton_eol_fd65.clicked.connect(lambda: self.frame.positive_response('22fd65'))
        self.pushButton_eol_fd40.clicked.connect(lambda: self.frame.positive_response('22fd40'))
        self.pushButton_eol_fd30.clicked.connect(lambda: self.frame.positive_response('22fd30'))
        self.pushButton_eol_fd13.clicked.connect(lambda: self.frame.positive_response('22fd13'))
        self.pushButton_eol_fda4.clicked.connect(lambda: self.frame.positive_response('22fda4'))

        self.pushButton_eol_fda2.clicked.connect(lambda: self.frame.positive_response('22fda2'))
        self.pushButton_eol_fda1.clicked.connect(lambda: self.frame.positive_response('22fda1'))
        self.pushButton_eol_fda0.clicked.connect(lambda: self.frame.positive_response('22fda0'))
        self.pushButton_eol_fd14.clicked.connect(lambda: self.frame.positive_response('22fd14'))
        self.pushButton_eol_fd70.clicked.connect(lambda: self.frame.positive_response('22fd70'))
        self.pushButton_eol_fdb5.clicked.connect(lambda: self.frame.positive_response('22fdb5'))
        self.pushButton_eol_f08b.clicked.connect(lambda: self.frame.positive_response('22f08b'))
        self.pushButton_eol_f083.clicked.connect(lambda: self.frame.positive_response('22f083'))

    def dtc_init(self):
        # self.pushButton_U118987.clicked.connect(lambda: self.check_has_dtc("D18987"))
        # self.pushButton_U012987.clicked.connect(lambda: self.check_has_dtc("C12987"))
        # self.pushButton_U014187.clicked.connect(lambda: self.check_has_dtc("C14187"))
        # self.pushButton_U013187.clicked.connect(lambda: self.check_has_dtc("C13187"))
        # self.pushButton_U010387.clicked.connect(lambda: self.check_has_dtc("C10387"))
        # self.pushButton_U015187.clicked.connect(lambda: self.check_has_dtc("C15187"))

        self.pushButton_check_all_dtc.clicked.connect(self.check_all_dtc)
        self.pushButton_send_14.clicked.connect(lambda: self.frame.positive_response('14ffffff'))
        self.comboBox_single_dtc.clear()
        self.comboBox_single_dtc.addItems([f"{key}-{DTCNumber().dtc_number[key][0]}-{DTCNumber().dtc_number[key][1]}"
                                           for key in DTCNumber().dtc_number.keys()])
        self.comboBox_single_dtc.currentTextChanged.connect(lambda: self.check_has_dtc(
            self.comboBox_single_dtc.currentText()[:6]))

        self.pushButton_check_single_dtc.clicked.connect(self.check_has_dtc_by_dtc_num)

    def ecu_did_init(self):
        self.pushButton_5703.clicked.connect(lambda: self.frame.positive_response("225703"))
        self.pushButton_5708.clicked.connect(lambda: self.frame.positive_response("225708"))
        self.pushButton_570e.clicked.connect(lambda: self.frame.positive_response("22570E"))
        self.pushButton_5717.clicked.connect(lambda: self.frame.positive_response("225717"))
        self.pushButton_5721.clicked.connect(lambda: self.frame.positive_response("225721"))
        self.pushButton_5722.clicked.connect(lambda: self.frame.positive_response("225722"))
        self.pushButton_5723.clicked.connect(lambda: self.frame.positive_response("225723"))
        self.pushButton_5724.clicked.connect(lambda: self.frame.positive_response("225724"))
        self.pushButton_5727.clicked.connect(lambda: self.frame.positive_response("225727"))
        self.pushButton_5728.clicked.connect(lambda: self.frame.positive_response("225728"))
        self.pushButton_5729.clicked.connect(lambda: self.frame.positive_response("225729"))
        self.pushButton_572a.clicked.connect(lambda: self.frame.positive_response("22572A"))
        self.pushButton_d008.clicked.connect(lambda: self.frame.positive_response("2eD008" + self.lineEdit_d008.text()))  # 2e
        self.pushButton_5739.clicked.connect(lambda: self.frame.positive_response("225739"))
        self.pushButton_572b.clicked.connect(lambda: self.frame.positive_response("22572B"))
        self.pushButton_572c.clicked.connect(lambda: self.frame.positive_response("22572C"))
        self.pushButton_572d.clicked.connect(lambda: self.frame.positive_response("22572D"))
        self.pushButton_572e.clicked.connect(lambda: self.frame.positive_response("22572E"))
        self.pushButton_572f.clicked.connect(lambda: self.frame.positive_response("22572F"))
        self.pushButton_5730.clicked.connect(lambda: self.frame.positive_response("225730"))
        self.pushButton_5731.clicked.connect(lambda: self.frame.positive_response("225731"))
        self.pushButton_573a.clicked.connect(lambda: self.frame.positive_response("22573A"))
        self.pushButton_573b.clicked.connect(lambda: self.frame.positive_response("22573B"))
        self.pushButton_573c.clicked.connect(lambda: self.frame.positive_response("22573C"))
        self.pushButton_573d.clicked.connect(lambda: self.frame.positive_response("22573D"))
        self.pushButton_573f.clicked.connect(lambda: self.frame.positive_response("22573F"))
        self.pushButton_5740.clicked.connect(lambda: self.frame.positive_response("225740"))
        self.pushButton_5741.clicked.connect(lambda: self.frame.positive_response("225741"))
        self.pushButton_5742.clicked.connect(lambda: self.frame.positive_response("225742"))
        self.pushButton_5743.clicked.connect(lambda: self.frame.positive_response("225743"))
        self.pushButton_5744.clicked.connect(lambda: self.frame.positive_response("225744"))
        self.pushButton_5745.clicked.connect(lambda: self.frame.positive_response("225745"))
        self.pushButton_574d.clicked.connect(lambda: self.frame.positive_response("22574D"))
        self.pushButton_574e.clicked.connect(lambda: self.frame.positive_response("22574E"))
        self.pushButton_574f.clicked.connect(lambda: self.frame.positive_response("22574F"))
        self.pushButton_5750.clicked.connect(lambda: self.frame.positive_response("225750"))
        self.pushButton_5751.clicked.connect(lambda: self.frame.positive_response("225751"))
        self.pushButton_5752.clicked.connect(lambda: self.frame.positive_response("225752"))
        self.pushButton_5753.clicked.connect(lambda: self.frame.positive_response("225753"))
        self.pushButton_5784.clicked.connect(lambda: self.frame.positive_response("225784"))

    def io_control_did_init(self):
        self.pushButton_571d_01.clicked.connect(lambda: self.frame.positive_response("2f571d01"))
        self.pushButton_571d_02.clicked.connect(lambda: self.frame.positive_response("2f571d02"))
        self.pushButton_571e_00.clicked.connect(lambda: self.frame.positive_response("2f571e00"))
        self.pushButton_571e_01.clicked.connect(lambda: self.frame.positive_response("2f571e01"))
        self.pushButton_571e_02.clicked.connect(lambda: self.frame.positive_response("2f571e02"))
        self.pushButton_571e_03.clicked.connect(lambda: self.frame.positive_response("2f571e03"))
        self.pushButton_571f_01.clicked.connect(lambda: self.frame.positive_response("2f571f01"))
        self.pushButton_571f_02.clicked.connect(lambda: self.frame.positive_response("2f571f02"))

    def coding_did_init(self):
        self.pushButton_read_f011.clicked.connect(self.refresh_f011_value)
        self.pushButton_f011_analyze.clicked.connect(lambda: DataHandle().analyze_byte_in_response(
            self.res_f011, int(self.lineEdit_byte.text()), CodingDID().coding_did
        ))

    def undefined_button_init(self):
        self.pushButton_undefined_1.setText(self.conf.get("undefined.button_name_1"))
        self.pushButton_undefined_1.clicked.connect(
            lambda: self.frame.positive_response(self.conf.get("undefined.msg_1")))
        self.pushButton_undefined_2.setText(self.conf.get("undefined.button_name_2"))
        self.pushButton_undefined_2.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_2")))
        self.pushButton_undefined_3.setText(self.conf.get("undefined.button_name_3"))
        self.pushButton_undefined_3.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_3")))
        self.pushButton_undefined_4.setText(self.conf.get("undefined.button_name_4"))
        self.pushButton_undefined_4.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_4")))
        self.pushButton_undefined_5.setText(self.conf.get("undefined.button_name_5"))
        self.pushButton_undefined_5.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_5")))
        self.pushButton_undefined_6.setText(self.conf.get("undefined.button_name_6"))
        self.pushButton_undefined_6.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_6")))
        self.pushButton_undefined_7.setText(self.conf.get("undefined.button_name_7"))
        self.pushButton_undefined_7.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_7")))
        self.pushButton_undefined_8.setText(self.conf.get("undefined.button_name_8"))
        self.pushButton_undefined_8.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_8")))
        self.pushButton_undefined_9.setText(self.conf.get("undefined.button_name_9"))
        self.pushButton_undefined_9.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_9")))
        self.pushButton_undefined_10.setText(self.conf.get("undefined.button_name_10"))
        self.pushButton_undefined_10.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_10")))
        self.pushButton_undefined_11.setText(self.conf.get("undefined.button_name_11"))
        self.pushButton_undefined_11.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_11")))
        self.pushButton_undefined_12.setText(self.conf.get("undefined.button_name_12"))
        self.pushButton_undefined_12.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_12")))
        self.pushButton_undefined_13.setText(self.conf.get("undefined.button_name_13"))
        self.pushButton_undefined_13.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_13")))
        self.pushButton_undefined_14.setText(self.conf.get("undefined.button_name_14"))
        self.pushButton_undefined_14.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_14")))
        self.pushButton_undefined_15.setText(self.conf.get("undefined.button_name_15"))
        self.pushButton_undefined_15.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_15")))
        self.pushButton_undefined_16.setText(self.conf.get("undefined.button_name_16"))
        self.pushButton_undefined_16.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_16")))
        self.pushButton_undefined_17.setText(self.conf.get("undefined.button_name_17"))
        self.pushButton_undefined_17.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_17")))
        self.pushButton_undefined_18.setText(self.conf.get("undefined.button_name_18"))
        self.pushButton_undefined_18.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_18")))
        self.pushButton_undefined_19.setText(self.conf.get("undefined.button_name_19"))
        self.pushButton_undefined_19.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_19")))
        self.pushButton_undefined_20.setText(self.conf.get("undefined.button_name_20"))
        self.pushButton_undefined_20.clicked.connect(lambda: self.frame.positive_response(self.conf.get("undefined.msg_20")))

    def refresh_f011_value(self):
        self.res_f011 = self.frame.basic_send_response('22f011')

    def send_28_combobox(self):
        _ = self.comboBox_CommunicationControl.currentText()
        if not _.startswith("select"):
            msg = self.data.wash_input(_)
            logger.info(f"combobox msg = {msg}")

            self.frame.positive_response(msg)

    # def set_routine_activate_type(self):
    #     current_activate_type = self.comboBox_routine_activate_type.currentText()
    #     match current_activate_type:
    #         case '0x00':
    #             self.activate_type = 0x00
    #             logger.info("Set routing activation type: 0x00--Default")
    #         case '0x01':
    #             self.activate_type = 0x01
    #             logger.info("Set routing activation type: 0x01--WWH-OBD")
    #         case 'None':
    #             self.activate_type = None
    #         case '0xE0':
    #             self.activate_type = 0xE0
    #     logger.info("Set routing activation type: 0xE0--Central security")

    def on_mode_changed(self):
        if self.radioButton_physical.isChecked():
            self.address = self.conf.get("current.ecu_logical_address")
        else:
            self.address = self.conf.get("current.ecu_functional_address")
        logger.debug(f"current address is：{self.address}")

    def save_log(self):
        content = self.textBrowser.toPlainText()
        file_path = os.path.join(os.getcwd(), "output.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Log saved: {file_path}")
    def check_all_dtc(self):
        res = self.frame.basic_send_response('190209')
        # res = "59 09 C1 51 87 09 C1 29 87 09 C1 03 87 09 C1 31 87 09 C1 41 87 09 D1 89 87 08"
        # res = basic_send_response('190a')
        # result_list = self.dtc.get_known_dtc_descriptions(res)
        current_dtcs, history_dtcs = self.dtc.get_known_dtc_by_status(res)
        if current_dtcs:
            logger.info("检测到当前故障！")

            for desc in current_dtcs:
                logger.info(f"  - {desc}")
        else:
            logger.info("未发现当前故障！")
        if history_dtcs:
            logger.info("检测到历史故障！")

            for desc in history_dtcs:
                logger.info(f"  - {desc}")
        else:
            logger.info("未发现历史故障！")


    def check_has_dtc(self, dtc_num):
        res = self.frame.basic_send_response('190209')
        # res = basic_send_response('190a')
        # logger.info(f"get dtc res = {res}")
        # logger.info(f"get type of dtc res = {type(res).__name__}")
        res = self.dtc.check_dtc_and_print(res, dtc_num)
        # if res[0]:
        #
        #     logger.info(res[1])
        # else:
        #     logger.error(res[1])
    # def load_history_from_disk(self):
    #     """从 QSettings 加载历史"""
    #     settings = QSettings("VST", "CherryDoIP")
    #     history = settings.value(self.history_key, [])
    #     if isinstance(history, list):
    #         history = [s for s in history if isinstance(s, str)]
    #         self.comboBox.addItems(history)

    def check_has_dtc_by_dtc_num(self):
        try:
            dtc_num = DataHandle().find_dtc_key(self.lineEdit_single_dtc.text().strip().upper(), DTCNumber.dtc_number)
            if dtc_num:
                self.check_has_dtc(dtc_num)
        except Exception as E:
            logger.exception(E)

    def save_current_input(self):
        """委托给 history_manager 处理"""
        text = self.textEdit_free_input.toPlainText().strip()
        self.history_manager.add_to_history(text)

        # 持久化
        # self.save_history_to_disk()

    def on_history_selected(self, text):
        """从历史下拉选择时，填充到 QTextEdit"""
        if text.strip():
            self.textEdit_free_input.setPlainText(text)
    #
    # def save_history_to_disk(self):
    #     """保存历史到 QSettings"""
    #     history = [self.comboBox.itemText(i) for i in range(self.comboBox.count())]
    #     settings = QSettings("YourCompany", "CherryDoIP")
    #     settings.setValue(self.history_key, history)
    #
    # def load_history(self):
    #     self.load_history_from_disk()

    @staticmethod
    def async_sleep(sleep_time):
        loop = QEventLoop()
        QTimer.singleShot(int(sleep_time), loop.quit)
        loop.exec()

    def toggle_send_3e(self):
        """点击按钮调用此方法：启动或停止发送"""
        if self.is_sending_3e:
            self.timer_3e.stop()
            self.is_sending_3e = False
            logger.info("Stopped sending 3E00")
            # 可选：更新按钮文本
            # self.button.setText("Start Sending")
        else:
            self.timer_3e.start(4000)  # 每4000毫秒（4秒）触发一次
            self.is_sending_3e = True
            logger.info("Started sending 3E00")
            # 可选：更新按钮文本
            # self.button.setText("Stop Sending")

    def toggle_send_3e_eol(self):
        """点击按钮调用此方法：启动或停止发送"""
        if self.is_sending_3e_eol:
            self.timer_3e_eol.stop()
            self.is_sending_3e_eol = False
            logger.info("Stopped sending 3E00")
            # 可选：更新按钮文本
            # self.button.setText("Start Sending")
        else:
            self.timer_3e_eol.start(4000)  # 每4000毫秒（4秒）触发一次
            self.is_sending_3e_eol = True
            logger.info("Started sending 3E00")

    def send_3e_once(self):
        """每次只发送一次"""
        self.frame.send_without_response('3e00')

    def send_3e_eol_once(self):
        self.frame.send_without_response('3e00')


    @Slot(str)
    def append_log(self, msg: str):
        html = ansi_to_html(msg)
        self.textBrowser.insertHtml(html + "<br>")  # <br> 换行
        # 自动滚动到底部
        self.textBrowser.verticalScrollBar().setValue(
            self.textBrowser.verticalScrollBar().maximum()
        )

    def clear_log(self):
        self.textBrowser.clear()
        
    def get_free_input(self):
        msg = self.textEdit_free_input.toPlainText()
        # logger.info(f"Send: \t{hex_output(msg)}")
        return msg

    def send_free_input(self):
        msg = self.data.wash_input(self.get_free_input())
        # logger.info(f"Send: \t{hex_output(msg)}")
        target_address = self.address

        activate_type = self.activate_type
        # logger.info(f"activate_type = {activate_type}")
        self.frame.free_send(msg, target_address, activation_type_code=activate_type)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # logger.info("程序启动成功！")
    # logger.warning("这是一个警告")
    # logger.error("出错了！")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()