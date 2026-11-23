import subprocess

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

# after translating the values RGB -> YUV -> RGB the values are not always the same. 
# sometimes it comes back +-1 off.
# this has to do with the fact that I round the values to whole numbers but 
# the calculations involve multiplication with floats


# Question 3)
# JPEG and video codec do this because the human eye is more sensetive to the change in 
# brightness than in color.


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
tool.resize(2, f"q4_resized/tool_half.png")
tool.resize(4, f"q4_resized/tool_quarter.png")
tool.resize(8, f"q4_resized/tool_eighth.png")

# ffmpeg uses bicubic by default. other algorithms I tried: neighbor, lanczos, area. 
# I can barely see the difference between bicubic, lanczos and area. All of these look good.
# With neighbor the image looks more 'pixely' the lines are not smooth but it's like separate pixels are visible.