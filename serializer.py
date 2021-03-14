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
        self.fmt = fmt

    def encode(self):
        """
        u: 1 bit
        o: 4 bits
        t: pack each character as 1-byte hex
        """
        parsedfmt = _parse_fmt(self.fmt)
        data = bytearray()
        order = self.fmt[0]
        bit_buffer = ''
        for fmt, value in zip(parsedfmt[1:], self.values()):
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

    # exist to solve an issue with IP packets; since encode() can't handle bit fields that aren't 1 bit or 4 bits long
    def alt_encode (self):
        '''
        # alternate version of the main function of serializer that works better with fields of irregular bit sizes
        # expands on struct.pack, allowing for fields smaller than a byte to be represented with the letter 'u'
        #
        # NOTE: current version only supports 'u', not 'o' or 't'
        #
        # WARNING: numbers in front of an 'u' determine size of the field in bits, similar to 's' in struct.pack()
        #
        # returns a stream of bytes
        '''

        (originalString, originalArgs) = preprocessFormatToAddStrings(self.fmt, list(self.values())) # replaces 't' characters with 's' character with the right length and changes strings to bytes
        currentString = originalString # holds the variable string; shrinks whenever findFirstBitInFormatString() is run on it
        currentArgs = originalArgs # holds the args tuple; shrinks after every struct.pack() call
        isBigEndian = False # for adding an '!' to every string but the first leftString if the format string starts with an '!'
        byteStream = bytearray() # the return value; a stream of bytes
        bitCount = 0 # holds the number of bits currently in use; makes sure all bits fit nicely into bytes before letting struct.pack() run on anything
        currentBitFieldsValue = 0 # holds all the current fields less than a bit in size; is passed into struct.pack() once no new bit fields are detected

        endiannessCharacter = '' # this is added to later strings in order to make it little or big endian
        if currentString[0] == '!' or currentString[0] == '>': # by default, strings are little endian
            isBigEndian = True
            endiannessCharacter = '!' # so we only set this character when we want big endian

        # first run happens outside any loops in order to account for currentString possibly being the same as formatString (if so, it can be passed directly to struct.pack)
        (leftString, bitString, currentString) = findFirstBitInFormatString(currentString)

        # if string remains the same, then we don't need to do anything extra
        if currentString == originalString:
            return byteStream + struct.pack(currentString, *currentArgs)
            
        # loop ends if there are no more 'u's
        while bitString != "":
            if leftString != "": # if there haven't been any unhandled bit fields before this segment, then just hand it off to struct.pack()
                if bitCount > 0: # if there are unhandled bit fields, check to make sure the bit fields are valid, then add them to the byte stream before handling the new left segment
                    if bitCount % 8 == 0: # bit fields must fit evenly into bytes; otherwise we can't put them into bytes for the byte stream
                        dataType = calculateStringOfFormatCharacters(bitCount) # first we calculate the format string
                        #TODO: Allow this to handle multiple format characters
                        print(currentBitFieldsValue)
                        byteStream += struct.pack(endiannessCharacter + dataType, currentBitFieldsValue) # only passes in one field and one argument
                        bitCount = 0 # resets since we just passed in the current bit fields
                        currentBitFieldsValue = 0 # resets since we just passed in the arg
                    else:
                        raise ValueError('Bit fields do not divide evenly into bytes') # if it doesn't split evenly, we're not going to touch it
                if (leftString[0] != '!' and leftString[0] != '>') and isBigEndian: # if it doesn't have an endianness character in front and it's big endian
                    leftString = endiannessCharacter + leftString # add a '!' in front
                byteStream += struct.pack(leftString, *currentArgs[:countNumberOfFieldsInFormatString(leftString)]) # uses struct.pack() to add as many fields as the left string specifies, using the right number of args
                currentArgs = currentArgs[countNumberOfFieldsInFormatString(leftString):] # remove the args we used from the args list

            if bitString != "": # if there's a bit field string, we need to handle it
                sizeOfField = 0
                if len(bitString) == 1: # if the length is 1, there can't be a leading number
                    sizeOfField = 1 # so the field is only 1 bit
                else:
                    sizeOfField = findNumberAtFrontOfString(bitString) # otherwise, use the number before the 'u' as the field size
                if currentArgs[0] >= (2 ** sizeOfField): # if the argument doesn't fit in the given field, we can't use it
                    raise ValueError('Argument too large for specified field')
                bitCount += sizeOfField # bitCount needs to be increased by the number of bits in the current field
                currentBitFieldsValue = currentBitFieldsValue << sizeOfField # the argument needs to be left shifted to make room for the new field's argument
                currentBitFieldsValue = currentBitFieldsValue | currentArgs[0] # put the new field's argument in using bitwise OR
                currentArgs = currentArgs[1:] # remove the argument we just used from the list of arguments

            (leftString, bitString, currentString) = findFirstBitInFormatString(currentString) # finally, refresh the three strings based on the current remaining string
            # if currentString is empty when this is run, all strings will be empty, including bitString, ending the loop

        #TODO: remove this replicated codeblock
        if bitCount > 0: # had to repeat it again to account for the scenario where there are no more 'u's in the remaining string
            if bitCount % 8 == 0: 
                dataType = calculateStringOfFormatCharacters(bitCount)
                byteStream += struct.pack(endiannessCharacter + dataType, currentBitFieldsValue) 
                bitCount = 0
                currentBitFieldsValue = 0
            else:
                raise ValueError('Bit fields do not divide evenly into bytes')
        byteStream += struct.pack(endiannessCharacter + currentString, *currentArgs) # since we left the loop because there's no more 'u's in the string, just pass the remaining string to struct.pack()

        return byteStream # finally, return the byte stream


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

# functions used for alt_encode()
def findNumberAtFrontOfString(stringWithNumberAtFront):
    '''
    # counts the number at the front of a string, stopping when it hits anything that's not a digit
    '''

    sumOfDigits = 0
    for character in stringWithNumberAtFront:
        if character.isdigit():
            sumOfDigits *= 10 # move the current sum over one place
            sumOfDigits += int(character) # add current character to sum as an integer
        else:
            break
    return sumOfDigits

def countNumberOfFieldsInFormatString(inString):
    '''
    # counts the number of fields in the input string to know how many args to pass to struct.pack()
    # returns that count
    '''
    count = 0
    subcount = 0
    wasLastCharANum = False
    for character in inString:
        if character != '!' and character != '<' and character != '>' and character != '@' and character != '=': # we don't want to count a special character, since they're not fields
            if character.isdigit(): # if it's a number, add that to the sum
                subcount *= 10
                subcount += int(character)
                wasLastCharANum = True
            elif character == 's' or character == 'u': # if it's 's' or 'u', the number in front doesn't change the number of fields, so reset the sub count and increment the count
                count += 1
                subcount = 0
                wasLastCharANum = False
            elif not wasLastCharANum: # if a letter didn't have a number before it, increment the count
                count += 1
            else: # if a letter had a number before it, add the sum to the count but DON'T add the letter itself
                count += subcount
                subcount = 0
                wasLastCharANum = False
    return count

def findFirstBitInFormatString(inString):
    '''
    # finds if there's is an 'u' in the given string
    # if yes, split string on that letter plus any preceding numbers and return all three parts
    # otherwise return input string
    '''

    currentString = inString
    rightIndex = currentString.find('u')
    leftIndex = rightIndex
    if rightIndex != -1:
        while leftIndex > 0 and currentString[leftIndex-1].isdigit():
            leftIndex -= 1
    else:
        return ("", "", currentString)

    # splits input string into three strings:
    #   * the string prior to the split string
    #   * the split string, which contains the 'u' character along with an optional immediately preceding number
    #   * the remainder of the string
    return (currentString[:leftIndex], currentString[leftIndex:rightIndex+1], currentString[rightIndex+1:])

def calculateStringOfFormatCharacters(inBitCount):
    '''
    # determines the format string for struct.pack() based on the number of bits
    # currently only calculates single character format strings
    #TODO: Allow for multiple format characters
    # returns a string of format characters
    '''

    STRUCT_PACK_DATA_TYPES = ['B', 'H', 'I', 'L', 'Q'] # constant for all the struct.pack() format integer characters in order from smallest to largest

    # the following tests are for the three main datatypes: 1 byte, 2 byte, and 4 byte integers
    if inBitCount / 8 == 1:
        return STRUCT_PACK_DATA_TYPES[0]
    elif inBitCount / 8 == 2:
        return STRUCT_PACK_DATA_TYPES[1]
    elif inBitCount / 8 == 4:
        return STRUCT_PACK_DATA_TYPES[2]
    else:
        raise ValueError('Number of bytes from bit fields do not fit evenly into a single datatype')

def preprocessFormatToAddStrings(inString, inArgs):
    '''
    # preprocesses both the format string and arguments to change 't' characters in serializer to valid 's' characters in struct
    # replaces 't' with the proper length 's', and replaces the string args with bytes args
    # returns a tuple of the processed format string and processed args
    '''

    currentString = inString
    currentArgs = inArgs
    rightIndex = currentString.find('t') # looks for the first 't' to prime the loop
    while rightIndex != -1: # until we run out of 't's to find
        argsToSkip = countNumberOfFieldsInFormatString(currentString[:rightIndex]) # figure out how many args we need to skip to get to the right string arg
        sizeOfString = len(currentArgs[argsToSkip]) # determine the size of that string before we convert it to bytes
        currentArgs[argsToSkip] = bytes(currentArgs[argsToSkip], 'utf-8') # convert it to bytes using utf-8, the standard encoding done by chr.encode()
        currentString = currentString.replace('t', str(sizeOfString) + 's', 1) # replace the 't' we just found with an 's' with the proper length in front of it
        rightIndex = currentString.find('t') # prime the loop again
    return (currentString, currentArgs)
