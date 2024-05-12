from pathlib import Path
from icoextract import IconExtractor, IconExtractorError


HERE = Path(__file__).parent
OUT_DIR = HERE.parent / 'extracted'


def extract_ico_set(exe_path, sizes=None):

    try:
        extractor = IconExtractor(exe_path)
        ename = Path(exe_path).name
        icons = extractor.list_group_icons()
        for i, (name, offset) in enumerate(icons):
            print(i, name, offset)
            out_path = OUT_DIR / f"{ename}_{i}.ico"
            # Export the first group icon to a .ico file
            extractor.export_icon(out_path, num=i)
        # # Or save the .ico to a buffer, to pass it into another library
        # data = extractor.get_icon(num=0)

        # from PIL import Image
        # im = Image.open(data)
        # # ... manipulate a copy of the icon directly
    except IconExtractorError:
        # No icons available, or the resource is malformed
        pass


import win32ui
import win32gui
import win32con
import win32api
from PIL import Image


def extract_icon(exe_path, output_path=None, out_width=256, out_height=256):

    """Given an icon path (exe file) extract it and output at the desired width/height as a png image.

    Args:
        exe_path (string): path to the exe to extract the icon from
        output_name (string): name of the icon so we can save it out with the correct name
        icon_out_path (string): final destination (FOLDER) - Gets combined with output_name for full icon_path
        out_width (int, optional): desired icon width
        out_height (int, optional): desired icon height

    Returns:
        string: path to the final icon
    """

    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
    ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)

    large, small = win32gui.ExtractIconEx(exe_path.as_posix(), 0)
    win32gui.DestroyIcon(small[0])

    hdc = win32ui.CreateDCFromHandle( win32gui.GetDC(0) )
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
    hdc = hdc.CreateCompatibleDC()

    hdc.SelectObject( hbmp )
    hdc.DrawIcon( (0,0), large[0] )

    bmpstr = hbmp.GetBitmapBits(True)
    icon = Image.frombuffer('RGBA', (32,32),
        bmpstr, 'raw', 'BGRA', 0, 1
    )

    output_name = exe_path.stem
    full_outpath = Path(output_path or OUT_DIR) / "{}.png".format(output_name)
    # full_outpath = os.path.join(icon_out_path, "{}.png".format(output_name))
    icon.resize((out_width, out_height))
    icon.save(full_outpath.as_posix())
    #return the final path to the image
    return full_outpath

