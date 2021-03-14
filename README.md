# network-serializer
network-serializer is the simplest, the most readable, and the most feasible serializer for networking packets.

- Simplicity: organize packets as easy as *struct*
- Readability: byte data is recognized by field names
- Feasibility: change field names or byte data any time and anywhere
- Supportability: support not only byte-like data but also bit-like data

## Installation
```bash
pip install network-serializer
```

## Usage
```python
from network_serializer import Encoder, Decoder
```

### Encoder
You can use Encoder to convert decimal data to bytearray data. Encoder follows the rule of python built-in module [struct](https://docs.python.org/3/library/struct.html) with additional functionalities.

We extend the struct to support 1-bit, 4-bit, and character-like encoding. In other words, the original formats, such as 'x', 'c', 'b', or 'h', still work perfectly with this Encoder.

| Format      | Standard size       | Notes |
| ----------- | ----------------    | ----  |
| u           | 1 bit               |  (1)  |
| o           | 4 bits              |  (1)  |
| t           | multiple 1-byte hex |  (2)  |

Notes:
1. Both 1-bit or 4-bit data needs to be accumulated into bytes for later encoding.
2. One of more characters will be encoded into 4-bit hex value. For example, a character, 'g', will be encoded into 0x67. Please see [ascii table](http://www.asciitable.com/) for conversion.

```python
>>> Encoder(fmt='!H', id=1).encode()
bytearray(b'\x00\x01')
```

Each Encoder object is a sub-class of OrderDict. You can name each network field based on the network protocol you use, and you can modify them even after initialization.

You will pass field names from a network protocol as a key along with a data value to that key. For example, there are 6 field names, that are id, flags, QDCOUNT, ANCOUNT, NSCOUNT, and ARCOUNT.

```python
>>> encoder = Encoder(fmt='!6H', id=17, flags=1 << 8, QDCOUNT=1, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0)
>>> encoder
Encoder([('id', 17), ('flags', 256), ('QDCOUNT', 1), ('ANCOUNT', 0), ('NSCOUNT', 0), ('ARCOUNT', 0)])
>>> encoder['id'] = 18
>>> encoder['id']
18
>>> encoder
Encoder([('id', 18), ('flags', 256), ('QDCOUNT', 1), ('ANCOUNT', 0), ('NSCOUNT', 0), ('ARCOUNT', 0)])

```
### Decoder
After requesting network, you can assign a field name to a response.

To use Decoder, you need to give each field a name and the size of that field. You need to follow the basic format below which separates *bit* and *byte*. For example, *TransactionID='2B'* means that a field, *TransactionID*, contains 2 bytes. *Response='b'* means that *Response* contains only 1 bit.

| Format      | Standard size       | Notes |
| ----------- | ----------------    | ----  |
| b           | 1 bit               |       |
| B           | 1 byte              |       |


```python
>>> Decoder(
        TransactionID='2B',
        Response='b',
        Opcode='4b',
        Authoritative='b',
        Truncated='b',
        RecursionDesired='b',
        RecursionAvailable='b',
        Z='b',
        AnswerAuthenticated='b',
        NonAuthenticated='b',
        ReplyCode='4b',
        Questions='2B',
        AnswerRRs='2B',
        AuthorityRRs='2B',
        AdditionalRRs='2B',
        Queries='16B',
        Answers='16B'
    ).decode(data=b'\x00\x11\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x06google\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x84\x00\x04\xd8:\xc8\xee')
 {
    'TransactionID': b'\x00\x11',
    'Response': '0b1',
    'Opcode': '0b0000',
    'Authoritative': '0b0',
    'Truncated': '0b0',
    'RecursionDesired': '0b1',
    'RecursionAvailable': '0b1',
    'Z': '0b0',
    'AnswerAuthenticated': '0b0',
    'NonAuthenticated': '0b0',
    'ReplyCode': '0b0000',
    'Questions': b'\x00\x01',
    'AnswerRRs': b'\x00\x01',
    'AuthorityRRs': b'\x00\x00',
    'AdditionalRRs': b'\x00\x00',
    'Queries': b'\x06google\x03com\x00\x00\x01\x00\x01',
    'Answers': b'\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x84\x00\x04\xd8:\xc8\xee'
    }
```

### Functions
Encoder(*fmt=''*, *k1=v1*, *k2=v2*, *...*).**encode**()

&nbsp;&nbsp;&nbsp;&nbsp;return a bytearray that encodes *v1*, *v2*, *...* using the format *fmt*.

Decoder(*k1=v1*, *k2=v2*, *...*).**decode**(data)

&nbsp;&nbsp;&nbsp;&nbsp;return a new dictionary in which each field name, *k1*, *k2*, *...*, has a string of bits or a bytearray following the format, *v1*, *v2*, *...* from a bytearray or byte-like object, *data*.

***Please see the [example](https://github.com/bubblemans/network-serializer/blob/main/example.py) which simulates a DNS client.***

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
