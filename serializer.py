import struct
from collections import OrderedDict


def _parse_fmt(fmt):
        """
        this function converts user-input format into a more processable string
        ex: !2H -> !HH
        """
        new_fmt = fmt[0]
        correspond_fmt = _extract_format(fmt[1:])
        for ch, times in correspond_fmt:
            new_fmt += (ch * times)

        return new_fmt


def _extract_format(fmt):
    """
    Returns:
        a list of tuples: each tuple is a
        ex: [('H', 6)]
    """
    correspond_fmt = []
    start = 0
    for i, ch in enumerate(fmt):
        if not ch.isdigit():
            end = i
            times = int(fmt[start:end]) if start != end else 1
            correspond_fmt.append((ch, times))
            start = end + 1
    return correspond_fmt


class Encoder(OrderedDict):
    def __init__(self, fmt='', *args, **kwargs):
        super(Encoder, self).__init__(*args, **kwargs)
        self.fmt = _parse_fmt(fmt)

    def encode(self):
        """
        u: 1 bit
        o: 4 bits
        t: pack each character as 4-bit hex
        """
        data = bytearray()
        order = self.fmt[0]
        bit_buffer = ''

        for fmt, value in zip(self.fmt[1:], self.values()):
            if fmt == 'u':
                bit_buffer += str(value)
            elif fmt == 'o':
                bit_buffer += str(value) * 4
            elif fmt == 't':
                for ch in value:
                    data += ch.encode()
            else:
                data += struct.pack(order + fmt, value)

            if len(bit_buffer) >= 8:
                data += self.bits_to_bytes(bit_buffer)
                bit_buffer = bit_buffer[8:]

        return data

    def bits_to_bytes(self, bits):

        def _bits_to_int(bits):
            integer = 0
            for i in range(len(bits)):
                factor = len(bits) - i - 1
                integer += int(bits[i]) * (2 ** factor)

            return integer

        integer = _bits_to_int(bits)
        return struct.pack('!B', integer)


class Decoder(OrderedDict):
    def __init__(self, *args, **kwargs):
        """
        B: bytes
        b: bits
        """
        super(Decoder, self).__init__(*args, **kwargs)

    def decode(self, data):
        decoded = dict()
        start_bytes = start_bits = 0
        for field_name, fmt in self.items():
            ch, num = _extract_format(fmt)[0]

            if ch == 'B':
                start, end = start_bytes, start_bytes+num
                decoded[field_name] = data[start:end]
                start_bytes += num
            elif ch == 'b':
                data_in_byte = self.extract_byte(num, start_bytes, data)

                # calculate bits from extracted byte
                bits = self.bytes_to_bits(data_in_byte)
                start, end = start_bits, start_bits+num
                decoded[field_name] = '0b' + bits[start:end]
                start_bits += num

                # check if each bit in extracted byte is used
                if start_bits >= 8:
                    start_bytes += (start_bits // 8)
                    start_bits = 0
        return decoded

    def extract_byte(self, num, start, data):
        num_bytes = num // 8  # 8 bits = 1 byte
        end = start + num_bytes + 1
        return data[start:end]

    def bytes_to_bits(self, data):
        bits = ''
        for byte in data:
            bits += format(byte, '08b')
        return bits
