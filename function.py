from client import DoIPClient
from binascii import unhexlify
from security_access import (cal_ace_emac, cal_tea_variant, cal_ace_emac_aibox_2701, cal_ace_emac_aibox_2719,
                             cal_tea_variant_aibox, cal_ace_emac_2711)
# from loguru import logger
from Lib.Log import Log
from Lib.ConfigCache import TomlConfig
import re
import random
# from openpyxl import load_workbook

"""
函数      输入类型	    输出类型    	功能
hexlify	    bytes	    bytes	    二进制 → 十六进制（ASCII）
unhexlify	str/bytes 	bytes	十六进制 → 二进制
"""
# print(logger.level)
# logger.level="TRACE"
# print(logger.level)
logger = Log(1, log_level='TRACE').create_log_sample()

conf = TomlConfig("config.toml")
ecu_add = conf.get("current.ecu_logical_address")
tester_add = conf.get("current.tester_logical_address")


#
class DoIPClientForTest(object):
    def __init__(self, client):
        self.client = client

    def basic_send_receive(self, msg):
        br = unhexlify(msg)
        logger.info(f"Send: \t{DataHandle.hex_output(br)}")
        uds_command = bytearray(br)
        self.client.send_diagnostic(uds_command)
        # _ = unhexlify(msg)
        # self.client.send_diagnostic(_)
        # logger.info(f"Send: {DataHandle.hex_output(_)}")
        response = self.client.receive_diagnostic().hex()
        str_res = DataHandle.hex_output(response)
        logger.info(f"Receive: {response}")
        return response

    def security_access_level_1(self):
        _ = unhexlify('2701')
        self.client.send_diagnostic(_)
        seed = self.client.receive_diagnostic().hex()[4:]
        token = cal_ace_emac(seed)
        new_msg = '2702' + token
        _ = self.client.send_diagnostic(unhexlify(new_msg))
        final_response = self.client.receive_diagnostic().hex()
        if final_response == "6702":
            logger.success(f"Security Access 01/02 successful: {final_response}")
        else:
            logger.error(f"Security Access 01/02 denied: {final_response}")
        return final_response

    def security_access_level_2(self):
        _ = unhexlify('2705')
        self.client.send_diagnostic(_)
        seed = self.client.receive_diagnostic().hex()[4:]
        token = cal_tea_variant(seed)
        new_msg = '2706' + token
        _ = self.client.send_diagnostic(unhexlify(new_msg))
        final_response = self.client.receive_diagnostic().hex()
        if final_response == "6706":
            logger.success(f"Security Access 05/06 successful: {final_response}")
        else:
            logger.error(f"Security Access 05/06 denied: {final_response}")
        return final_response


    def session_and_security_level(self,session=1, level=1):
        pass


class DoIPMessage(object):
    def __init__(self):
        self.config = TomlConfig('config.toml')
        self.target_address = self.config.get("current.ecu_logical_address")
        
        self.ecu_ip = self.config.get("current.ecu_ip_address")

        self.physical_address = self.config.get("current.ecu_logical_address")
        self.functional_address = self.config.get("current.ecu_functional_address")
        self.tester_address = self.config.get("current.tester_logical_address")

    def basic_send_response(self, msg):
        logger.trace(f"self.ecu_ip = {self.ecu_ip}")
        logger.trace(f"self.physical_address = {self.physical_address}")
        logger.trace(f"client_logical_address=self.tester_address = {self.tester_address}")
        with DoIPClient(self.ecu_ip, self.physical_address, client_logical_address=self.tester_address) as doip:
            # ✅ 明确使用 bytearray
            # uds_command = bytearray([0x10, 0xC0])  # 进入扩展诊断会话
            # msg = "1003"
            logger.trace(f"doip object: {doip}")
            br = unhexlify(msg)
            logger.info(f"Send: \t{DataHandle.hex_output(br)}")
            uds_command = bytearray(br)
            doip.send_diagnostic(uds_command)

            response = doip.receive_diagnostic()
            re_current = response.hex()
            # a = 123
            # logger.info(f"Response: {hex_output(response)}")
            res_str = DataHandle.hex_output(response.hex())
            logger.info(f"Response: \t{res_str}")
            # logger.info(f"re_current: \t{re_current}")
            # logger.info(f"type of Response: {type(a).__name__}")
            return re_current


    def free_send(self, msg, target_address, activation_type_code):
        with DoIPClient(self.ecu_ip, target_address, client_logical_address=self.tester_address,
                        activation_type=activation_type_code) as doip:
            # ✅ 明确使用 bytearray
            # uds_command = bytearray([0x10, 0xC0])  # 进入扩展诊断会话
            # msg = "1003"
            br = unhexlify(msg)
            logger.trace(f"target_address: {target_address}")
            logger.info(f"Send: \t{DataHandle.hex_output(br)}")
            uds_command = bytearray(br)
            doip.send_diagnostic(uds_command)

            response = doip.receive_diagnostic()
            re_current = response.hex()
            # a = 123
            # logger.info(f"Response: {hex_output(response)}")
            res_str = DataHandle.hex_output(response.hex())
            logger.info(f"Response: \t{res_str}")
            # logger.info(f"type of Response: {type(a).__name__}")
            return re_current

    def udp_send(self, msg, target_address, activation_type_code=None):
        with DoIPClient(self.ecu_ip, target_address, client_logical_address=self.tester_address,
                        activation_type=activation_type_code) as doip:
            br = unhexlify(msg.replace(" ", ""))
            logger.info(f"UDP Send: \t{DataHandle.hex_output(br)}")
            doip._udp_sock.sendto(br, (doip._ecu_ip_address, doip._udp_port))
            try:
                response = doip._udp_sock.recv(4096)
                res_hex = response.hex()
                logger.info(f"UDP Response: \t{DataHandle.hex_output(res_hex)}")
                return res_hex
            except Exception as e:
                logger.warning(f"No response or error: {e}")
                return ""

    def positive_response(self, msg):
        response = self.basic_send_response(msg)
        if response.startswith("7f"):
            logger.error(f"Negative response: {DataHandle.hex_output(response)}")
        else:
            str_msg = DataHandle.wash_input(msg)
            str_res = DataHandle.wash_input(response)
            result = DataHandle.check_positive_response(str_msg, str_res)
            if result:
                logger.success("PASS")
            else:
                logger.error(f"FAIL: response: {DataHandle.hex_output(str_res)}")

    def send_without_response(self, msg):
        with DoIPClient(self.ecu_ip, self.physical_address, client_logical_address=self.tester_address) as doip:
            # ✅ 明确使用 bytearray
            # uds_command = bytearray([0x10, 0xC0])  # 进入扩展诊断会话
            # msg = "1003"
            br = unhexlify(msg)
            logger.trace(f"Send: \t{DataHandle.hex_output(br)}")
            uds_command = bytearray(br)
            doip.send_diagnostic(uds_command)
            response = doip.receive_diagnostic()

            # a = 123
            # logger.info(f"Response: {hex_output(response)}")
            res_str = DataHandle.hex_output(response.hex())
            logger.info(f"Response: \t{res_str}")

    def raw_send(self, hex_data):
        """直接发送原始十六进制数据（不经过DoIP封装），支持构造畸形报文"""
        with DoIPClient(self.ecu_ip, self.physical_address, client_logical_address=self.tester_address) as doip:
            br = unhexlify(hex_data.replace(" ", ""))
            logger.info(f"Raw Send: \t{DataHandle.hex_output(br)}")
            doip._tcp_sock.send(br)
            try:
                response = doip._tcp_sock.recv(4096)
                res_hex = response.hex()
                logger.info(f"Response: \t{DataHandle.hex_output(res_hex)}")
                return res_hex
            except Exception as e:
                logger.warning(f"No response or error: {e}")
                return ""

    def send_security_access_2701(self):
        with DoIPClient(self.ecu_ip, self.physical_address, client_logical_address=self.tester_address) as doip:
            # ✅ 明确使用 bytearray
            # uds_command = bytearray([0x10, 0xC0])  # 进入扩展诊断会话
            # msg = "1003"

            br = unhexlify('2701')
            # uds_command = bytearray(br)
            doip.send_diagnostic(br)

            seed = doip.receive_diagnostic().hex()[4:]
            logger.info(f"seed: {seed}")
            # logger.info(f"type of seed = {type(seed)}")

            token = cal_ace_emac(seed)
            new_request = '2702' + token
            new_br = unhexlify(new_request)
            doip.send_diagnostic(new_br)

            response = doip.receive_diagnostic().hex().upper()
            if response == "6702":
                logger.success(f"pass response = {response}")
                return 1
            else:
                logger.error(f"fail response = {response}")
                return 0

    def send_security_access_2711(self):
        with DoIPClient(self.ecu_ip, self.physical_address, client_logical_address=self.tester_address) as doip:
            # ✅ 明确使用 bytearray
            # uds_command = bytearray([0x10, 0xC0])  # 进入扩展诊断会话
            # msg = "1003"

            br = unhexlify('2711')
            # uds_command = bytearray(br)
            doip.send_diagnostic(br)

            seed = doip.receive_diagnostic().hex()[4:]
            logger.info(f"seed: {seed}")
            # logger.info(f"type of seed = {type(seed)}")

            token = cal_ace_emac_2711(seed)
            new_request = '2712' + token
            new_br = unhexlify(new_request)
            doip.send_diagnostic(new_br)

            response = doip.receive_diagnostic().hex().upper()
            if response == "6712":
                logger.success(f"pass response = {response}")
                return 1
            else:
                logger.error(f"fail response = {response}")
                return 0

    def send_security_access_2701_aibox(self):
        with DoIPClient(self.ecu_ip, self.physical_address, client_logical_address=self.tester_address) as doip:
            # ✅ 明确使用 bytearray
            # uds_command = bytearray([0x10, 0xC0])  # 进入扩展诊断会话
            # msg = "1003"

            br = unhexlify('2701')
            # uds_command = bytearray(br)
            doip.send_diagnostic(br)

            seed = doip.receive_diagnostic().hex()[4:]
            logger.info(f"seed: {seed}")
            # logger.info(f"type of seed = {type(seed)}")

            token = cal_ace_emac_aibox_2701(seed)
            new_request = '2702' + token
            new_br = unhexlify(new_request)
            doip.send_diagnostic(new_br)

            response = doip.receive_diagnostic().hex().upper()
            if response == "6702":
                logger.success(f"pass response = {response}")
                return 1
            else:
                logger.error(f"fail response = {response}")
                return 0

    def send_security_access_2719_aibox(self):
        with DoIPClient(self.ecu_ip, self.physical_address, client_logical_address=self.tester_address) as doip:
            # ✅ 明确使用 bytearray
            # uds_command = bytearray([0x10, 0xC0])  # 进入扩展诊断会话
            # msg = "1003"

            br = unhexlify('2719')
            # uds_command = bytearray(br)
            doip.send_diagnostic(br)

            seed = doip.receive_diagnostic().hex()[4:]
            logger.info(f"seed: {seed}")
            # logger.info(f"type of seed = {type(seed)}")

            token = cal_ace_emac_aibox_2719(seed)
            new_request = '271a' + token
            new_br = unhexlify(new_request)
            doip.send_diagnostic(new_br)

            response = doip.receive_diagnostic().hex().upper()
            if response == "671a":
                logger.success(f"pass response = {response}")
                return 1
            else:
                logger.error(f"fail response = {response}")
                return 0

    def send_security_access_2705_aibox(self):
        with DoIPClient(self.ecu_ip, self.physical_address, client_logical_address=self.tester_address) as doip:
            # ✅ 明确使用 bytearray
            # uds_command = bytearray([0x10, 0xC0])  # 进入扩展诊断会话
            # msg = "1003"

            br = unhexlify('2705')
            # uds_command = bytearray(br)
            doip.send_diagnostic(br)

            seed = doip.receive_diagnostic().hex()[4:]
            logger.info(f"seed: {seed}")
            # logger.info(f"type of seed = {type(seed)}")

            token = cal_tea_variant_aibox(seed)
            new_request = '2706' + token
            new_br = unhexlify(new_request)
            doip.send_diagnostic(new_br)

            response = doip.receive_diagnostic().hex().upper()
            if response == "6706":
                logger.success(f"pass response = {response}")
                return 1
            else:
                logger.error(f"fail response = {response}")
                return 0

    def send_security_access_2761(self):
        with DoIPClient(self.ecu_ip, self.physical_address, client_logical_address=self.tester_address) as doip:
            br = unhexlify('2761')
            # uds_command = bytearray(br)
            doip.send_diagnostic(br)

            seed = doip.receive_diagnostic().hex()[4:]
            logger.info(f"seed: {seed}")
            # logger.info(f"type of seed = {type(seed)}")

            token = cal_ace_emac(seed)
            new_request = '2762' + token
            new_br = unhexlify(new_request)
            doip.send_diagnostic(new_br)

            response = doip.receive_diagnostic().hex().upper()
            if response == "6762":
                logger.success(f"pass response = {response}")
                return 1
            else:
                logger.error(f"fail response = {response}")
                return 0

    def send_security_access_2705(self):
        with DoIPClient(self.ecu_ip, self.physical_address, client_logical_address=self.tester_address) as doip:
            # ✅ 明确使用 bytearray
            # uds_command = bytearray([0x10, 0xC0])  # 进入扩展诊断会话
            # msg = "1003"

            br = unhexlify('2705')
            # uds_command = bytearray(br)
            doip.send_diagnostic(br)

            seed = doip.receive_diagnostic().hex()[4:]
            logger.info(f"seed: {seed}")
            # logger.info(f"type of seed = {type(seed)}")

            token = cal_tea_variant(seed)
            new_request = '2706' + token
            new_br = unhexlify(new_request)
            doip.send_diagnostic(new_br)

            response = doip.receive_diagnostic().hex().upper()
            if response == "6706":
                logger.success(f"pass response = {response}")
                return 1
            else:
                logger.error(f"fail response = {response}")
                return 0

    def send_security_access_2719(self):
        with DoIPClient(self.ecu_ip, self.physical_address, client_logical_address=self.tester_address) as doip:
            # ✅ 明确使用 bytearray
            # uds_command = bytearray([0x10, 0xC0])  # 进入扩展诊断会话
            # msg = "1003"

            br = unhexlify('2719')
            # uds_command = bytearray(br)
            doip.send_diagnostic(br)

            seed = doip.receive_diagnostic().hex()[4:]
            logger.info(f"seed: {seed}")
            # logger.info(f"type of seed = {type(seed)}")

            token = cal_tea_variant(seed)
            new_request = '271a' + token
            new_br = unhexlify(new_request)
            doip.send_diagnostic(new_br)

            response = doip.receive_diagnostic().hex().upper()
            if response == "671a":
                logger.success(f"pass response = {response}")
                return 1
            else:
                logger.error(f"fail response = {response}")
                return 0





class DataHandle:
    def __init__(self):
        pass

    @staticmethod
    def wash_input(user_input: str) -> str:
        if not isinstance(user_input, str):
            raise TypeError("Input must be a string")

        s = user_input.strip()
        if not s:
            raise ValueError("Empty input")

        # 情况一：看起来是“按字节分隔”的格式（包含空格 或 多个 0x）
        if ' ' in s or '\t' in s or '\n' in s or s.count('0x') > 1 or s.count('0X') > 1:
            # 按空白分割
            tokens = re.split(r'\s+', s)
            cleaned = []
            for token in tokens:
                token = token.strip()
                if not token:
                    continue
                # 去掉可能的 0x/0X 前缀
                if token.lower().startswith('0x'):
                    token = token[2:]
                # 每个 token 必须是 1-2 位 hex（一个字节）
                if not re.fullmatch(r'[0-9a-fA-F]{1,2}', token):
                    raise ValueError(f"Invalid hex byte token: '{token}'")
                cleaned.append(token.zfill(2))  # 确保两位，如 'A' → '0A'
            hex_str = ''.join(cleaned)

        else:
            # 情况二：整体 hex 字符串（可能带一个全局 0x）
            if s.lower().startswith('0x'):
                s = s[2:]
            # 检查是否全为 hex 字符
            if not re.fullmatch(r'[0-9a-fA-F]+', s):
                raise ValueError(f"Invalid hex string: '{s}'")
            hex_str = s
        # logger.info(hex_str)
        return hex_str.upper()

    @staticmethod
    def check_positive_response(request_hex: str, response_hex: str) -> bool:
        """
        检查 UDS 响应是否为正响应

        Args:
            request_hex: 请求的十六进制字符串，如 "1003"
            response_hex: 响应的十六进制字符串，如 "5003"

        Returns:
            bool: True 表示正响应，False 表示否定响应或无效

        Example:
            # >>> check_positive_response("1003", "5003")
            # True
            # >>> check_positive_response("22F190", "62F190")
            # True
            # >>> check_positive_response("1003", "7F1022")
            False  # 否定响应
        """
        # 清理输入：去空格、转大写
        req = request_hex.replace(" ", "").upper()
        resp = response_hex.replace(" ", "").upper()

        # 验证是否为合法 hex 且长度 >= 2
        if len(req) < 2 or len(resp) < 2:
            return False
        if not all(c in '0123456789ABCDEF' for c in req + resp):
            return False

        # 提取请求 SID（前两个字符）
        req_sid = int(req[0:2], 16)
        expected_resp_sid = req_sid + 0x40  # 正响应 SID = 请求 SID + 0x40

        # 提取响应 SID（前两个字符）
        try:
            resp_sid = int(resp[0:2], 16)
        except ValueError:
            return False

        # 判断是否为正响应
        if resp_sid == expected_resp_sid:
            # 可选：进一步检查后续字节是否匹配（简单场景可只比对第一个参数）
            # 例如：请求 10 03 → 响应 50 03，第二个字节应相同
            if len(req) >= 4 and len(resp) >= 4:
                if req[2:4] != resp[2:4]:
                    # 参数不一致，可能是错误（根据具体服务决定是否严格）
                    pass  # 或 return False
            return True
        else:
            return False
        
    @staticmethod
    def hex_output(msg_str):
        # logger.info(f"type of msg_str: {type(msg_str).__name__}")
        if isinstance(msg_str, str):
            formatted = ' '.join([msg_str[i:i + 2] for i in range(0, len(msg_str), 2)])
            return formatted.upper()
        elif isinstance(msg_str, bytes):
            msg_str = msg_str.hex()
            formatted = ' '.join([msg_str[i:i + 2] for i in range(0, len(msg_str), 2)])
            return formatted.upper()
        else:
            logger.info("check the type of data")

    @staticmethod
    def random_bytes_string(n: int) -> str:
        if n < 0:
            raise ValueError("n 必须为非负整数")
        return ''.join(f'{random.randint(0, 255):02X}' for _ in range(n))

    @staticmethod
    def find_dtc_key(search_value, dict):
        for key, value in dict.items():
            if search_value == value[0]:
                return key

    @staticmethod
    def analyze_byte_in_response(response_hex: str, target_config_byte: int, config_dict: dict):
        """
        分析 UDS ReadDataByIdentifier (0x22) 响应中指定配置字节的含义

        :param response_hex: UDS 响应的十六进制字符串，如 "62 F0 11 00 80 ..."
        :param target_config_byte: 要分析的**配置数据字节索引**（对应你表格中的 "Byte" 列，从 0 开始）
        :param config_dict: 配置字典，其中 key 的第一个元素是表格中的 Byte 编号（0,1,2...）
        :return: 解析结果字符串
        """
        # 1. 清理输入：去空格、转大写
        hex_str = response_hex.replace(" ", "").upper()
        if len(hex_str) % 2 != 0:
            raise ValueError("Hex string must have even length")

        # 2. 转为字节数组
        try:
            response_bytes = bytes.fromhex(hex_str)
        except ValueError as e:
            raise ValueError(f"Invalid hex string: {e}")

        # 3. 检查是否为 0x22 的正响应（可选）
        if len(response_bytes) < 3:
            return "❌ Response too short (min 3 bytes for SID+DID)"
        if response_bytes[0] != 0x62:
            return "⚠️ Warning: Not a 0x22 positive response (SID=0x62 expected)"

        # 4. 提取配置数据部分：跳过前3字节 (62 F0 11)
        config_data = response_bytes[3:]

        # 5. 检查目标字节是否在范围内
        if target_config_byte >= len(config_data):
            return (f"❌ Config Byte {target_config_byte} out of range. "
                    f"Config data length: {len(config_data)} bytes (response has {len(response_bytes)} bytes total)")

        target_byte_value = config_data[target_config_byte]

        # 6. 在 config_dict 中查找该 config byte 的所有定义
        matches = [
            (key, value) for key, value in config_dict.items()
            if key[0] == target_config_byte
        ]

        if not matches:
            return f"🔍 Config Byte {target_config_byte}: 0x{target_byte_value:02X} (no definition in config_dict)"

        # 7. 解析每个匹配项
        results = []
        for key, (chinese_name, enum_list) in matches:
            byte_val = target_byte_value

            if len(key) == 2:
                # 单 bit: (byte, bit)
                _, bit = key
                # 按汽车惯例：bit 7 = MSB, bit 0 = LSB
                bit_value = (byte_val >> (7 - bit)) & 1
                found = False
                for enum in enum_list:
                    if f"{bit_value}b:" in enum:
                        results.append(f"  - {chinese_name}: {enum}")
                        found = True
                        break
                if not found:
                    results.append(f"  - {chinese_name}: bit{bit} = {bit_value} (未定义)")

            else:
                # 多 bit: (byte, start_bit, end_bit)
                _, start, end = key
                if start > end:
                    start, end = end, start
                # 提取 [start, end] 位（start 为低位，end 为高位）
                num_bits = end - start + 1
                mask = (1 << num_bits) - 1
                field_val = (byte_val >> start) & mask
                bin_str = format(field_val, f'0{num_bits}b')

                # 尝试匹配枚举
                matched_desc = None
                for enum in enum_list:
                    if ":" not in enum:
                        continue
                    prefix, desc = enum.split(":", 1)
                    desc = desc.strip()
                    # 情况1: 精确匹配 "000b:xxx"
                    if prefix.endswith('b') and prefix[:-1] == bin_str:
                        matched_desc = desc
                        break
                    # 情况2: 范围匹配 "0010b~1111b:reserved"
                    if '~' in prefix and prefix.endswith('b'):
                        try:
                            low_str, high_str = prefix[:-1].split('~')
                            low = int(low_str, 2)
                            high = int(high_str, 2)
                            if low <= field_val <= high:
                                matched_desc = desc
                                break
                        except ValueError:
                            continue

                if matched_desc:
                    results.append(f"  - {chinese_name}: {matched_desc} (bits {start}~{end}, value=0b{bin_str})")
                else:
                    results.append(f"  - {chinese_name}: 0b{bin_str} (未定义)")

        # 8. 返回结果
        header = f"📌 Config Byte {target_config_byte} = 0x{target_byte_value:02X} ({target_byte_value})"
        res = header + "\n" + "\n".join(results)
        logger.info(res)
        return res

    # @staticmethod
    # def get_2ef011_value():
    #     # 加载 Excel 文件
    #     file_path = conf.get('current.f011_data', "CheryE0V下线配置计算表V1.0.xlsx")
    #     cell_location = conf.get("current.cell_location", "B1802")
    #     wb = load_workbook(file_path, data_only=True)  # 替换为你的文件路径
    #
    #     # 选择工作表（默认第一个）
    #     ws = wb.active
    #     # 或者按名称选择：ws = wb["Sheet1"]
    #
    #     # 方法 1：通过单元格名称（如 "C3"）
    #     cell_value = ws[cell_location].value
    #
    #     logger.info(f"要写入的did coding的值是: {cell_value}")
    #     return cell_value



# def send_all_in_one(msg, session_mode=1, security_level=1, qt_write_input=False, rs=True,):
#     """
# 
#     :param msg: 要发送的信息
#     :param rs: 是否需要获取反馈
#     :param qt_write_input: 是否需要输入，是的话需要填入相应的输入框对象
#     :param session_mode:
#     :param security_lever:
#     :return:
#     """
#     with DoIPClient("192.168.69.32", ecu_add, client_logical_address=tester_add,
#                     activation_type=None) as doip:
#         if session_mode == 1:
#             pass
#         elif session_mode == 3:
#             positive_response('1003')
#             # time.sleep(0.5)
#         if security_level == 1:
#             send_security_access_2701()
#         else:
#             pass
# 
#         if not qt_write_input:
#             pass
#         else:
#             write = wash_input(qt_write_input.text())
#             msg += write
#             logger.info(f"will send msg = {msg}")
#         doip.send_diagnostic(unhexlify(msg))
#         logger.info(f"Send: \t{hex_output(msg)}")
#         if rs:
#             response = doip.receive_diagnostic()
#             re_current = response.hex()
#             res_str = hex_output(response.hex())
#             logger.info(f"Response: \t{res_str}")
#             return re_current
#         else:
#             pass







if __name__ == "__main__":
    logger.trace("test trace")
    a = DoIPMessage()
    b = a.basic_send_response('1003')
    a.send_security_access_2701()
#
# with DoIPClient("192.168.69.32", 0x07D0, client_logical_address=0x0E00,
#                 activation_type=None) as doip:
#     # ✅ 明确使用 bytearray
#     # uds_command = bytearray([0x10, 0xC0])  # 进入扩展诊断会话
#     msg = "1003"
#     br = unhexlify(msg)
#     print(br)
#     uds_command = bytearray(br)
#     doip.send_diagnostic(uds_command)
#
#     response = doip.receive_diagnostic()
#     print(f"Response: {response.hex().upper()}")
#
#     # # 读数据示例
#     # read_command = bytearray([0x22, 0xF1, 0x80])  # 读取数据标识符 F190
#     # doip.send_diagnostic(read_command)
#     # response = doip.receive_diagnostic()
#     # print(f"Read Response: {response.hex().upper()}")
#
# # version1
# # from client import DoIPClient
# # from messages import RoutingActivationRequest
# #
# # # 连接到 ECU
# with DoIPClient("192.168.69.32", 0x0300, client_logical_address=0x0E80) as doip:
#     # 发送 UDS 诊断
#     doip.send_diagnostic([0x10, 0xC0])  # 进入诊断会话
#     response = doip.receive_diagnostic()
#     print(f"Response: {response.hex().upper()}")