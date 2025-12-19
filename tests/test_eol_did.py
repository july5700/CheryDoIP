import pytest
import allure
from loguru import logger
from function import DoIPClientForTest, DataHandle


@allure.epic("Chery-DoIP")
@allure.feature("EOL DID")
class TestEolDID:

    @pytest.mark.parametrize("msg, expected_response", [
        ("22f187", "62f187"),
        ("22f189", "62f189"),
        ("22f089", "62f089"),
        ("22f013", "62f013"),
        ("22F18A", "62F18A"),
        ("22f18b", "62f18b"),
        ("22f18c", "62f18c"),
        ("22f1ae", "62f1ae"),
        ("22da10", "62da10"),
        ("22f195", "62f195"),
        ("22fd98", "62fd98"),
        ("22fd00", "62fd00"),
        ("22f193", "62f193"),
        ("22fdf6", "62fdf6"),
        ("22fdf7", "62fdf7"),
        ("22da21", "62da21"),
        ("22fd89", "62fd89"),
        ("22fd15", "62fd15"),
        ("22f116", "62f116"),
        ("22fd0c", "62fd0c"),
        ("22fd1c", "62fd1c"),
        ("22fd0b", "62fd0b"),
        ("22fd51", "62fd51"),
        ("22fd53", "62fd53"),
        ("22fd61", "62fd61"),
        ("22fd65", "62fd65"),
        ("22fd40", "62fd40"),
        ("22fd30", "62fd30"),
        ("22fd13", "62fd13"),
        ("22fda4", "62fda4"),
        ("22fda2", "62fda2"),
        ("22fda1", "62fda1"),
        ("22fda0", "62fda0"),
        ("22fd14", "62fd14"),
        ("22fd70", "62fd70"),
        ("22fdb5", "62fdb5"),
        ("22f08b", "62f08b"),
        ("22f083", "62f083"),
    ])
    def test_eol_did(self, doip_client, msg, expected_response):
        DoIPClientForTest(doip_client).basic_send_receive('1060')
        res = DoIPClientForTest(doip_client).basic_send_receive(msg)
        logger.info(f"doip_client object: {doip_client}")
        assert res[:6].upper() == expected_response.upper()


if __name__ == "__main__":
    pytest.main([__file__])