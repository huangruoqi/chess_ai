def load_inputs(file):
    inputs = []
    with open(file, 'rb') as f:
        content = bytearray(f.read())
        row = [0]*(64*7)
        count = 0
        for byte in content:
            for j in range(7, -1, -1):
                x = byte & 1
                byte >>= 1
                if x == 1:
                    row[8 * count + j] = 1
            count += 1
            if count == 64*7//8:
                inputs.append(row)
                row = [0]*(64*7)
                count = 0
    return inputs
