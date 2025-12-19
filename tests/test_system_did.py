import pytest
import allure
from loguru import logger
from function import DoIPClientForTest, DataHandle


@allure.epic("Chery-DoIP")
@allure.feature("System DID")
class TestSystemDID:

    @pytest.mark.parametrize("msg, expected_response", [
        ("22f180", "62f180"),
        ("22f187", "62f187"),
        ("22f189", "62f189"),
        ("22f089", "62f089"),
        ("22f013", "62f013"),
        ("22f18a", "62f18a"),
        ("22f18b", "62f18b"),
        ("22f18c", "62f18c"),
        ("22f186", "62f186"),
        ("22f160", "62f160"),

        ("22f161", "62f161"),
        ("22f091", "62f091"),
        ("22f083", "62f083"),
        ("22f084", "62f084"),
        ("22f086", "62f086"),
        ("22f087", "62f087"),
        ("22f08b", "62f08b"),

    ])
    def test_system_did(self, doip_client_session, msg, expected_response):
        res = DoIPClientForTest(doip_client_session).basic_send_receive(msg)
        logger.info(f"doip_client_session object: {doip_client_session}")
        assert res[:6].upper() == expected_response.upper()

    def test_write_data_by_identifier_f190(self, doip_client_session):
        DoIPClientForTest(doip_client_session).basic_send_receive('1003')
        DoIPClientForTest(doip_client_session).security_access_level_1()
        read_res_before_write = DoIPClientForTest(doip_client_session).basic_send_receive('22f190')
        logger.critical(f"read_res_before_write= {read_res_before_write}")
        random_byte = DataHandle().random_bytes_string(17)
        res_after_write = DoIPClientForTest(doip_client_session).basic_send_receive('2ef190' + random_byte)
        logger.critical(f"res_after_write= {res_after_write}")
        assert res_after_write.upper() == '6ef190'.upper()
        read_res_after_write = DoIPClientForTest(doip_client_session).basic_send_receive('22f190')
        assert read_res_after_write.upper() == "62f190"+random_byte.upper()
        assert read_res_after_write.upper() != read_res_before_write.upper()

    def test_write_data_by_identifier_f0fe(self, doip_client_session):
        DoIPClientForTest(doip_client_session).basic_send_receive('1003')
        DoIPClientForTest(doip_client_session).security_access_level_1()
        read_res_before_write = DoIPClientForTest(doip_client_session).basic_send_receive('22f0fe')
        logger.critical(f"read_res_before_write= {read_res_before_write}")
        random_byte = DataHandle().random_bytes_string(15)
        res_after_write = DoIPClientForTest(doip_client_session).basic_send_receive('2ef0fe' + random_byte)
        logger.critical(f"res_after_write= {res_after_write}")
        assert res_after_write.upper() == '6ef0fe'.upper()
        read_res_after_write = DoIPClientForTest(doip_client_session).basic_send_receive('22f0fe')
        assert read_res_after_write.upper() == "62f0fe"+random_byte.upper()
        assert read_res_after_write.upper() != read_res_before_write.upper()


if __name__ == "__main__":
    pytest.main([__file__])