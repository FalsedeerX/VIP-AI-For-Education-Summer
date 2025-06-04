## DESC: Echo Server for Mimicking AI Model Query
## Coded by Falsedeer (Yu-Kuang Chen)
## CopyRight (C) All Rights Reserved

def hexdump(string, step):
    result = []
    for x in range(0, len(string), step):
        offset = '%08x' % x  # offset for indexing
        buffer = []  # a list to store hex code
        for y in string[x: x + step]:
            code = '%02x' % y
            buffer.append(code)  # store the first line of hex code to list
        hexcode = ''.join(buffer)
        buffer.clear()

        for z in range(0, len(hexcode), 4):  # 2 hexcode in a group
            groupcode = hexcode[z: z + 4]
            buffer.append(groupcode)
        hexcode = ' '.join(buffer)  # join each group and split with space

        normal_len = step*2.5 - 1
        if len(hexcode) != normal_len:
            patch = normal_len - len(hexcode)
            for i in range(0, int(patch), 1):
                hexcode = hexcode + ' '  # fill the space in hexcode with space
        else:
            pass

        text = string[x: x + step].decode('utf-8')

        output = offset + ' | ' + hexcode + ' | ' + text  # make a nice format
        result.append(output)  # store each line to list

    output = '\n'.join(result)
    return output


# testing
if __name__ == '__main__':
    print("[#]Modele executed locally")
    print(hexdump(b'can you read me ?', 8))
