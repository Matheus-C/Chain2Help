def hex2str(hex):
    """Decode a hex string prefixed with "0x" into a UTF-8 string"""
    return bytes.fromhex(hex[2:]).decode("utf-8")


def str2hex(str):
    """Encode a string as a hex string, adding the "0x" prefix"""
    return "0x" + str.encode("utf-8").hex()
