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

def cal_tea_variant(seed, pinp=0xFFFFFFFF):
    """
    The seed-to-key algorithm used in 05/06 (based on the TEA variant)

    Args:
        seed: 64-bit seed value
        pinp: 32-bit PINP value (default: 0xFFFFFFFF)

    Returns:
        64-bit key value
    """
    # Decompose the 64-bit seed into two 32-bit parts
    v = [0, 0]
    v[0] = (seed >> 32) & 0xFFFFFFFF
    v[1] = seed & 0xFFFFFFFF

    # Initialize key array
    k = [0xBE355A5C, 0xD6952BBE, 0x355A5CD6, 0x952B784E]

    # If PINP is not NULL (not all FF), perform XOR with the first key
    if pinp != 0xFFFFFFFF:
        k[0] ^= pinp

    n = 2
    z = v[n-1]
    y = v[0]
    sum_val = 0
    DELTA = 0x9e3779b9

    q = 58
    while q > 0:
        sum_val = (sum_val + DELTA) & 0xFFFFFFFF
        e = (sum_val >> 2) & 3

        for p in range(n-1):
            y = v[p+1]
            mx = (((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((sum_val ^ y) + (k[(p & 3) ^ e] ^ z))
            mx &= 0xFFFFFFFF
            v[p] = (v[p] + mx) & 0xFFFFFFFF
            z = v[p]

        y = v[0]
        mx = (((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((sum_val ^ y) + (k[((n-1) & 3) ^ e] ^ z))
        mx &= 0xFFFFFFFF
        v[n-1] = (v[n-1] + mx) & 0xFFFFFFFF
        z = v[n-1]

        q -= 1

    # The combination result is a 64-bit key
    key = ((v[0] << 32) | v[1]) & 0xFFFFFFFFFFFFFFFF

    return hex(key)[2:]


if __name__ == '__main__':
    seed = '488706E6454016B72858B1C14337BB7D'
    a = cal_ace_emac(seed)
    print(f"a = {a}")
    print(f"type of a = {type(a)}")

    seed2 = 0x7eeb79e497ef3c6d
    b = cal_tea_variant(seed2)
    print(f"b = {b}")
    print(f"type of b = {type(b)}")

