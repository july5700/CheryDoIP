import pytest
from loguru import logger
from function import DoIPClientForTest, DataHandle


class TestApplicationService:
    @pytest.mark.parametrize("msg, expected_response", [
        ("1001", "5001"),
        ("1003", "5003")])
    def test_diagnostic_session_control(self, doip_client, msg, expected_response):
        res = DoIPClientForTest(doip_client).basic_send_receive(msg)
        logger.info(f"doip_client object: {doip_client}")
        assert res[:4] == expected_response

    @pytest.mark.skip(reason="功能未实现;增加重启后验证的step")
    @pytest.mark.parametrize("msg, expected_response", [
        ("1101", "5101"),
        ("1103", "5103")])
    def test_ecu_reset(self, doip_client, msg, expected_response):
        res = DoIPClientForTest(doip_client).basic_send_receive(msg)
        logger.info(f"doip_client object: {doip_client}")
        assert res[:4] == expected_response

    def test_security_access_level_1(self, doip_client):
        res = DoIPClientForTest(doip_client).security_access_level_1()
        logger.info(f"doip_client object: {doip_client}")
        assert res[:4] == '6702'


    @pytest.mark.skip(reason="本机版本不匹配此功能")
    @pytest.mark.parametrize("msg, expected_response", [
        ("280001", "680001"),
        ("280002", "680002"),
        ("280003", "680003"),
        ("280301", "680301"),
        ("280302", "680302"),
        ("280303", "680303"),
    ])
    def test_communication_control(self, doip_client, msg, expected_response):
        res = DoIPClientForTest(doip_client).basic_send_receive(msg)
        logger.info(f"doip_client object: {doip_client}")
        assert res[:4] == expected_response

    @pytest.mark.parametrize("msg, expected_response", [
        ("8501", "c501"),
        ("8502", "c502"),
    ])
    def test_control_dtc_setting(self, doip_client, msg, expected_response):
        res = DoIPClientForTest(doip_client).basic_send_receive(msg)
        logger.info(f"doip_client object: {doip_client}")
        assert res[:4] == expected_response

    def test_tester_present(self, doip_client):
        res = DoIPClientForTest(doip_client).basic_send_receive('3e00')
        assert res[:4] == '7e00'


    def test_read_dtc_information(self, doip_client):
        # DoIPClientForTest(doip_client).basic_send_receive('1003')
        # DoIPClientForTest(doip_client).security_access_level_1()
        res = DoIPClientForTest(doip_client).basic_send_receive('1902ff')
        logger.info(f"len of dtc {len(res)}")
        logger.critical(f"dtc {res}")
        assert res[:4] == '5909'
        assert len(res) >= 12  # 至少有一个DTC

    def test_clear_diagnostic_infomation(self, doip_client):
        dtc_res = DoIPClientForTest(doip_client).basic_send_receive('1902ff')
        assert len(dtc_res) >= 12
        res = DoIPClientForTest(doip_client).basic_send_receive('14ffffff')
        assert res[:2] == '54'
        dtc_res_new = DoIPClientForTest(doip_client).basic_send_receive('1902ff')
        assert len(dtc_res_new) == 4

    def test_read_data_by_identifier(self, doip_client):
        res = DoIPClientForTest(doip_client).basic_send_receive('22f187')
        assert res[:6] == '62f187'

    def test_write_data_by_identifier(self, doip_client):
        DoIPClientForTest(doip_client).basic_send_receive('1003')
        DoIPClientForTest(doip_client).security_access_level_1()
        read_res_before_write = DoIPClientForTest(doip_client).basic_send_receive('22f190')
        logger.critical(f"read_res_before_write= {read_res_before_write}")
        random_byte = DataHandle().random_bytes_string(17)
        res_after_write = DoIPClientForTest(doip_client).basic_send_receive('2ef190' + random_byte)
        logger.critical(f"res_after_write= {res_after_write}")
        assert res_after_write == '6ef190'
        read_res_after_write = DoIPClientForTest(doip_client).basic_send_receive('22f190')
        assert read_res_after_write == "62f190"+random_byte.lower()
        assert read_res_after_write != read_res_before_write

    def test_routine_control(self, doip_client):
        DoIPClientForTest(doip_client).basic_send_receive('1003')
        DoIPClientForTest(doip_client).security_access_level_1()
        res = DoIPClientForTest(doip_client).basic_send_receive('31015783')
        assert res[:6] == '710102'


if __name__ == "__main__":
    pytest.main([__file__])