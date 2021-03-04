import struct
from collections import OrderedDict


class Serializer(OrderedDict):
    def __init__(self, fmt='', encoding='', *args, **kwargs):
        super(Serializer, self).__init__(*args, **kwargs)
        self.fmt = fmt
        # self._parse_fmt()
        self.encoding = encoding

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

    def _parse_fmt(self):
        """
        this function converts user-input format into a more processable string
        ex: !2H -> !HH
        """
        fmt = self.fmt[0]

        start = 1
        for i, ch in enumerate(self.fmt[1:]):
            if not ch.isdigit():
                fmt += (ch * int(self.fmt[start:i+1]))
                start = i + 1

        self.fmt = fmt
        return fmt

