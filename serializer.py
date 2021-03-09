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
    [summary]

    Args:
        fmt ([type]): [description]

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

        Returns:
            [type]: [description]
        """
        data = bytearray()
        order = self.fmt[0]
        for fmt, value in zip(self.fmt[1:], self.values()):
            if fmt == 't':
                for ch in value:
                    data += ch.encode()
            else:
                data += struct.pack(order + fmt, value)
        return data


class Decoder(OrderedDict):
    def __init__(self, fmt, data, *args, **kwargs):
        """
        B: bytes
        b: bits

        Args:
            fmt ([type]): [description]
            data ([type]): [description]
        """
        super(Decoder, self).__init__(*args, **kwargs)
        self.fmt = fmt
        self.data = data

    def decode(self, *args, **kwargs):
        """
        [summary]
        """
        data = self._extract_data()

        for field_name, value in zip(args, data):
            self[field_name] = value

        return self

    def _extract_data(self):
        data = []
        correspond_fmt = _extract_format(self.fmt)
        start = 0
        start_bits = 0
        for ch, num in correspond_fmt:
            if ch == 'B':
                data.append(self.data[start:start+num])
                start += num
            elif ch == 'b':
                num_bytes = num // 8  # 8 bits = 1 byte
                data_in_byte = self.data[start:start+num_bytes+1]
                bits = ''
                for byte in data_in_byte:
                    bits += format(byte, '08b')
                data.append('0b' + bits[start_bits:start_bits+num])
                start_bits += num

                if start_bits >= 8:
                    start += (start_bits // 8)
                    start_bits = 0

        return data
