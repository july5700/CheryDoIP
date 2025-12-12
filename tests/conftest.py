import pytest
import os
from client import DoIPClient
from Lib.ConfigCache import TomlConfig
from loguru import logger
from binascii import unhexlify
from function import DataHandle
from security_access import cal_ace_emac

# # 读取配置（只读一次）
# config = TomlConfig("config.toml")
# ECU_IP = config.get("current.ecu_ip_address")
# TARGET_ADDR = config.get("current.target_address")
# TESTER_ADDR = config.get("current.tester_logical_address")
#
# FUNCTIONAL_ADDR = config.get("current.ecu_functional_address")
# PHYSICAL_ADDR = config.get("current.ecu_logical_address")


class ConfigTable:
    def __init__(self):
        self.config = TomlConfig(os.path.join(os.path.dirname(__file__), "..", "config.toml")).get('current')
        self.ip = self.config.get('ecu_ip_address')
        self.target_addr = self.config.get('target_address')
        self.tester_addr = self.config.get('tester_logical_address')
        self.activate_type = self.config.get('activate_type')


# # class DoIPTestEnvironment:
#     def __init__(self):
#         self.config = TomlConfig(os.path.join(os.path.dirname(__file__), "..", "config.toml")).get('current')
#         self.ip = self.config.get('ecu_ip_address')
#         self.target_addr = self.config.get('target_address')
#         self.tester_addr = self.config.get('tester_logical_address')
#         self.activate_type = self.config.get('activate_type')

        # self.log = logger
        # self.log_level = "INFO"

#     def create_client(self):
#         client = DoIPClient(self.ip, self.target_addr, client_logical_address=self.tester_addr, activation_type=self.activate_type)
#
#         return client
#
#     def session_security_level(self):
#         """
#         00 - level0
#         01 - level1 - 2701+2702
#         10 - level2 - 2705+2706 # 尚不适配
#         11 - level3 - 2761+2762 # 尚不适配
#         -------------------------------------
#         01 - default session
#         10 - extended diagnostic session
#         :return:
#         """
#         pass
#
#     # @staticmethod
#     def basic_send_receive(self, client, msg):
#         _ = unhexlify(msg)
#         client.send_diagnostic(_)
#         logger.info(f"Send: {DataHandle.hex_output(_)}")
#         response = client.receive_diagnostic()
#         logger.info(f"Receive: {DataHandle.hex_output(response)}")
#         return response.hex()
#
#     # @staticmethod
    def security_access_level_1(self, client):
        _ = unhexlify('2701')
        client.send_diagnostic(_)
        seed = client.receive_diagnostic().hex()[4:]
        token = cal_ace_emac(seed)
        new_msg = '2701' + token
        _ = client.send_diagnostic(unhexlify(new_msg))
        final_response = client.receive_diagnostic().hex()
        if final_response == "6702":
            logger.success(f"Security Access successful: {final_response}")
        else:
            logger.error(f"Security Access denied: {final_response}")
#
#
# @pytest.fixture(scope='session')
# def doip_client():
#     env = DoIPTestEnvironment()
#     env.create_client()
#     yield env
#
# @pytest.fixture(scope='function')
# def doip_client_init(doip_client):
#     doip_client.basic_send_receive('1001')
#
# a = DoIPTestEnvironment().get_config()
# print(a[0])
# print(a[-1])
# print("here")
# print("there")
# os._exit(0)
@pytest.fixture(scope='function')
def doip_client():
    # logger.info(f"ECU_IP = {ECU_IP}")
    # logger.info(f"PHYSICAL_ADDR = {PHYSICAL_ADDR}")
    # logger.info(f"TESTER_ADDR = {TESTER_ADDR}")
    # ecu_ip = str(ECU_IP)
    # physical_addr = int(PHYSICAL_ADDR)
    # tester_addr = int(TESTER_ADDR)
    with DoIPClient(ConfigTable().ip, ConfigTable().target_addr, client_logical_address=ConfigTable().tester_addr,
                    activation_type=ConfigTable().activate_type) as doip:
    # with DoIPClient("192.168.69.32", 2000, client_logical_address=3584) as doip:
    #     br = unhexlify('1001')
    #     doip.send_diagnostic(br)
    #     response = doip.receive_diagnostic()
    #     print(response)
    #     print(f"response = {response.hex()}")
        yield doip
        doip.send_diagnostic(unhexlify('1001'))


@pytest.fixture(scope='session')
def doip_client_session():
    # logger.info(f"ECU_IP = {ECU_IP}")
    # logger.info(f"PHYSICAL_ADDR = {PHYSICAL_ADDR}")
    # logger.info(f"TESTER_ADDR = {TESTER_ADDR}")
    # ecu_ip = str(ECU_IP)
    # physical_addr = int(PHYSICAL_ADDR)
    # tester_addr = int(TESTER_ADDR)
    with DoIPClient(ConfigTable().ip, ConfigTable().target_addr, client_logical_address=ConfigTable().tester_addr,
                    activation_type=ConfigTable().activate_type) as doip:
    # with DoIPClient("192.168.69.32", 2000, client_logical_address=3584) as doip:
    #     br = unhexlify('1001')
    #     doip.send_diagnostic(br)
    #     response = doip.receive_diagnostic()
    #     print(response)
    #     print(f"response = {response.hex()}")
        yield doip
        doip.send_diagnostic(unhexlify('1001'))
# @pytest.fixture(scope='function')
# def doip_client_mode_0110():
#     with DoIPClient(ConfigTable().ip, ConfigTable().target_addr, client_logical_address=ConfigTable().tester_addr,
#                     activation_type=ConfigTable().activate_type) as doip:
#         yield doip
