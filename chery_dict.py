class RoutineDID:

    routine_did = {
        "0x5781-保养清零": ("5781", "Reset vehicle maintenance"),
        "0x5783-进入域控8155 9008模式": ("5783", "Enter DMC 8155 9008 Mode"),
        "0x5787-AVM EOL 标定": ("5787", "AVM EOL Calibration"),
        "0x5784-以太线缆诊断": ("5784", "Ethernet Cable Diag"),
        "0x5785-设置主从模式": ("5785", "Master/Slave mode"),
        "0x5786-使能以太网测试模式": ("5786", "Ethernet Enable Test Mode"),
        "0x5788-学SK": ("5788", "Learn Secret Key"),
        "0x5789-教SK": ("5789", "Tech Secret Key"),
        "0x5790-重置防盗": ("5790", "Reset to Delivery Condition"),
        "0x5791-ICC 模式（ADB/USB）切换": ("5791", "ICC mode (ADB/USB) switch"),
        "0x5792-恢复出厂设置": ("5792", "factory data reset"),
        "0x5793-触发U盘升级": ("5793", "The upgrade through USB is triggered"),
        "0x5794-以太线缆诊断拓展": ("5794", "Ethernet Cable Diag Extended"),
        "0x5795-保养清零 2": ("5795", "Reset vehicle maintenance 2"),
        "0xDD46-证书灌装": ("DD46", "Filling CSR")
    }


class DTCNumber:
    dtc_number = {
    "980016": ("B180016", "电源电压回路电压过低", "Power Supply Circuit voltage below threshold"),
    "980017": ("B180017", "电源电压回路电压过高", "Power Supply Circuit voltage over threshold"),
    "980C11": ("B180C11", "左前喇叭电路对地短路", "Front Left Speaker Circuit Short To Ground"),
    "980C12": ("B180C12", "左前喇叭电路对电源短路", "Front Left Speaker Circuit Short To Battery"),
    "980C13": ("B180C13", "左前喇叭电路开路", "Front Left Speaker Circuit Open"),
    "980D11": ("B180D11", "右前喇叭电路对地短路", "Front Right Speaker Circuit Short To Ground"),
    "980D12": ("B180D12", "右前喇叭电路对电源短路", "Front Right Speaker Circuit Short To Battery"),
    "980D13": ("B180D13", "右前喇叭电路开路", "Front Right Speaker Circuit Open"),
    "980E11": ("B180E11", "左后喇叭电路对地短路", "Rear Left Speaker Circuit Short To Ground"),
    "980E12": ("B180E12", "左后喇叭电路对电源短路", "Rear Left Speaker Circuit Short To Battery"),
    "980E13": ("B180E13", "左后喇叭电路开路", "Rear Left Speaker Circuit Open"),
    "980F11": ("B180F11", "后右喇叭电路对地短路", "Rear Right Speaker Circuit Short To Ground"),
    "980F12": ("B180F12", "后右喇叭电路对电源短路", "Rear Right Speaker Circuit Short To Battery"),
    "980F13": ("B180F13", "后右喇叭电路开路", "Rear Right Speaker Circuit Open"),
    "981804": ("B181804", "EEPROM读/写故障", "EPROM R/W Failure"),
    "981C04": ("B181C04", "主处理器电源管理芯片控制故障", "Voice Recognition IC R/W Failure"),
    "981E04": ("B181E04", "TBOX连接通断故障", "Disconnect with Tbox"),
    "982019": ("B182019", "USB1接口电路过电流（OTG）", "USB1 current above threshold"),
    "982119": ("B182119", "USB2接口电路过电流（TF卡）", "USB2 current above threshold"),
    "982904": ("B182904", "与人脸识别摄像头连接故障-系统内部故障", "Connection Failure With Face Recognition Camera-System Internal Failure"),
    "982A04": ("B182A04", "麦克风故障-系统内部故障", "Microphone Fault-System Internal Failure"),
    "982B04": ("B182B04", "与乘员监测（OMS）摄像头连接故障-系统内部故障", "Connection Failure With OMS-System Internal Failure"),
    "910111": ("B110111", "仪表燃油系统故障（燃油系统与地短路）", "ICM fuel system fault-Circuit Short To Ground"),
    "910115": ("B110115", "仪表燃油系统故障（燃油系统开路）", "ICM fuel system fault-Circuit Short To Battery or Open"),
    "910C11": ("B110C11", "燃油主泵主采样线路与地短路故障", "ICM Master detect circuit -Circuit Short To Ground"),
    "910C13": ("B110C13", "燃油主泵主采样线路开路故障", "ICM Master detect circuit-Circuit Open"),
    "910D11": ("B110D11", "燃油主泵辅助采样线路与地短路故障", "ICM Assistant detect circuit-Circuit Short To Ground"),
    "910D13": ("B110D13", "燃油主泵辅助采样线路开路故障", "ICM Assistant detect circuit-Circuit Open"),
    "E98000": ("U298000", "以太网初始化Phy失败", "Ethernet PhyInitfail"),
    "E00384": ("U200384", "车控计算中心/左前区域控制器与信息计算中心连接的端口SQI不充足", "Insufficient SQI of the port of VCC/FLZCU to ICC"),
    "E20308": ("U220308", "车控计算中心/左前区域控制器与信息计算中心非预期连接丢失", "Ethernet unexpected Link Loss of VCC/FLZCU&ICC"),
    "D19787": ("U119787", "与智驾计算中心失去通讯", "Lost Communication With ADCC"),
    "C15987": ("U015987", "与泊车雷达辅助失去通讯", "Lost Communication With PDC"),
    "D16187": ("U116187", "与后左角雷达失去通讯", "Lost Communication With RLCR"),
    "D16987": ("U116987", "与后右角雷达失去通讯", "Lost Communication With RRCR"),
    "D20087": ("U120087", "与前左角雷达失去通讯", "Lost Communication With FLCR"),
    "D20187": ("U120187", "与前右角雷达失去通讯", "Lost Communication With FRCR"),
    "C18687": ("U018687", "与外置功放失去通讯", "Lost Communication With EAMP"),
    "C15887": ("U015887", "与抬头显示模块失去通讯", "Lost Communication With HUD"),
    "C15187": ("U015187", "与气囊控制器失去通讯", "Lost Communication With ACU"),
    "D16287": ("U116287", "与前摄像头失去通讯", "Lost Communication With FCM"),
    "C13287": ("U013287", "与自动悬架控制模块失去通讯", "Lost Communication With ASU"),
    "C11187": ("U011187", "与电池管理系统失去通讯", "Lost Communication With BMS"),
    "D21487": ("U121487", "与数字钥匙主控模块失去通讯", "Lost Communication With BNCM"),
    "D16887": ("U116887", "与充电及电压转换单元模块失去通讯", "Lost Communication With CDU"),
    "D19487": ("U119487", "与手机无线充电模块失去通讯", "Lost Communication With CWC"),
    "C10387": ("U010387", "与组合开关总成失去通讯", "Lost Communication With CSA"),
    "C12887": ("U012887", "与右电子驻车控制器总成失去通讯", "Lost Communication With EPB_R"),
    "C13187": ("U013187", "与电动助力转向控制器失去通讯", "Lost Communication With EPS"),
    "D21587": ("U121587", "与PLC通讯转换模块失去通讯", "Lost Communication With EVCC"),
    "C14187": ("U014187", "与左区域控制器失去通讯", "Lost Communication With FLZCU"),
    "D18987": ("U118987", "与多功能方向盘开关失去通讯", "Lost Communication With MFS"),
    "C12987": ("U012987", "与集成制动控制器总成失去通讯", "Lost Communication With ONEBOX"),
    "D21387": ("U121387", "与后低压电池管理系统失去通讯", "Lost Communication With RLBMS"),
    "C11087": ("U011087", "与后驱动电机模块失去通讯", "Lost Communication With RMCU"),
    "C19887": ("U019887", "与无线通讯模块失去通讯", "Lost Communication With TBOX"),
    "C10087": ("U010087", "与发动机管理系统失去通讯", "Lost Communication With EMS"),
    "D16687": ("U116687", "与集成启动发电机失去通讯", "Lost Communication With ISG"),
    "C14287": ("U014287", "与右区域控制器失去通讯", "Lost Communication With FRZCU"),
    "C29287": ("U029287", "与前驱动电机模块失去通讯", "Lost Communication With FMCU"),
    "D21087": ("U121087", "与左前安全带总成失去通讯", "Lost Communication With PPMID"),
    "D20887": ("U120887", "与左交互式信号显示灯失去通讯", "Lost Communication With LISD"),
    "D20987": ("U120987", "与右交互式信号显示灯失去通讯", "Lost Communication With RISD"),
    "C20087": ("U020087", "与左前门控模块失去通讯", "Lost Communication With FLDCM"),
    "C20187": ("U020187", "与右前门控模块失去通讯", "Lost Communication With FRDCM"),
    "C20287": ("U020287", "与左后门控模块失去通讯", "Lost Communication With RLDCM"),
    "C20387": ("U020387", "与右后门控模块失去通讯", "Lost Communication With RRDCM"),
    "C21087": ("U021087", "与二排座椅模块失去通讯", "Lost Communication With SCUM"),
    "C10487": ("U010487", "与动力系统域控制系统失去通讯", "Lost Communication With PDCS"),
    "D02788": ("U102788", "信息计算总线关闭", "Infotainment Computing Control Module Communication Bus Off"),
    "D03288": ("U103288", "信息计算中心私CAN总线关闭", "Infotainment Computing Private CAN Control Module Communication Bus Off"),
    "D30055": ("U130055", "ECU软件配置未配置", "ECU Configuration Is Not Configured"),
    "D30056": ("U130056", "ECU软件配置无效/不兼容", "ECU Configuration Is Invalid / Incompatible Configuration"),
    "D30155": ("U130155", "整车物料号未写入", "Vehicle Material Number Is Not Configured"),
    "600E11": ("C200E11", "前环视摄像头短地故障", "Front Center Around View Camera Circuit short to GND"),
    "600E12": ("C200E12", "前环视摄像头短电源故障", "Front Center Around View Camera Circuit short to BATT"),
    "600E57": ("C200E57", "前环视摄像头标定异常", "Front Center Around View Camera calibration abnormal"),
    "600E97": ("C200E97", "前环视摄像头遮挡", "Front Center Around View Camera blindness"),
    "600F11": ("C200F11", "后环视摄像头短地故障", "Rear Center Around View Camera Circuit short to GND"),
    "600F12": ("C200F12", "后环视摄像头短电源故障", "Rear Center Around View Camera Circuit short to BATT"),
    "600F57": ("C200F57", "后环视摄像头标定异常", "Rear Center Around View Camera calibration abnormal"),
    "600F97": ("C200F97", "后环视摄像头遮挡", "Rear Center Around View Camera blindness"),
    "601011": ("C201011", "左环视摄像头短地故障", "Left Side Around View Camera Circuit short to GND"),
    "601012": ("C201012", "左环视摄像头短电源故障", "Left Side Around View Camera Circuit short to BATT"),
    "601057": ("C201057", "左环视摄像头标定异常", "Left Side Around View Camera  calibration abnormal"),
    "601097": ("C201097", "左环视摄像头遮挡", "Left Side Around View Camera  blindness"),
    "601111": ("C201111", "右环视摄像头短地故障", "Right Side Around View Camera Circuit short to GND"),
    "601112": ("C201112", "右环视摄像头短电源故障", "Right Side Around View Camera Circuit short to BATT"),
    "601157": ("C201157", "右环视摄像头标定异常", "Right Side Around View Camera calibration abnormal"),
    "601197": ("C201197", "右环视摄像头遮挡", "Right Side Around View Camera blindness"),
    "601900": ("C201900", "前环视摄像头电源管理芯片故障", "Front Center Around View Camera PMIC error"),
    "601A00": ("C201A00", "前环视摄像头sensor异常", "Front Center Around View Camera sensor error"),
    "601B00": ("C201B00", "前环视摄像头串行器故障", "Front Center Around View Camera serializer error"),
    "601C00": ("C201C00", "后环视摄像头电源管理芯片故障", "Rear Center Around View Camera PMIC error"),
    "601D00": ("C201D00", "后环视摄像头sensor异常", "Rear Center Around View Camera sensor error"),
    "601E00": ("C201E00", "后环视摄像头串行器故障", "Rear Center Around View Camera serializer error"),
    "601F00": ("C201F00", "左环视摄像头电源管理芯片故障", "Left Side Around View Camera PMIC error"),
    "602000": ("C202000", "左环视摄像头sensor异常", "Left Side Around View Camera sensor error"),
    "602100": ("C202100", "左环视摄像头串行器故障", "Left Side Around View Camera serializer error"),
    "602200": ("C202200", "右环视摄像头电源管理芯片故障", "Right Side Around View Camera PMIC error"),
    "602300": ("C202300", "右环视摄像头sensor异常", "Right Side Around View Camera sensor error"),
    "602400": ("C202400", "右环视摄像头串行器故障", "Right Side Around View Camera serializer error"),
    "603A00": ("C203A00", "左环视摄像头图像不可用故障", "Left Side Around View Camera image unavailable"),
    "603B00": ("C203B00", "右环视摄像头图像不可用故障", "Right Side Around View Camera image unavailable"),
    "603C00": ("C203C00", "前环视摄像头图像不可用故障", "Front Center Around View Camera image unavailable"),
    "603D00": ("C203D00", "后环视摄像头图像不可用故障", "Rear Center Around View Camera image unavailable"),
    "604C16": ("C204C16", "左环视摄像头供电电压过低", "Left Side Around View Camera Circuit Voltage too low"),
    "604C17": ("C204C17", "左环视摄像头供电电压过高", "Left Side Around View Camera Circuit Voltage too high"),
    "604D16": ("C204D16", "右环视摄像头供电电压过低", "Right Side Around View Camera Circuit Voltage too low"),
    "604D17": ("C204D17", "右环视摄像头供电电压过高", "Right Side Around View Camera Circuit Voltage too high"),
    "604E16": ("C204E16", "前环视摄像头供电电压过低", "Front Center Around View Circuit Voltage too low"),
    "604E17": ("C204E17", "前环视摄像头供电电压过高", "Front Center Around View Circuit Voltage too high"),
    "604F16": ("C204F16", "后环视摄像头供电电压过低", "Rear Center Around View Circuit Voltage too low"),
    "604F17": ("C204F17", "后环视摄像头供电电压过高", "Rear Center Around View Circuit Voltage too high"),
    "983000": ("B183000", "VIN码未写入", "VIN is not written"),
    "983100": ("B183100", "PIN码未写入", "Security Code (PIN) is not written"),
    "983200": ("B183200", "SK未学习", "Secret Key(SK) is not learned"),
    "D19587": ("U119587", "与副仪表台控制面板失去通讯", "Lost Communication With CTP"),
    "D23687": ("U123687", "与车载冷暖箱失去通讯", "Lost Communication With CHB"),
    "982C11": ("B182C11", "内置AVM前摄像头电源对地短路", "The built-in AVM front camerapower is short-circuited to ground"),
    "982C12": ("B182C12", "内置AVM前摄像头电源对电源正短路", "The built-in AVM front camera power supply is positively short-circuited to the power supply"),
    "982C13": ("B182C13", "内置AVM前摄像头线束开路", "Built-in AVM front camera harness open circuit"),
    "982C31": ("B182C31", "内置AVM前摄像头视频信号断开", "The video signal of the built-in AVM front camera is disconnected"),
    "982D11": ("B182D11", "内置AVM后摄像头电源对地短路", "The built-in AVM rear camerapower is short-circuited to ground"),
    "982D12": ("B182D12", "内置AVM后摄像头电源对电源正短路", "The built-in AVM rear camera power supply is positively short-circuited to the power supply"),
    "982D13": ("B182D13", "内置AVM后摄像头线束开路", "Built-in AVM rear camera harness open circuit"),
    "982D31": ("B182D31", "内置AVM后摄像头视频信号断开", "The video signal of the built-in AVM rear camera is disconnected"),
    "982E11": ("B182E11", "内置AVM左摄像头电源对地短路", "The built-in AVM left camerapower is short-circuited to ground"),
    "982E12": ("B182E12", "内置AVM左摄像头电源对电源正短路", "The built-in AVM left camera power supply is positively short-circuited to the power supply"),
    "982E13": ("B182E13", "内置AVM左摄像头线束开路", "Built-in AVM left camera harness open circuit"),
    "982E31": ("B182E31", "内置AVM左摄像头视频信号断开", "The video signal of the built-in AVM left camera is disconnected"),
    "982F11": ("B182F11", "内置AVM右摄像头电源对地短路", "The built-in AVM right camerapower is short-circuited to ground"),
    "982F12": ("B182F12", "内置AVM右摄像头电源对电源正短路", "The built-in AVM right camera power supply is positively short-circuited to the power supply"),
    "982F13": ("B182F13", "内置AVM右摄像头线束开路", "Built-in AVM right camera harness open circuit"),
    "982F31": ("B182F31", "内置AVM右摄像头视频信号断开", "The video signal of the built-in AVM right camera is disconnected"),
    "983011": ("B183011", "内置DVR摄像头电源对地短路", "The built-in DVR camera power is short-circuited to ground"),
    "983012": ("B183012", "内置DVR摄像头电源对电源正短路", "The built-in DVR camera power supply is positively short-circuited to the power supply"),
    "983013": ("B183013", "内置DVR摄像头线束开路", "Built-in DVR camera harness open circuit"),
    "983031": ("B183031", "内置DVR摄像头视频信号断开", "The video signal of the built-in DVR camera is disconnected"),
    "983154": ("B183154", "内置AVM未标定", "AVM no calibration"),
    "E00A84": ("U200A84", "智驾计算中心与信息计算中心连接的端口SQI不充足", "Insufficient SQI of the port of ADCC to ICC"),
    "E20A08": ("U220A08", "智驾计算中心与信息计算中心非预期连接丢失", "Ethernet unexpected Link Loss of ADCC&ICC"),
    "983213": ("B183213", "备用电池未连接", "Backup battery not connected"),
    "983313": ("B183313", "GPS模块故障：天线回路开路", "GPS module fault: Ant circuit open"),
    "983311": ("B183311", "GPS模块故障：天线回路对地短路", "GPS module fault:Ant circuit short to ground"),
    "983312": ("B183312", "GPS模块故障：天线回路对12V短路", "GPS module fault:Ant circuit short to 12V"),
    "983331": ("B183331", "GPS模块故障：GPS 模块异常", "GPS module fault: GPS module is abnormal"),
    "983413": ("B183413", "WAN 模块故障：天线回路开路", "Wan module fault: Ant circuit open"),
    "983411": ("B183411", "WAN 模块故障：天线回路对地短路", "Wan module fault: Ant circuit short to ground"),
    "983412": ("B183412", "WAN模块故障：天线回路对12V短路", "Wan module fault:Ant circuit short to 12V"),
    "983431": ("B183431", "WAN模块故障：WAN 模块异常", "Wan module failure: Wan module is abnormal"),
    "983513": ("B183513", "MIC 故障：MIC输入回路开路", "Mic fault: MIC input circuit is open"),
    "983511": ("B183511", "MIC故障：MIC输入回路对地短路", "Mic fault: MIC input circuit is short circuited to ground"),
    "983512": ("B183512", "MIC 故障：MIC输入与12V短路", "MIC input circuit short to 12V"),
    "983600": ("B183600", "SIM卡故障：内置SIM卡未连接", "SIM card failure: the built-in SIM card is not connected"),
    "983700": ("B183700", "SIM卡故障：内置SIM卡异常", "SIM card failure: the built-in SIM card is abnormal"),
    "983800": ("B183800", "TBOX处于工厂模式", "Tbox is in factory mode"),
    "98394B": ("B18394B", "TBOX温度过高", "TBOX_TEMP_HIGH"),
    "983A96": ("B183A96", "RTC芯片异常", "TBOX_RTC_ERROR"),
    "983B4B": ("B183B4B", "内部电池温度过高", "RTM_BATTERY_TEMPERATURE_ERROR"),
    "983C49": ("B183C49", "内部电池寿命结束", "Internal battery failure or end of life"),
    "D02588": ("U102588", "数字钥匙总线关闭", "Digital Key Control Module Communication Bus Off"),
    "983D00": ("B183D00", "以太网2 初始化Phy失败", "Ethernet2 PhyInitfail"),
    "983E96": ("B183E96", "ICC_RTC芯片异常", "ICC_RTC_ERROR"),
    "C51087": ("U051087", "与二排空调控制面板失去通讯", "Lost Communication With RCCP"),
    "D24787": ("U124787", "与后轮转向失去通讯", "Lost Communication With RWS"),
    "983F09": ("B183F09", "SecOC组件运行错误", "SecOC Component runtime error"),
    "984044": ("B184044", "发生了同步计数器数据NVM访问失败的情况", "erase trip counter data in NVM failed")
}


class CodingDID:
    coding_did = {
        (1, 7): ["RLBMS", ["0b:No present", "1b:present"]],
        (2, 4): ["左后角雷达", ["0b:No present", "1b:present"]],
        (2, 5): ["右后角雷达", ["0b:No present", "1b:present"]],
        (3, 6): ["EMS", ["0b:No present", "1b:present"]],
        (3, 7): ["BNCM", ["0b:No present", "1b:present"]],
        (4, 1): ["EAMP/EPA", ["0b:No present", "1b:present"]],
        (4, 2): ["CWC", ["0b:No present", "1b:present"]],
        (4, 3): ["RMCU", ["0b:No present", "1b:present"]],
        (4, 4): ["FMCU", ["0b:No present", "1b:present"]],
        (4, 5): ["CDU", ["0b:No present", "1b:present"]],
        (4, 6): ["BMS", ["0b:No present", "1b:present"]],
        (4, 7): ["EPS", ["0b:No present", "1b:present"]],
        (5, 1): ["ASU/ECAS", ["0b:No present", "1b:present"]],
        (5, 4): ["EPB1", ["0b:No present", "1b:present"]],
        (5, 6): ["PPMID", ["0b:No present", "1b:present"]],
        (5, 7): ["ISG", ["0b:No present", "1b:present"]],
        (7, 4): ["FLDCM", ["0b:No present", "1b:present"]],
        (7, 5): ["FRDCM", ["0b:No present", "1b:present"]],
        (7, 6): ["RLDCM", ["0b:No present", "1b:present"]],
        (7, 7): ["RRDCM", ["0b:No present", "1b:present"]],
        (8, 0): ["FLDRM", ["0b:No present", "1b:present"]],
        (8, 4): ["RCM", ["0b:No present", "1b:present"]],
        (11, 3): ["EVCC", ["0b:No present", "1b:present"]],
        (11, 7): ["CHB", ["0b:No present", "1b:present"]],
        (12, 3): ["车型平台2", ["000b:Reserved", "001b:4.x"]],
        (12, 6): ["RWS", ["0b:No present", "1b:present"]],
        (12, 7): ["SCUM SCUM-E0Y横置增程专用", ["0b:No present", "1b:present"]],
        (13, 0, 7): ["增程/PHEV车型纯电里程", ["00000000b:200km", "00000001b:300km", "00000010b~11111111b:reserved"]],
        (14, 5): ["PDCS", ["0b:No present", "1b:present"]],
        (15, 0, 3): ["车型", ["0000b:SUV", "0001b:Sedan"]],
        (15, 4): ["电动尾翼", ["0b:No present", "1b:present"]],
        (17, 4): ["RCWC", ["0b:No present", "1b:present"]],
        (18, 2): ["副仪表板滑动功能", ["0b:No present", "1b:present"]],
        (18, 5): ["感应开启后背门", ["0b:No present", "1b:present"]],
        (18, 6, 7): ["电动调节方向盘", ["00b:Two directions", "01b:Four directions", "10b:No present"]],
        (19, 0): ["电动调节方向盘记忆", ["0b:No present", "1b:present"]],
        (19, 1, 2): ["TBOX类型", ["00b:netless", "01b: 4G", "10b:5G", "11b: 5G+V2X"]],
        (19, 3, 4): ["零重力座椅位置", ["00b:No present", "01b:Front row", "10b:Second row"]],
        (19, 5, 7): ["主驾座椅电动调节", [
            "000b:Six directions (horizontal, backrest, height)",
            "001b:Eight directions (horizontal, backrest, height, cushion)",
            "010b:Ten directions (horizontal, backrest, height, cushion, leg drag)",
            "011b:reserved",
            "100b:No present",
            "101b:Eight directions (horizontal, backrest, height, leg drag)"
        ]],
        (20, 0, 2): ["副驾座椅电动调节", [
            "000b:Four directions (horizontal, backrest)",
            "001b:Six directions (horizontal, backrest, height)",
            "010b:Eight directions (horizontal, backrest, height, cushion)",
            "011b:Ten directions (horizontal, backrest, cushion, leg drag, height)",
            "100b:reserved",
            "101b:Eight directions (horizontal, backrest, height, leg drag)",
            "110b: No present"
        ]],
        (20, 3, 4): ["二排座椅电动调节", [
            "00b:Two directions",
            "01b:Four directions",
            "10b:Six directions",
            "11b:No present"
        ]],
        (20, 6): ["主驾座椅记忆", ["0b:No present", "1b:present"]],
        (20, 7): ["副驾座椅记忆", ["0b:No present", "1b:present"]],
        (21, 0): ["二排座椅记忆", ["0b:No present", "1b:present"]],
        (21, 1, 2): ["主驾座椅加热", [
            "00b:Backrest only",
            "01b:Cushion only",
            "10b:Backrest and cushion",
            "11b:No present"
        ]],
        (21, 3, 4): ["副驾座椅加热", [
            "00b:Backrest only",
            "01b:Cushion only",
            "10b:Backrest and cushion",
            "11b:No present"
        ]],
        (21, 5, 6): ["二排座椅加热", [
            "00b:Backrest only",
            "01b:Cushion only",
            "10b:Backrest and cushion",
            "11b:No present"
        ]],
        (22, 0, 1): ["主驾座椅通风", [
            "00b:Backrest only",
            "01b:Cushion only",
            "10b:Backrest and cushion",
            "11b:No present"
        ]],
        (22, 2, 3): ["副驾座椅通风", [
            "00b:Backrest only",
            "01b:Cushion only",
            "10b:Backrest and cushion",
            "11b:No present"
        ]],
        (22, 4, 5): ["二排座椅通风", [
            "00b:Backrest only",
            "01b:Cushion only",
            "10b:Backrest and cushion",
            "11b:No present"
        ]],
        (22, 7): ["后视镜倒车下翻", ["0b:No present", "1b:present"]],
        (23, 0): ["后视镜自动折叠", ["0b:No present", "1b:present"]],
        (23, 1): ["电动手套箱解锁", ["0b:No present", "1b:present"]],
        (23, 2): ["车速自动上锁", ["0b:No present", "1b:present"]],
        (23, 5): ["自动亮灯", ["0b:No present", "1b:present"]],
        (23, 6): ["自动除雾", ["0b:No present", "1b:present"]],  # 注：原表为 "Y"，视为 bit6
        (24, 2): ["前雾灯", ["0b:No present", "1b:present"]],
        (24, 7): ["电子儿童锁", ["0b:No present", "1b:present"]],
        (25, 2): ["前风挡加热", ["0b:No present", "1b:present"]],
        (25, 3): ["方向盘加热", ["0b:No present", "1b:present"]],
        (25, 4): ["雨刮喷嘴加热", ["0b:No present", "1b:present"]],
        (26, 4, 6): ["纯电里程", [
            "000b:500km",
            "001b:600km",
            "010b:700km",
            "011b:550km",
            "100b:660km",
            "101b:905km",
            "110b:640km",
            "111b:reserved"
        ]],
        (27, 0): ["香氛功能", ["0b:No present", "1b:present"]],
        (27, 2, 3): ["空气质量净化系统", [
            "00b:With air quality sensor without negative ions",
            "01b:Without air quality sensor without negative ions",
            "10b:With air quality sensor with negative ions",
            "11b:Without air quality sensor with negative ions"
        ]],
        (27, 6): ["二排独立空调控制", ["0b:No present", "1b:present"]],
        (27, 7): ["三排独立空调", ["0b:No present", "1b:present"]],
        (28, 0): ["左右舵", ["0b:Left Rudder", "1b:Right Rudder"]],
        (28, 2): ["驾驶员优先模式", ["0b:Without DFM", "1b:With DFM"]],
        (31, 7): ["CTP", ["0b:No present", "1b:present"]],
        (33, 0, 1): ["智能格栅", [
            "00b:外置式带智能格栅",
            "01b:内置式智能格栅",
            "10b:不带智能格栅"
        ]],
        (34, 0, 1): ["压缩比", [
            "00b:High compression ratio",
            "01b:Low compression ratio",
            "10b~11b:reserved"
        ]],
        (34, 2, 4): ["驱动形式", [
            "000b:front-drive",
            "001b:front-rear-drive",
            "010b:Full-time all-wheel-drive",
            "011b:Timely four-wheel drive",
            "100b:Time-sharing four-wheel drive",
            "101b:Rear-rear-drive",
            "110b:Electric four-wheel drive",
            "111b:reserved"
        ]],
        (35, 1, 2): ["车道保持系统", [
            "00b:With lane keeping system, without emergency lane keeping",
            "01b:Without lane keeping system, without emergency lane keeping",
            "10b:With emergency lane keeping, without lane keeping system",
            "11b:With lane keeping system, with emergency lane keeping"
        ]],
        (37, 3, 6): ["自动紧急制动", [
            "0000b:AEB NO present",
            "0100b：AEB(Single Camera) present"
        ]],
        (38, 6, 7): ["无钥匙进入和启动功能", [
            "00b:No present PEPS",
            "01b:present PEPS"
        ]],
        (43, 3): ["二排安全带锁扣开关+乘员探测", ["0b:No present", "1b:present"]],
        (45, 5): ["副驾驶员双限力式安全带", ["0b:No present", "1b:present"]],
        (46, 0, 7): ["车型代码", [
            "00000000b:E03",
            "00000001b:E0Y",
            "00000010b:EH3",
            "00000011b:EHY",
            "00000100b:E01",
            "00000101b:E02",
            "00000110b:D01",
            "00000111b:D01P",
            "00001000b:M32T",
            "00001001b:T29",
            "00001010b:E08",
            "00001011b:T16A",
            "00001100b:T1J",
            "00001101b:T22",
            "00001110b:T26",
            "00001111b~11111111b:Reserved"
        ]],
        (52, 5): ["SCUM", ["0b:No present", "1b:present"]],
        (53, 0, 3): ["音响仪表域控制器", [
            "0000b:8155 Audio instrument domain controller",
            "0001b:8295 Audio instrument domain controller",
            "0010b:8255 Audio instrument domain controller",
            "0011b:8295 Audio instrument domain controller A",
            "0100b:8295 Audio instrument domain controller B",
            "0101b:8678 Audio instrument domain controller"
        ]],
        (56, 5, 7): ["NFC卡片钥匙数量", [
            "000b:0",
            "001b:1",
            "010b:2"
        ]],
        (57, 5, 7): ["音区", [
            "000b:Four-tone Recognition Zone",
            "001b:Two-tone Recognition Zone",
            "010b:Six-tone Recognition Zone"
        ]],
        (61, 1): ["吸顶屏", ["0b:No present", "1b:present"]],
        (62, 0): ["E0X平台", ["0b:No", "1b:Yes"]],
        (62, 6, 7): ["驱动动力形式", [
            "00b:EV",
            "01b:REEV",
            "10b:PHEV",
            "11b:Reserved"
        ]],
        (63, 2, 3): ["后悬架弹簧形式", [
            "00b:Rear helical spring",
            "01b:Rear air spring",
            "10b:Reserved",
            "11b:Reserved"
        ]],
        (63, 4): ["底盘冗余", ["0b:No present", "1b:present"]],
        (63, 5): ["长距激光雷达", ["0b:No present", "1b:present"]],
        (63, 6): ["补盲激光雷达", ["0b:No present", "1b:present"]],
        (63, 7): ["前毫米波雷达", ["0b:No present", "1b:present"]],
        (64, 0, 7): ["轮胎规格", [
            "00000000b:255/55 R19",
            "00000001b:255/50 R20",
            "00000010b:265/45 R21",
            "00000011b:245/55 R18",
            "00000100b:245/55 R19",
            "00000101b:245/45 R20",
            "00000110b:255/40 R21",
            "00000111b:255/45 R21",
            "00001000b:265/70 R18",
            "00001001b:275/60 R20",
            "00001010b:235/50 R19",
            "00001011b:235/55 R19",
            "00001100b:245/50 R20",
            "00001101b:215/55 R17",
            "00001110b:235/45 R18",
            "00001111b:235/40 R19",
            "00010000b:225/60 R18",
            "00010011b:235/60 R18",
            "00010001b~11111111b:预留"
        ]],
        (65, 0, 1): ["角毫米波雷达", [
            "00b:Without angle millimeter wave radar",
            "01b:Two Angle millimeter wave radar",
            "10b:Four Angle millimeter wave radar",
            "11b:Reserved"
        ]],
        (65, 4, 6): ["全景影像", [
            "000b:No 360 panoramic audio",
            "001b:540 panoramic images (3 million pixels)",
            "010b:Reserved"
        ]],
        (65, 7): ["周视摄像头", ["0b:No present", "1b:present"]],
        (66, 0): ["后视摄像头", ["0b:No present", "1b:present"]],
        (66, 1): ["前视广摄像头", ["0b:No present", "1b:present"]],
        (66, 2): ["前视长焦摄像头", ["0b:No present", "1b:present"]],
        (66, 3): ["前视智能摄像头", ["0b:No present", "1b:present"]],
        (66, 4, 5): ["自动驾驶控制中心", [
            "00b:Without Automatic driving control center",
            "01b:Automatic driving control center A",
            "10b:Automatic driving control center B",
            "11b: This configuration is not used"
        ]],
        (66, 6): ["高精定位模块", ["0b:No present", "1b:present"]],
        (67, 5, 7): ["遮阳帘操纵方式", [
            "000b:Without sunshade",
            "001b:Manual control of sunshade",
            "010b:Front electrically controlled sunshade, rear manually controlled sunshade",
            "011b:Electric control sunshade"
        ]],
        (71, 0, 7): ["外饰风格(PDC)", [
            "00000000b:Exterior style 1",
            "00000001b:Exterior style 2",
            "00000010b:Exterior style 3"
        ]],
        (72, 0, 2): ["主动降噪", [
            "000b:No active noise cancellation",
            "001b:Active noise reduction for road noise",
            "010b:Active noise reduction of the engine",
            "011b:The drive motor actively reduces noise",
            "100b~111b:reserved"
        ]],
        (73, 0, 3): ["功放音效", [
            "0000b:No sound effect",
            "0001b:With Arkamys advanced sound",
            "0010b:With Sony Sound",
            "0011b:With iFlytek sound",
            "0100b:With sound",
            "0101b~1111b:reserved"
        ]],
        (73, 5, 7): ["后排氛围灯", [
            "000b:With Back Row Atmosphere Light",
            "001b:Without Back Row Atmosphere Light",
            "010b~111b:reserved"
        ]],
        (74, 0, 2): ["天窗氛围灯", [
            "000b:Without Sunroof Atmosphere Lamp",
            "001b:With Sunroof Atmosphere Lamp",
            "010b~111b:reserved"
        ]],
        (74, 3, 5): ["车内氛围灯颜色", [
            "000b:Multiple colors Interior Atmosphere Light",
            "001b:A color Interior Atmosphere Light",
            "010b:Dual color Interior Atmosphere Light",
            "011b:Without Interior Atmosphere Light",
            "100b~111b:reserved"
        ]],
        (75, 3): ["RCCP", ["0b:No present", "1b:present"]],
        (75, 4, 7): ["首次保养里程", [
            "0000b:5000km",
            "0001b:10000km",
            "0010b:15000km",
            "0011b~1111b:reserved"
        ]],
        (76, 0, 3): ["保养间隔里程", [
            "0000b:10000km",
            "0001b:5000km",
            "0010b:15000km",
            "0011b:7500km",
            "0100b~1111b:reserved"
        ]],
        (77, 0, 4): ["油箱容积", [
            "00000b:67L",
            "00001b:51L",
            "00010b:45L",
            "00011b:57L",
            "00100b:65L",
            "00101b:60L",
            "00110b:55L",
            "00111b:48L",
            "01000b:70L",
            "01001b~11111b:reserved"
        ]],
        (77, 5, 7): ["车辆控制屏", [
            "000b:No vehicle control screen",
            "001b:Segment code vehicle control screen",
            "010b:Color vehicle control screen",
            "011b~111b:reserved"
        ]],
        (78, 1, 3): ["电压平台", [
            "000b:400V voltage platform",
            "001b:750V voltage platform",
            "010b~111b:reserved"
        ]],
        (78, 6, 7): ["装饰灯", [
            "00b:No decorative lights",
            "01b:With decorative lights",
            "10b~11b:reserved"
        ]],
        (79, 0, 7): ["自动驾驶控制中心2", [
            "00000000b:This configuration is not used",
            "00000001b:Automatic driving control center C",
            "00000010b::Automatic driving control center D",
            "00000011b:Automatic driving control center F",
            "00000100b:Automatic driving control center G",
            "00000101b~11111111b::reserved"
        ]],
        (85, 0, 3): ["整车造型", [
            "0000b:Common",
            "0001b:Facelift",
            "0010b~1111b:reserved"
        ]],
        (86, 7): ["线控机械制动控制器", ["0b:No present", "1b:present"]],
        (88, 1): ["驾驶员座椅按摩功能", ["0b:No present", "1b:present"]],
        (88, 2): ["副驾驶员座椅按摩功能", ["0b:No present", "1b:present"]],
        (88, 3, 6): ["车内氛围灯", [
            "0000b:No present",
            "0001b:With in-car static line light atmosphere light",
            "0010b:With in-car (static line light source + static light panel) atmosphere light",
            "0011b:With in-car (static line light source + flow light panel) atmosphere light",
            "0100b:With in-car static luminescent panel atmosphere light",
            "0101b:Interior flow light panel atmosphere light",
            "0110b:With in-car static double line light source atmosphere light",
            "0111b~1111b:reserved"
        ]],
        (88, 7): ["大灯高度调节", ["0b:Manual", "1b:Auto"]],
        (89, 1, 3): ["头枕扬声器", [
            "000b:No present",
            "001b:2",
            "010b:4",
            "011b:6",
            "100b:8",
            "101b~111b:reserved"
        ]],
        (94, 3): ["智能主动限速", ["0b:No present", "1b:present"]],
        (96, 5, 7): ["高性能功率放大器", [
            "000b:No present",
            "001b:With high performance power amplifier",
            "010b~111b:reserved"
        ]],
        (99, 4, 7): ["泊车雷达辅助系统2", [
            "0000b:This configuration is not used",
            "0001b:Front 2 rear 4 reverse radar",
            "0010b~1111b:reserved"
        ]],
        (105, 0, 3): ["整车造型（ICC）", [
            "0000b:Common",
            "0001b:FL1",
            "0010b:FL2",
            "0011b:FL3",
            "1000b~1111b:reserved"
        ]],
        (107, 5, 7): ["三排座椅电加热功能", [
            "000b:Only seat cushion",
            "001b:Only backrest",
            "010b:Backrest and cushion",
            "011b:Not present"
        ]],
        (108, 0, 2): ["胎压监测系统", [
            "000b:TPMS NO Present",
            "001b: Indirect TPMS Present"
        ]],
        (109, 5): ["DGC", ["0b:No present", "1b:present"]],
        (111, 0, 2): ["座椅数量", [
            "000b:4 seats（2+2）",
            "001b:5 seats（2+3）",
            "010b:6 seats（2+2+2）",
            "011b:7 seats（2+2+3）",
            "100b:7 seats（2+3+2）",
            "101b~111b:reserved"
        ]],
        (111, 3, 5): ["空调系统调节方式", [
            "000b:Dual zone automatic air conditioning",
            "001b:Three zone automatic air conditioning",
            "010b:Three zone automatic air conditioning without afterblow",
            "011b~111b:reserved"
        ]],
        (111, 6, 7): ["无线充电板类型", [
            "00b:No wireless charging pad",
            "01b:With wireless charging pad",
            "10b:Dual charge wireless charging pad",
            "11b:reserved"
        ]],
        (112, 0, 2): ["转向管柱调节", [
            "000b:Manual four direction adjustment",
            "001b:Electric four direction adjustment",
            "010b~111b:reserved"
        ]],
        (112, 3): ["疲劳监测功能", ["0b:No present", "1b:present"]],
        (112, 4): ["照地灯", ["0b:No present", "1b:present"]],
        (112, 5): ["APM", ["0b:No present", "1b:present"]],
        (112, 6): ["后风挡玻璃加热功能", ["0b:No present", "1b:present"]],
        (112, 7): ["TPMS功能", ["0b:No present", "1b:present"]],
        (113, 0): ["EPB功能", ["0b:No present", "1b:present"]],
        (113, 1): ["PLG功能", ["0b:No present", "1b:present"]],
        (113, 2, 5): ["低音扬声器数量", [
            "0000b:No present",
            "0001b:1",
            "0010b:2",
            "0011b:4",
            "0100b:5",
            "0101b:6",
            "0110b~1111b:reserved"
        ]],
        (113, 6, 7): ["重低音扬声器数量", [
            "00b:No present",
            "01b:1",
            "10b:reserved",
            "11b:reserved"
        ]],
        (114, 0, 3): ["高音扬声器数量", [
            "0000b:No present",
            "0001b:2",
            "0010b:4",
            "0011b:5",
            "0100b:6",
            "0101b:9",
            "0110b~1111b:reserved"
        ]],
        (114, 4, 7): ["中音扬声器数量", [
            "0000b:No present",
            "0001b:1",
            "0010b:2",
            "0011b:3",
            "0100b:4",
            "0101b:5",
            "0110b~1111b:reserved"
        ]],
        (115, 0, 2): ["环绕扬声器数量", [
            "000b:No present",
            "001b:2",
            "010b:4",
            "011b:6",
            "100b~111b:reserved"
        ]],
        (115, 3, 5): ["灯光音乐律动", [
            "000b:No present",
            "001b:Present",
            "010b~111b:reserved"
        ]],
        (115, 6): ["保养公里(首保)", ["0b:Domestic/International (5000km)", "1b:International (10000km)"]],
        (115, 7): ["保养公里(保养间隔)", ["0b:Domestic/International (5000km)", "1b:International (10000km)"]],
        (117, 0, 1): ["HUD类型", [
            "00b:No head-up display",
            "01b:Windshield head-up display",
            "10b:Augmented reality head-up realist",
            "11b:reserved"
        ]],
        (117, 2): ["220V电压输出", ["0b:No present", "1b:present"]],
        (117, 3): ["乘员监测", ["0b:No present", "1b:present"]],
        (117, 4, 5): ["超速报警", [
            "00b:No present",
            "01b:30-130km/h",
            "10b:120km/h（GSO）",
            "11b:120km/h（Domestic, three alarm calls）"
        ]],
        (117, 6): ["组合仪表带限速设置", ["0b:No present", "1b:present"]],
        (117, 7): ["车身防盗报警", ["0b:No present", "1b:present"]],
        (118, 0, 1): ["收音区域", [
            "00b:Asia",
            "01b:European Union",
            "10b:America",
            "11b:Latin America"
        ]],
        (118, 2): ["倒车影像", ["0b:No present", "1b:present"]],
        (118, 3): ["自适应前照灯系统（AFS）", ["0b:No present", "1b:present"]],
        (118, 4): ["日间行车灯", ["0b:No present", "1b:present"]],
        (118, 5): ["模拟声浪", ["0b:No present", "1b:present"]],
        (118, 6): ["外后视镜镜片调节方式", ["0b:No present", "1b:present"]],
        (118, 7): ["车载电子收费单元", ["0b:No present", "1b:present"]],
        (119, 0): ["外后视镜电加热功能", ["0b:No present", "1b:present"]],
        (119, 1): ["电动防眩目内后视镜", ["0b:No present", "1b:present"]],
        (119, 2): ["外后视镜记忆功能", ["0b:No present", "1b:present"]],
        (119, 3): ["洗涤液位传感器", ["0b:No present", "1b:present"]],
        (119, 4): ["转向模式选择", ["0b:No present", "1b:present"]],
        (119, 5): ["导航信息", ["0b:No present", "1b:present"]],
        (119, 6): ["收音天线参数", ["0b:extraposition", "1b:built-in"]],
        (119, 7): ["UWB实体钥匙", ["0b:No present", "1b:present"]],
        (120, 0): ["人脸识别", ["0b:No present", "1b:present"]],
        (120, 1, 2): ["USB接口数量", [
            "00b:No USB interface",
            "01b:1 USB port",
            "10b:2 USB port",
            "11b:reserved"
        ]],
        (120, 3): ["语音识别", ["0b:No present", "1b:present"]],
        (120, 4, 6): ["驾驶员座椅腰部调节", [
            "000b:No present",
            "001b:Manual 2 directions",
            "010b:Electric 2 directions",
            "011b:Manual 4 directions",
            "100b:Electric 4 directions",
            "101b~111b:reserved"
        ]],
        (120, 7): ["副驾座椅调节老板键", ["0b:No present", "1b:present"]],
        (121, 0, 2): ["副驾座椅腰部调节", [
            "000b:Manual 4 directions",
            "001b:Manual 6 directions",
            "010b:Manual 8 directions",
            "011b:Electric 4 directions",
            "100b:Electric 6 directions",
            "101b:Electric 8 directions",
            "110b~111b:reserved"
        ]],
        (121, 3, 5): ["二排座椅靠背调节", [
            "000b:Backrest fixed",
            "001b:Manual Angle adjustment",
            "010b:The backrest can be folded",
            "011b:The backrest folds",
            "100b:Manual adjustment + backrest folding",
            "101b:Electric Angle control",
            "110b:Electric Angle adjustment + backrest folding",
            "111b:reserved"
        ]],
        (121, 6, 7): ["二排坐垫调节", [
            "00b:stationary",
            "01b:foldable",
            "10b:reserved",
            "11b:reserved"
        ]],
        (122, 0, 2): ["二排左座椅腰部调节", [
            "000b:No present",
            "001b:Manual 2 directions",
            "010b:Electric 2 directions",
            "011b:Manual 4 directions",
            "100b:Electric 4 directions",
            "101b~111b:reserved"
        ]],
        (122, 3, 5): ["二排右座椅腰部调节", [
            "000b:No present",
            "001b:Manual 2 directions",
            "010b:Electric 2 directions",
            "011b:Manual 4 directions",
            "100b:Electric 4 directions",
            "101b~111b:reserved"
        ]],
        (122, 6): ["二排座椅按摩功能", ["0b:No present", "1b:present"]],
        (122, 7): ["ECALL功能", ["0b:No present", "1b:present"]],
        (123, 0, 3): ["品牌", [
            "0000b:Chery",
            "0001b:EXCEED",
            "0010b:EXLANTIX",
            "0011b:ESTEO",
            "0100b:CHIREY",
            "0101b~1111b:reserved"
        ]],
        (123, 4, 7): ["智能手机钥匙", [
            "0000b:No smartphone keys",
            "0001b:TBOX integrates single Bluetooth phone key without NFC key",
            "0010b:TBOX integrated multi-Bluetooth phone key, no NFC key",
            "0011b:TBOX integrated multi-Bluetooth phone key with NFC key",
            "0100b:No TBOX integrated multi-Bluetooth phone key, with NFC key",
            "0101b:Data key Master module (BLE+UWB) without NFC key",
            "0110b:Data key main module (BLE+UWB) with NFC key",
            "0111b:Data key Master module BLE without NFC key",
            "1000b:Date key Master module BLE with NFC key",
            "1001b~1111b:reserved"
        ]],
        (124, 0, 4): ["驾驶模式", [
            "00000b:No driving mode",
            "00001b:ECO mode only",
            "00010b:SPORT mode only",
            "00011b:With ECO,SPORT mode switch",
            "00100b:With ECO, SPORT and NORMAL mode switch,without memory",
            "00101b:With ECO,SPORT and NORMAL mode switch",
            "00110b:With ECO,SPORT and NORMAL mode switch,with memory",
            "00111b:With SPORT and NORMAL mode switch,without memory",
            "01000b:With NORMAL,SPORT,SNOW,MUD,OFFROAD mode switch,without memory",
            "01001b:With ECO,NORMAL,SPORT,SNOW,MUD,OFFROAD mode switch,without memory",
            "01010b:With ECO,NORMAL,SPORT,SNOW,MUD,SAND,OFFROAD mode switch,without memory",
            "01011b:SPORT,ECO,COMFORT with memory, OFFROAD,INDIVIDUAL without memory",
            "01100b:SPORT,ECO,COMFORT with memory，RAIN AND SNOW ,INDIVIDUAL without memory",
            "01101b:ECO,SPORT,NORMAL,SNOW,MUD,SAND,OFFROAD mode switch,with memory",
            "01110b:ECO,SPORT,NORMAL,SNOW mode switch,with memory",
            "01111b:SPORT,ECO,COMFORT,INDIVIDUAL without memory",
            "10000b:SPORT,ECO,COMFORT,INDIVIDUAL with memory",
            "10001b:SPORT,ECO,COMFORT,INDIVIDUAL with memory，OFFROAD without memory",
            "10010b:SPORT,ECO,COMFORT,INDIVIDUAL with memory，RAIN AND SNOW without memory",
            "10011b:reserved",
            "10100b:eserved",
            "10101b:SPORT,ECO,COMFORT,INDIVIDUAL,OFFROAD without memory",
            "10110b:SPORT,ECO,COMFORT,INDIVIDUAL，RAIN AND SNOW without memory",
            "10111b:ECO、SPORT、COMFORT、INDIVIDUAL with memory、RAIN AND SNOW、SAND、OFFROAD without memory",
            "11000b:ECO EV, ECO HEV, COMFORT HEV, INDIVIDUAL HEV with memory, SPORT HEV without memory",
            "11001b:ECO EV, ECO HEV, COMFORT HEV, INDIVIDUAL HEV with memory, RAIN AND SNOW, SPORT HEV without memory",
            "11010b:ECO、NORMAL、SPORT、SNOW、SAND、OFFROAD mode switch,without memory",
            "11011b:ECO、SPORT、COMFORT、INDIVIDUAL with memory,RAIN AND SNOW、OFFROAD without memory"
        ]],
        (124, 5): ["雨量传感器灵敏度软开关", ["0b:No present", "1b:present"]],
        (124, 6): ["DAB", ["0b:No present", "1b:present"]],
        (124, 7): ["多色车内氛围灯", ["0b:No present", "1b:present"]],
        (125, 0): ["大灯延时关闭", ["0b:No present", "1b:present"]],
        (125, 1): ["电动后扰流板", ["0b:No present", "1b:present"]],
        (125, 2, 3): ["交互式信号显示灯", [
            "00b:No present",
            "01b:Only the front has an interactive signal display light",
            "10b:reserved",
            "11b:reserved"
        ]],
        (125, 5): ["迎宾仪式点亮功能", ["0b:No present", "1b:present"]],
        (125, 6): ["四音区", ["0b:2 microphones", "1b:4 microphones"]],
        (125, 7): ["Hicar", ["0b:No present", "1b:present"]],
        (126, 0, 1): ["行车电脑", [
            "00b:No driving computer",
            "01b:Driving computer",
            "10b:Air cooled driving computer",
            "11b:Water cooled driving computer"
        ]],
        (126, 2, 5): ["音响及娱乐显示屏尺寸", [
            "0000b:15.6-inch display",
            "0001b:12.36-inch display",
            "0010b:30-inch display",
            "0011b~1111b:reserved"
        ]],
        (126, 6): ["WIFI", ["0b:No present", "1b:present"]],
        (126, 7): ["蓝牙功能", ["0b:No present", "1b:present"]],
        (127, 0, 3): ["Telematics天线", [
            "0000b:No present",
            "0001b:2 channels GNSS+4 channels 5G+2 channels V2X",
            "0010b:2 channels GNSS+4 channels 5G",
            "0011b:GNSS+2 channel 4G (built-in) with Beidou",
            "0100b:GNSS Splitter (built-in)",
            "0101b~1111b:reserved"
        ]],
        (127, 4): ["组合仪表亮度自动调节", ["0b:No present", "1b:present"]],
        (127, 5): ["手机APP远程控制", ["0b:No present", "1b:present"]],
        (127, 6): ["Lion人工智能系统", ["0b:No present", "1b:present"]],
        (127, 7): ["方向盘离手监测", ["0b:No present", "1b:present"]],
        (128, 0): ["方向盘带仪表翻页", ["0b:No present", "1b:present"]],
        (128, 1): ["多功能方向盘按键", ["0b:No present", "1b:present"]],
        (128, 2, 5): ["组合仪表尺寸", [
            "0000b:10.25-inch display",
            "0001b:9.2-inch display",
            "0010b:8.88-inch display",
            "0011b~1111b:reserved"
        ]],
        (128, 6, 7): ["泊车雷达辅助系统", [
            "00b:Front no rear 4 reverse radar",
            "01b:Front 4 rear 4 reverse radar",
            "10b:Front 6 rear 6 reverse radar",
            "11b:This configuration is not used"
        ]],
        (129, 0, 4): ["语言", [
            "00000b:Chinese",
            "00001b:English",
            "00010b:Russian",
            "00011b:Arabic",
            "00100b:Portuguese",
            "00101b:Farsi",
            "00110b:Spanish",
            "00111b:Italian",
            "01000b:Turkish",
            "01001b:Ukrainian",
            "01010b:Thai",
            "01011b:Indonesian",
            "11100b~11111b:reserved"
        ]],
        (129, 5): ["朝拜指南针", ["0b:No present", "1b:present"]],
        (129, 6, 7): ["智能大灯控制", [
            "00b:No present",
            "01b:With adaptive high beam",
            "10b:With automatic near and far light switching",
            "11b:reserved"
        ]],
        (130, 0, 1): ["车内儿童检测", [
            "00b:No present",
            "01b:Child detection in car",
            "10b:Passive in-car child detection",
            "11b:reserved"
        ]],
        (130, 2, 3): ["语言识别方式", [
            "00b:No speech recognition",
            "01b:Local speech recognition",
            "10b:Local + cloud identification",
            "11b:reserved"
        ]],
        (130, 4, 5): ["PAB屏蔽", [
            "00b:No front PAB mechanical shield",
            "01b:Aith front PAB Mechanical shield",
            "10b:With front PAB touch shield",
            "11b:reserved"
        ]],
        (130, 6, 7): ["行车记录仪", [
            "00b:No present",
            "01b:With separate Traffic recorder",
            "10b:With integrated Traffic recorder",
            "11b:reserved"
        ]],
        (131, 0, 7): ["销售区域（ICC）", [
            "00000000b:China",
            "00000001b:Chile",
            "00000010b:Indonesia",
            "00000011b:Malaysia",
            "00000100b:Brazil",
            "00000101b:Central Asia",
            "00000110b:bay",
            "00000111b:Russia",
            "00001000b:Egypt",
            "00001001b:Italy",
            "00001010b:Ukraine",
            "00001011b:Ecuador",
            "00001100b:Mexico",
            "00001101b:Philippines",
            "00001110b:Saudi Arabia",
            "00001111b:Thailand",
            "00010000b:Kazakhstan",
            "00010001b:Australia",
            "00010010b:Turkey",
            "00010011b:Israel",
            "00010100b:Serbia",
            "00010101b:United Arab Emirates",
            "00010110b:Britain",
            "00010111b:Colombia",
            "00011000b:Peru",
            "00011001b:Uzbekistan",
            "00011010b:Norway",
            "00011011b:Belarus",
            "00011100b:South Africa",
            "00011101b:Korea",
            "00011110b~11111111b:reserved"
        ]],
        (132, 0, 4): ["多功能方向盘按键2", [
            "00000b:Multi-function steering wheel keys with rollers only",
            "00001b:Multi-function steering wheel buttons with buttons and rollers",
            "00010b:No multi-function steering wheel buttons",
            "00011b:With multi-function steering wheel buttons",
            "00100b~11111b:reserved"
        ]],
        (132, 6): ["三排座椅加热", ["0b:not present", "1b:present"]],
        (136, 0, 4): ["麦克风数量", [
            "00000b:2",
            "00001b:4",
            "00010b:5",
            "00011b:6",
            "00100b~11111b:reserved"
        ]],
        (136, 7): ["自动泊车模块", ["0b:not present", "1b:present"]],
        (143, 4, 7): ["AVM集成方式", [
            "0000b:APA integrated AVM",
            "0001b:ICC integrated AVM",
            "0010b:non-existent"
        ]],
        (144, 4, 5): ["倒车侧向紧急制动系统", [
            "00b:No present",
            "01b:present"
        ]],
        (146, 0, 2): ["怠速启停系统", [
            "000b:Idle Stop-Start System nopresent",
            "001b:12V Idle Stop-Start System"
        ]],
        (146, 3, 5): ["前后方交通穿行提示", [
            "000b:No present",
            "001b:Front Cross-Traffic Alert no present, Rear Cross-Traffic Alert present"
        ]],
        (154, 6, 7): ["智驾域控与座舱域控连接方式", [
            "00b:Ethernet Direct connection",
            "01b:Ethernet Non Direct connection",
            "10b~11b:reseerved"
        ]],
        (158, 1, 3): ["行人提醒装置", [
            "000b:AVAS Not present",
            "001b:One AVAS  present"
        ]],
        (164, 0, 5): ["侧门开启方式", [
            "000000b:Manual side door",
            "000001b:Power side door",
            "000010b:Left front door power with ultrasonic detection radar",
            "000011b:Right front door power with ultrasonic detection radar",
            "000100b:Front door electric with ultrasonic detection radar",
            "000101b:Four-door electric radar with ultrasonic detection",
            "000110b:Left front door power with millimeter wave detection radar",
            "000111b:Right front door power with millimeter wave detection radar",
            "001000b:Front door electric with millimeter wave detection radar",
            "001001b:Four-door electric radar with millimeter wave detection",
            "001010b~111111b:reserved"
        ]],
        (165, 0, 2): ["侧门锁释放方式", [
            "000b:Electrically release front door lock, electrically release rear door lock",
            "001b:Release the front door lock electrically and the rear door lock manually",
            "010b:Manually release the front door lock and electrically release the rear door lock",
            "011b:Manually release the front door lock and manually release the rear door lock",
            "100b~111b::reserved"
        ]]
    }
if __name__ == '__main__':
    a = [key for key in RoutineDID().routine_did.keys()]
    print(a)
    print(len(a))

    code = "C15187"
    if code in DTCNumber().dtc_number:
        dtc, chinese, english = DTCNumber().dtc_number[code]
        print(f"DTC: {dtc}")
        print(f"中文: {chinese}")
        print(f"English: {english}")