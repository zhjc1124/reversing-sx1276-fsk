import numpy as np
def LSRF(num):
    s = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    result = []
    for i in range(num):
        result.append(s[0]) 
        s[9] = s[0] ^ s[5] 
        s = np.roll(s, -1)
    return np.array(result, dtype=np.int)

size = 8*18
lsrf = LSRF(size)
for i in range(size/8):
    print(lsrf[i*8:(i+1)*8])