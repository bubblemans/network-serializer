import socket
from serializer import Encoder, Decoder, _parse_fmt


if __name__ == '__main__':
    encoder = Encoder(fmt='!6H', id=17, flags=1 << 8, QDCOUNT=1, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0)

    # serializer is a dict
    print(encoder)

    # behave like a dict
    encoder['id'] = 18
    print('id:', encoder['id'])

    # test _parse_format
    print()
    print('--- Test _parse_format ---')
    print(_parse_fmt('!2H'))
    print(_parse_fmt('!H'))
    print(_parse_fmt('!2H2H'))
    print(_parse_fmt('!HH'))
    print('--- End Test _parse_format ---')

    # encode DNS req
    print()
    print('--- Test DNS Request ---')
    header = Encoder(fmt='!HHHHHH', id=17, flags=1 << 8, QDCOUNT=1, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0).encode()
    question_name = Encoder(fmt='!BtBtB', ch_length_1=6, domain_name_1='google', ch_length_2=3, domain_name_2='com', delimiter=0).encode()
    question_type = Encoder(fmt='!H', Q_TYPE=1).encode()
    question_class = Encoder(fmt='!H', Q_CLASS=1).encode()
    query = question_name + question_type + question_class
    request = header + query
    print(request)
    print('--- End Test DNS Request ---')

    # decode DNS res
    print()
    print('--- Test DNS Response ---')
    sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = '8.8.8.8'
    port = 53
    sd.connect((host, port))
    sd.send(request)
    raw_response = sd.recv(1024)
    print(raw_response)
    print(Decoder(fmt='2Bb4bbbbbbbb4b2B2B2B2B16B16B', data=raw_response).decode(
        'Transaction ID',
        'Response',
        'Opcode',
        'Authoritative',
        'Truncated',
        'Recursion desired',
        'Recursion available',
        'Z',
        'Answer authenticated',
        'Non-authenticated',
        'Reply code',
        'Questions',
        'Answer RRs',
        'Authority RRs',
        'Additional RRs',
        'Queries',
        'Answers'
    ))
    print('--- End Test DNS Response ---')
