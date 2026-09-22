# dtc_parser.py
from loguru import logger
from chery_dict import DTCNumber, DtcNumberAiBox


class DTCParser:
    """
    解析 UDS 19 02 响应中的 DTC（故障码），
    判断是否包含已知的特定故障，并支持获取详细描述。
    """

    # 预定义已知 DTC 映射表：{ "原始3字节Hex": "标准DTC-描述" }
    KNOWN_DTCS = DTCNumber().dtc_number

    @classmethod
    def _clean_hex(cls, hex_str: str) -> str:
        """清理十六进制字符串：去空格、转大写"""
        return hex_str.replace(" ", "").replace("\t", "").upper()

    @classmethod
    def has_known_dtc(cls, hex_string: str) -> bool:
        """
        判断响应中是否包含任意一个已知 DTC。

        Args:
            hex_string (str): 原始十六进制响应字符串（如 "59 09 D1 89 87 00 ..."）

        Returns:
            bool: 存在已知 DTC 返回 True，否则 False
        """
        try:
            dtc_list = cls._parse_dtcs_with_status(hex_string)
            return any(dtc in cls.KNOWN_DTCS for dtc, status in dtc_list)
        except Exception:
            return False

    @classmethod
    def get_known_dtc_descriptions(cls, hex_string: str):
        """
        获取所有匹配到的已知 DTC 的完整描述列表。

        Args:
            hex_string (str): 原始十六进制响应字符串

        Returns:
            List[tuple]: 匹配到的 DTC 描述和状态的元组列表，如 [("U118987-多功能方向盘开关失去通讯", "current"), ...]
        """
        try:
            dtc_list = cls._parse_dtcs_with_status(hex_string)
            descriptions = []
            for dtc, status in dtc_list:
                if dtc in cls.KNOWN_DTCS:
                    description = cls.KNOWN_DTCS[dtc][1]
                    status_text = "current" if status == "09" else "history" if status == "08" else "unknown"
                    descriptions.append((f"{cls.KNOWN_DTCS[dtc][0]}-{description}", status_text))
            return descriptions
        except Exception:
            return []

    @classmethod
    def get_known_dtc_by_status(cls, hex_string: str):
        """
        按状态分类获取已知 DTC。

        Args:
            hex_string (str): 原始十六进制响应字符串

        Returns:
            tuple: (current_dtcs, history_dtcs) 两个列表，分别包含当前故障和历史故障
        """
        try:
            dtc_list = cls._parse_dtcs_with_status(hex_string)
            current_dtcs = []
            history_dtcs = []

            for dtc, status in dtc_list:
                if dtc in cls.KNOWN_DTCS:
                    description = cls.KNOWN_DTCS[dtc][1]
                    dtc_info = f"{cls.KNOWN_DTCS[dtc][0]}-{description}"

                    if status == "09":
                        current_dtcs.append(dtc_info)
                    elif status == "08":
                        history_dtcs.append(dtc_info)
                    else:
                        # 其他状态也归为未知状态，但可以视需要调整
                        logger.info(f"发现未知状态字节 {status} 对应故障码 {dtc}")

            return current_dtcs, history_dtcs
        except Exception as e:
            logger.error(f"解析DTC时出错: {e}")
            return [], []

    @classmethod
    def _parse_dtcs_with_status(cls, hex_string: str):
        """
        内部方法：从十六进制字符串中提取所有 DTC 及其状态字节

        Returns:
            List[tuple]: DTC 和状态字节的元组列表，如 [("D18987", "09"), ("C14187", "08"), ...]
        """
        clean = cls._clean_hex(hex_string)
        if len(clean) % 2 != 0:
            raise ValueError("Invalid hex string: odd length")

        # 转为字节列表
        bytes_list = [clean[i:i + 2] for i in range(0, len(clean), 2)]

        if len(bytes_list) < 2:
            return []

        # 跳过服务响应头 59 09
        payload = bytes_list[3:]

        dtc_status_pairs = []
        i = 0
        while i + 4 <= len(payload):  # 每组4字节：3字节DTC + 1字节状态
            # 取前3个字节组成 DTC key
            dtc = "".join(payload[i:i + 3])
            # 取第4个字节作为状态
            status = payload[i + 3]
            dtc_status_pairs.append((dtc, status))
            i += 4  # 跳过整组（4字节）

        return dtc_status_pairs

    @classmethod
    def _parse_dtcs(cls, hex_string: str):
        """
        内部方法：从十六进制字符串中提取所有 DTC（3-byte keys）- 保持向后兼容
        """
        dtc_status_pairs = cls._parse_dtcs_with_status(hex_string)
        return [dtc for dtc, status in dtc_status_pairs]

    @classmethod
    def check_dtc_and_print(cls, hex_string: str, target_dtc: str) -> tuple:
        """
        检查指定的 DTC（如 "D18987"）是否存在于响应数据中。
        如果存在，打印其标准故障码和描述，并返回 True；否则返回 False。

        Args:
            hex_string (str): 原始十六进制响应字符串，例如 "59 09 D1 89 87 00 ..."
            target_dtc (str): 要查找的 6 位原始 DTC（大写），例如 "D18987"

        Returns:
            tuple: 存在返回 True + dtc_num + dtc description，否则 False。
        """
        # 标准化输入：去空格、转大写
        target = target_dtc.strip().upper()
        if target not in cls.KNOWN_DTCS:
            logger.info(f"🔍 提示：DTC '{target}' 不在已知故障码列表中。")
            # 但仍可检查它是否出现在响应中（即使无描述）

        try:
            dtc_list = cls._parse_dtcs_with_status(hex_string)
        except Exception as e:
            logger.info(f"解析响应失败: {e}")
            return False, f"未找到故障码: {target}"

        # 查找目标 DTC 及其状态
        for dtc, status in dtc_list:
            if dtc == target:
                if target in cls.KNOWN_DTCS:
                    description = cls.KNOWN_DTCS[target][1]
                    status_text = "当前故障" if status == "09" else "历史故障" if status == "08" else f"未知状态({status})"
                    logger.info(f"找到故障码: {description} - {status}:{status_text}")
                    return True, f"找到故障码: {cls.KNOWN_DTCS[target][0]}-{description} ({status_text})"
                else:
                    logger.info(f"找到未知故障码: {target}（无描述）")
                    return True, f"找到故障码: {target}（无描述）"

        logger.info(f"未在响应中找到故障码: {target}")
        return False, f"未找到故障码: {target}"





class EnhancedDTCParser:
    """
    增强版 DTC 解析器，支持完整的 DTC 状态位解析（bitmask），
    并使用新的 dtc_number 映射表（含 Alt Display、中英文描述）。
    """

    KNOWN_DTCS = DtcNumberAiBox().dtc_number

    DTC_STATUS_BITS = {
        "00": "Test failed",
        "01": "Test failed during this monitoring or operational cycle",
        "02": "Pending DTC",
        "03": "Confirmed DTC",
        "04": "Test not completed since last clear",
        "05": "Test failed since last clear",
        "06": "Test not completed during this monitoring or operational cycle",
        "07": "Warning indicator requested",
    }

    @classmethod
    def _clean_hex(cls, hex_str: str) -> str:
        """清理十六进制字符串：去空格、转大写"""
        return hex_str.replace(" ", "").replace("\t", "").upper()

    @classmethod
    def _parse_dtcs_with_status(cls, hex_string: str):
        """
        从 UDS 19 02 响应中提取 DTC + 状态字节。
        格式: 59 02 [DTCStatusAvailabilityMask] [DTC(3B) + Status(1B)]...
        """
        clean = cls._clean_hex(hex_string)
        if len(clean) % 2 != 0:
            raise ValueError("Invalid hex string: odd length")

        bytes_list = [clean[i:i + 2] for i in range(0, len(clean), 2)]

        if len(bytes_list) < 3 or bytes_list[0] != "59" or bytes_list[1] != "02":
            logger.warning("Response does not start with 59 02")
            return []

        # 跳过 59 02 [DTCStatusAvailabilityMask] → 前3字节
        payload = bytes_list[3:]

        dtc_status_pairs = []
        i = 0
        while i + 4 <= len(payload):
            dtc = "".join(payload[i:i + 3])
            status_byte = payload[i + 3]
            dtc_status_pairs.append((dtc, status_byte))
            i += 4
        return dtc_status_pairs

    @classmethod
    def _decode_status_byte(cls, status_hex: str) -> list:
        try:
            val = int(status_hex, 16)
        except ValueError:
            logger.warning(f"Invalid status byte: {status_hex}")
            return ["Invalid status"]

        active = []
        for bit in range(8):
            if val & (1 << bit):
                active.append(cls.DTC_STATUS_BITS.get(bit, f"Unknown bit {bit}"))
        return active or ["No active status bits"]

    @classmethod
    def has_known_dtc(cls, hex_string: str) -> bool:
        try:
            dtc_list = cls._parse_dtcs_with_status(hex_string)
            return any(dtc in cls.KNOWN_DTCS for dtc, _ in dtc_list)
        except Exception as e:
            logger.error(f"has_known_dtc error: {e}")
            return False

    @classmethod
    def get_known_dtc_descriptions(cls, hex_string: str):
        try:
            dtc_list = cls._parse_dtcs_with_status(hex_string)
            results = []
            for dtc, status_hex in dtc_list:
                if dtc in cls.KNOWN_DTCS:
                    alt_code = cls.KNOWN_DTCS[dtc][0]
                    chinese_desc = cls.KNOWN_DTCS[dtc][1]
                    status_texts = cls._decode_status_byte(status_hex)
                    results.append((f"{alt_code}-{chinese_desc}", status_texts))
            return results
        except Exception as e:
            logger.error(f"get_known_dtc_descriptions error: {e}")
            return []

    @classmethod
    def get_known_dtc_with_raw_status(cls, hex_string: str):
        """
        解析 UDS 19 02 响应，返回所有已知 DTC 及其原始状态字节（如 '01', '03' 等）。
        不再做“当前/历史”分类，仅如实呈现状态码。

        返回格式: List[Tuple[str, str]]
          - 第一项: "U118E00-以太网上未连接..."
          - 第二项: 原始状态字节字符串，如 "01"
        """
        try:
            dtc_list = cls._parse_dtcs_with_status(hex_string)
            results = []

            for dtc, status_hex in dtc_list:
                if dtc not in cls.KNOWN_DTCS:
                    continue

                alt, desc = cls.KNOWN_DTCS[dtc][0], cls.KNOWN_DTCS[dtc][1]
                # logger.info(f"alt, desc= {alt},{desc}")
                entry = f"{alt}-{desc}"
                # 保持 status_hex 为大写两位字符串，如 "01"
                normalized_status = status_hex.upper().zfill(2)
                # logger.info(f"normalized_status:{normalized_status}")
                status_des = cls.DTC_STATUS_BITS[str(normalized_status)]
                results.append((entry, normalized_status, status_des))

            return results
        except Exception as e:
            logger.error(f"get_known_dtc_with_raw_status error: {e}")
            return []

    # ✅ 关键：这个方法必须在类内部！
    @classmethod
    def check_dtc_and_print(cls, hex_string: str, target_dtc: str):
        """
        检查指定 DTC 是否存在，并打印详细状态。
        """
        target = target_dtc.strip().upper()
        try:
            dtc_list = cls._parse_dtcs_with_status(hex_string)
        except Exception as e:
            logger.error(f"解析失败: {e}")
            return False, f"解析失败: {e}"

        for dtc, status_hex in dtc_list:
            if dtc == target:
                status_descs = cls._decode_status_byte(status_hex)
                if target in cls.KNOWN_DTCS:
                    alt = cls.KNOWN_DTCS[target][0]
                    chn = cls.KNOWN_DTCS[target][1]
                    msg = f"找到故障码: {alt}-{chn} | 状态: {', '.join(status_descs)}"
                    logger.info(msg)
                    return True, msg
                else:
                    msg = f"找到未知故障码: {target} | 状态: {', '.join(status_descs)}"
                    logger.info(msg)
                    return True, msg

        msg = f"未找到故障码: {target}"
        logger.info(msg)
        return False, msg

def main_chery_8397():
    response = "59 02 09 D2 00 87 09 C1 31 87 09 D1 61 87 09 C1 03 87 09 C1 29 87 09 C1 51 87 09 D2 56 87 09 D1 62 87 09 D2 01 87 09 D1 69 87 09 C1 28 87 09 D1 97 87 09 D1 68 87 09 D1 89 87 09 C1 86 87 09 C1 41 87 09 D1 94 87 09 C1 42 87 09 D2 14 87 09 C1 11 87 09"
    current_dtcs, history_dtcs = EnhancedDTCParser.get_known_dtc_by_status(response)

    if current_dtcs:
        logger.info("🔍 检测到当前故障！")
        for dtc_desc in current_dtcs:
            logger.info(f"  - {dtc_desc}")
    else:
        logger.info("✅ 未发现当前故障")

    if history_dtcs:
        logger.info("🔍 检测到历史故障！")
        for dtc_desc in history_dtcs:
            logger.info(f"  - {dtc_desc}")
    else:
        logger.info("✅ 未发现历史故障")

    # 测试单个DTC检查
    res1 = DTCParser.check_dtc_and_print(response, "D18987")
    res2 = DTCParser.check_dtc_and_print(response, "C12987")
    res3 = DTCParser.check_dtc_and_print(response, "C14187")
    res4 = DTCParser.check_dtc_and_print(response, "C13187")
    res5 = DTCParser.check_dtc_and_print(response, "C10387")
    res6 = DTCParser.check_dtc_and_print(response, "C15187")

def main_aibox():
    response = "59 02 07 d1 4b 15 02 d1 8e 00 04 d1 4c 51 03"

    # 获取所有已知 DTC + 原始状态码
    dtc_status_list = EnhancedDTCParser.get_known_dtc_with_raw_status(response)
    print(f"dtc_status_list = {dtc_status_list}")

    if dtc_status_list:
        logger.info("🔍 检测到以下故障码及其原始状态码：")
        for desc, status, description in dtc_status_list:
            logger.info(f"  - {desc} | 状态: {status} | {description}")
    else:
        logger.info("✅ 未发现任何已知故障码")

    # 单个 DTC 检查（可选保留）
    logger.info("\n🔍 单个 DTC 检查:")
    EnhancedDTCParser.check_dtc_and_print(response, "D18E00")
    EnhancedDTCParser.check_dtc_and_print(response, "D14B15")
    EnhancedDTCParser.check_dtc_and_print(response, "D14C51")

    print(EnhancedDTCParser.get_known_dtc_with_raw_status(response))
if __name__ == "__main__":
    main_aibox()