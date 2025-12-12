import pytest
from loguru import logger
from function import DoIPClientForTest, DataHandle


class TestSystemDID:

    @pytest.mark.parametrize("msg, expected_response", [
        ("2f571d01", "6f571d"),
        ("2f571d02", "6f571d"),
        ("2f571e00", "6f571e"),
        ("2f571e01", "6f571e"),
        ("2f571e02", "6f571e"),
        ("2f571e03", "6f571e"),
        ("2f571f01", "6f571f"),
        ("2f571f02", "6f571f"),
    ])
    def test_control_dtc_setting(self, doip_client, msg, expected_response):
        res = DoIPClientForTest(doip_client).basic_send_receive(msg)
        logger.info(f"doip_client object: {doip_client}")
        assert res[:6] == expected_response



if __name__ == "__main__":
    pytest.main([__file__])