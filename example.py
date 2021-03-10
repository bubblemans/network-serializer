import socket
from serializer import Encoder, Decoder, _parse_fmt


if __name__ == '__main__':
    # behave like a dict
    encoder = Encoder(fmt='!6H', id=17, flags=1 << 8, QDCOUNT=1, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0)
    print(encoder)
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
    encoder = Encoder(
        fmt='!Huo7uoHHHHBtBtBHH',
        id=17,
        Response=0,
        Opcode=0,
        AA=0,
        Truncated=0,
        RecursionDesired=1,
        RA=0,
        Z=0,
        Dummy_1=0,
        NonAuthenticated=0,
        RCODE=0,
        QDCOUNT=1,
        ANCOUNT=0,
        NSCOUNT=0,
        ARCOUNT=0,
        domain_name_1_length=6,
        domain_name_1='google',
        domain_name_2_length=3,
        domain_name_2='com',
        delimiter=0,
        Q_TYPE=1,
        Q_CLASS=1
    )
    request = encoder.encode()
    print('Raw Request:', encoder)
    print('Encoded Request:', request)
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
    print('Raw Response:', raw_response)
    print('Decoded Response:', Decoder(
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
    ).decode(data=raw_response))
    print('--- End Test DNS Response ---')
