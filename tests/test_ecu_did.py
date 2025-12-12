import pytest
from loguru import logger
from function import DoIPClientForTest, DataHandle


class TestECUDID:

    @pytest.mark.parametrize("msg, expected_response", [
        ("225703", "625703"),
        ("225708", "625708"),
        ("22570e", "62570e"),
        ("225717", "625717"),
        ("225721", "625721"),

        ("225722", "625722"),
        ("225723", "625723"),
        ("225724", "625724"),
        ("225727", "625727"),
        ("225728", "625728"),

        ("225729", "625729"),
        ("22572a", "62572a"),

        ("225739", "625739"),
        ("22572b", "62572b"),

        ("22572C", "62572C"),
        ("22572D", "62572D"),
        ("22572E", "62572E"),
        ("22572F", "62572F"),
        ("225730", "625730"),

        ("225731", "625731"),
        ("22573A", "62573A"),
        ("22573B", "62573B"),
        ("22573C", "62573C"),
        ("22573D", "62573D"),

        ("22573F", "62573F"),
        ("225740", "625740"),
        ("225741", "625741"),
        ("225742", "625742"),
        ("225743", "625743"),

        ("225744", "625744"),
        ("225745", "625745"),
        ("22574D", "62574D"),
        ("22574E", "62574E"),
        ("22574F", "62574F"),

        ("225750", "625750"),
        ("225751", "625751"),
        ("225752", "625752"),
        ("225753", "625753"),
        ("225784", "625784"),

    ])
    def test_control_dtc_setting(self, doip_client, msg, expected_response):
        res = DoIPClientForTest(doip_client).basic_send_receive(msg)
        logger.info(f"doip_client object: {doip_client}")
        assert res[:6] == expected_response

    def test_write_data_by_identifier_d008(self, doip_client):
        # DoIPClientForTest(doip_client).basic_send_receive('1003')
        # DoIPClientForTest(doip_client).security_access_level_1()
        read_res_before_write = DoIPClientForTest(doip_client).basic_send_receive('22d008')
        logger.critical(f"read_res_before_write= {read_res_before_write}")
        random_byte = DataHandle().random_bytes_string(4)
        res_after_write = DoIPClientForTest(doip_client).basic_send_receive('2ed008' + random_byte)
        logger.critical(f"res_after_write= {res_after_write}")
        assert res_after_write == '6ed008'
        read_res_after_write = DoIPClientForTest(doip_client).basic_send_receive('22d008')
        assert read_res_after_write == "62d008"+random_byte.lower()
        assert read_res_after_write != read_res_before_write

if __name__ == "__main__":
    pytest.main([__file__])