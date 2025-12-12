from Crypto.Cipher import AES
from Crypto.Hash import CMAC
from binascii import unhexlify
from Lib.ConfigCache import TomlConfig



conf = TomlConfig("config.toml")
sec_key = conf.get('current.sec-key')
def cal_ace_emac(seed):
    """
    给27 01/02用的加密方法，未来可能还要给到27 61/62
    :param seed:
    :return:
    """
    key = unhexlify(sec_key)  # 20251114
    seed = unhexlify(seed)
    mac = CMAC.new(key, seed, ciphermod=AES)
    # print("AES_CMAC:", mac.hexdigest())
    return mac.hexdigest()


if __name__ == '__main__':
    seed = '488706E6454016B72858B1C14337BB7D'
    a = cal_ace_emac(seed)

