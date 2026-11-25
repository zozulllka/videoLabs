import subprocess
import numpy as np
from PIL import Image
import os

# Question 2)
class ColorTranslator:
    def rgb_to_yuv(self, r, g, b):
        y = round(0.299*float(r) + 0.587*float(g) + 0.114*float(b))
        u = round(-0.147*float(r) - 0.289*float(g) + 0.436*float(b))
        v = round(0.615*float(r) - 0.515*float(g) - 0.100*float(b))
        return (y, u, v)

    def yuv_to_rgb(self, y, u, v):
        r = round(float(y) + 1.140*float(v))
        g = round(float(y) - 0.395*float(u) - 0.581*float(v))
        b = round(float(y) + 2.032*float(u))
        return (r, g, b)

ct = ColorTranslator()
def test_color_translator():
    r_test = input("r value: ")
    g_test = input("g value: ")
    b_test = input("b value: ")

    y_test, u_test, v_test = ct.rgb_to_yuv(r_test, g_test, b_test)
    r_result, g_result, b_result = ct.yuv_to_rgb(y_test, u_test, v_test)

    print("initial rgb: ", r_test, g_test, b_test)
    print("yuv: ", y_test, u_test, v_test)
    print("resulting rgb: ", r_result, g_result, b_result)

"""
    after translating the values RGB -> YUV -> RGB the values are not always the same.
    sometimes it comes back +-1 off.
    this has to do with the fact that I round the values to whole numbers but
    the calculations involve multiplication with floats
"""


"""
Question 3)
    JPEG and video codec do this because the human eye is more sensetive to the change in
    brightness than in color.
"""

# Question 4)
class ImageTool:
    def __init__(self, path):
        self.path = path

    def resize(self, factor, out_path, flags=None):
        """Downscale by 1/factor using FFmpeg. flags: optional sws algorithm, e.g. 'nearest'."""
        vf = f"scale=iw/{factor}:ih/{factor}"
        if flags:
            vf += f":flags={flags}"
        cmd = ["ffmpeg", "-y", "-i", self.path, "-vf", vf, out_path]
        subprocess.run(cmd, check=True)

tool = ImageTool("input.png")
#tool.resize(2, f"q4_resized/tool_half.png")
#tool.resize(4, f"q4_resized/tool_quarter.png")
#tool.resize(8, f"q4_resized/tool_eighth.png")

"""
    ffmpeg uses bicubic by default. other algorithms I tried: neighbor, lanczos, area.
    I can barely see the difference between bicubic, lanczos and area. All of these look good.
    With neighbor the image looks more 'pixely' the lines are not smooth but it's like separate pixels are visible.
"""


# Question 5)
def zigzag(matrix):
    rows, columns = matrix.shape

    solution = [[] for i in range(rows+columns-1)]

    for i in range(rows):
        for j in range(columns):
            sum = i+j
            if(sum % 2 == 0):

                # add at beginning
                solution[sum].insert(0, matrix[i][j])
            else:

                # add at end of the list
                solution[sum].append(matrix[i][j])


    # print the solution as it as
    #for i in solution:
    #    for j in i:
    #        print(j, end=" ")
    return [int(x) for diagonal in solution for x in diagonal]

def inverse_zigzag(list, rows, columns):
    matrix = np.zeros((rows, columns), dtype=np.asarray(list).dtype)

    k = 0
    for s in range(rows + columns - 1):
        # rows i that lie on diagonal s
        i_min = max(0, s - columns + 1)
        i_max = min(s, rows - 1)
        diagonal = range(i_min, i_max + 1)

        if s % 2 == 0:
            diagonal = reversed(diagonal)

        for i in diagonal:
            matrix[i][s - i] = list[k]
            k += 1

    return matrix


matrix = np.array([ [1,  2,  3,  4,  5,  6,  7,  8],
                    [9,  10, 11, 12, 13, 14, 15, 16],
                    [17, 18, 19, 20, 21, 22, 23, 24],
                    [25, 26, 27, 28, 29, 30, 31, 32],
                    [33, 34, 35, 36, 37, 38, 39, 40],
                    [41, 42, 43, 44, 45, 46, 47, 48],
                    [49, 50, 51, 52, 53, 54, 55, 56],
                    [57, 58, 59, 60, 61, 62, 63, 64]])

#print(zigzag(matrix))

list = [1, 2, 9, 17, 10, 3, 4, 11, 18, 25, 33, 26, 19, 12, 5, 6, 13, 20, 27, 34, 41, 49, 42, 35, 28, 21, 14, 7, 8, 15, 22, 29, 36, 43, 50, 57, 58, 51, 44, 37, 30, 23, 16, 24, 31, 38, 45, 52, 59, 60, 53, 46, 39, 32, 40, 47, 54, 61, 62, 55, 48, 56, 63, 64]
#print(inverse_zigzag(list, 8, 8))

#print(inverse_zigzag(zigzag(matrix), 8, 8))


# Question 6)
# Standard JPEG luminance quantization table (quality 50)
JPEG_LUMA = np.array([
    [16, 11, 10, 16,  24,  40,  51,  61],
    [12, 12, 14, 19,  26,  58,  60,  55],
    [14, 13, 16, 24,  40,  57,  69,  56],
    [14, 17, 22, 29,  51,  87,  80,  62],
    [18, 22, 37, 56,  68, 109, 103,  77],
    [24, 35, 55, 64,  81, 104, 113,  92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103,  99],
])

class BlockCodec:
    N = 8

    def __init__(self, quality=50):
        self.set_quality(quality)
        # orthonormal DCT-II matrix: C[k, n] = a(k) * cos((2n+1) * k * pi / 2N)
        n = np.arange(self.N)
        k = n.reshape(-1, 1)
        self.C = np.cos((2*n + 1) * k * np.pi / (2*self.N))
        self.C[0] *= np.sqrt(1 / self.N)
        self.C[1:] *= np.sqrt(2 / self.N)

    def set_quality(self, quality):
        if not 1 <= quality <= 100:
            raise ValueError("quality must be in 1..100")
        self.quality = quality
        # IJG quality scaling
        scale = 5000 / quality if quality < 50 else 200 - 2*quality
        self.Q = np.clip((JPEG_LUMA * scale + 50) // 100, 1, 255)

    # 2D DCT-II and its inverse: C @ X @ C.T
    def dct(self, block):
        return self.C @ (block - 128.0) @ self.C.T      # level shift like JPEG

    def idct(self, coeffs):
        return self.C.T @ coeffs @ self.C + 128.0

    def quantize(self, coeffs):
        return np.round(coeffs / self.Q).astype(int)

    def dequantize(self, q):
        return q * self.Q

    def encode(self, block):
        return self.quantize(self.dct(block))

    def decode(self, q):
        return np.clip(np.round(self.idct(self.dequantize(q))), 0, 255)


def test_block_codec():
    # smooth gradient + a bit of noise
    np.random.seed(0)
    row, col = np.mgrid[0:8, 0:8]
    block = 100 + 8*col + 5*row + np.random.randint(-12, 13, (8, 8))

    for quality in (90, 50, 20, 5):
        codec = BlockCodec(quality)
        q = codec.encode(block)
        error = np.mean((codec.decode(q) - block) ** 2)
        print("quality", quality)
        print(q)
        print("nonzero:", np.count_nonzero(q), "/ 64, bottom-right 4x4 nonzero:", np.count_nonzero(q[4:, 4:]), "/ 16, error:", round(error, 1))
        print()

#test_block_codec()

"""
    when the quality goes down the quantization steps get bigger. The steps in the table are already
    bigger for high frequencies, so those coefficients are the first to round to 0.
    at quality 90: 5 of 28 high-freq coefficients are nonzero, at quality 50 and below: 0.
    at quality 5 only 3 of 64 coefficients are left (DC + 2 low freq) but the error (MSE) goes up from 18 to 104.
"""

# Question 7)
def rle_encode(values):
    if len(values) == 0:
        return []

    result = []
    count = 1
    for i in range(1, len(values)):
        if values[i] == values[i-1]:
            count += 1
        else:
            result.append((values[i-1], count))
            count = 1

    # save the last run
    result.append((values[-1], count))
    return result

def rle_decode(encoded):
    values = []
    for value, count in encoded:
        values.extend([value] * count)
    return values

series = [5, 0, 0, 0, 2, 2, 7, 0, 0, 0, 0, 0, 0, 0, 0]
#print(rle_encode(series))
#print(rle_decode(rle_encode(series)) == series)
# the output: [(5, 1), (0, 3), (2, 2), (7, 1), (0, 8)]


# Question 8
def mini_jpeg(gray, quality):
    h, w = gray.shape
    codec = BlockCodec(quality)
    result = np.zeros((h, w))
    symbols = 0

    for i in range(0, h, 8):
        for j in range(0, w, 8):
            block = gray[i:i+8, j:j+8]

            # encode: DCT + quantization -> zigzag -> RLE
            q = codec.encode(block)
            encoded = rle_encode(zigzag(q))
            symbols += len(encoded)

            # decode: RLE -> inverse zigzag -> dequantization + inverse DCT
            q_back = inverse_zigzag(rle_decode(encoded), 8, 8)
            result[i:i+8, j:j+8] = codec.decode(q_back)

    return result, symbols

def psnr(original, compressed):
    mse = np.mean((original - compressed) ** 2)
    return 10 * np.log10(255**2 / mse)

def test_mini_jpeg():
    gray = np.array(Image.open("input.png").convert("L"), dtype=float)
    h, w = gray.shape
    gray = gray[:h - h % 8, :w - w % 8]   # crop so the size is a multiple of 8
    Image.fromarray(gray.astype(np.uint8)).save("q8_gray.png")
    print("original (raw gray):", gray.size, "bytes")

    # my jpeg
    for quality in (90, 50, 10):
        result, symbols = mini_jpeg(gray, quality)
        Image.fromarray(result.astype(np.uint8)).save(f"q8_mine_{quality}.png")
        # each symbol = value (2 bytes) + count (1 byte)
        print(f"mine quality {quality}: {symbols} symbols, ~{symbols*3} bytes, PSNR {psnr(gray, result):.2f} dB")

test_mini_jpeg()

"""
    results:

    mine quality 90:                129000 symbols, ~387000 bytes, PSNR 46.37 dB
    mine quality 50:                78877 symbols, ~236631 bytes, PSNR 35.16 dB
    mine quality 10:                42890 symbols, ~128670 bytes, PSNR 27.90 dB

    file size of ffmpeg image:      wc -c q8_ffmeg_31.jpg
    PSNR:                           ffmpeg -i q8_ffmeg_31.jpg -i q8_gray.png -lavfi psnr -f null -

    ffmpeg q:v 2:                   95430 bytes, PSNR 47.73 dB
    ffmpeg q:v 10:                  48004 bytes, PSNR 35.23 dB
    ffmpeg q:v 31:                  26351 bytes, PSNR 28.41 dB

    ffmpeg is smaller at the same PSNR because it uses huffman coding on the coefficients,
    I only use RLE and store every symbol with a fixed size.
"""
