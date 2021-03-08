from serializer import Serializer


if __name__ == '__main__':
    serializer = Serializer(fmt='!6H', encoding='dec', id=17, flags=1 << 8, QDCOUNT=1, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0)

    # serializer is a dict
    print(serializer)

    # behave like a dict
    serializer['id'] = 18
    print('id:', serializer['id'])

    # test _parse_format
    print(Serializer(fmt='!2H', encoding='dec', id=17, flags=1 << 8)._parse_fmt())

    # encode
    header = Serializer(fmt='!HHHHHH', encoding='dec', id=17, flags=1 << 8, QDCOUNT=1, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0).encode()
    header_alt = Serializer(fmt='!Hu4uuuuu3u4uHHHH', encoding='dec', id=17, QUERY=0, OPCODE=0, AA=0, TRUNCATION=0, RECURSION_DESIRED=1, RECURSION_AVAILABLE=0, Z=0, RCODE=0, QDCOUNT=1, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0).alt_encode()
    question_name = Serializer(fmt='!BtBt', encoding='dec', ch_length_1=6, domain_name_1='google', ch_length_2=3, domain_name_2='com').encode()
    question_type = Serializer(fmt='!H', encoding='dec', Q_TYPE=1).encode()
    question_class = Serializer(fmt='!H', encoding='dec', Q_CLASS=1).encode()
    query = question_name + question_type + question_class
    print(header + query)
    print(header_alt + query)
