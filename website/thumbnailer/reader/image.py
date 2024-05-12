from PIL import Image
from resizeimage import resizeimage

RW_SUPPORTED = (
    'blp',
    'bmp',
    'dds',
    'dib',
    'eps',
    'gif',
    'icns',
    'ico',
    'im',
    'jpeg',
    'jpeg-2000',
    'msp',
    'pcx',
    'pfm',
    'id9',
    'png',
    'apng-sequences',
    'ppm',
    'sgi',
    'spider',
    'tga',
    'tiff',
    'webp',
    'xbm'
)

R_SUPPORTED = (
    'cur',
    'dcx',
    'fits',
    'fli-flc',
    'fpx',
    'ftex',
    'gbr',
    'gd',
    'imt',
    'iptc-naa',
    'mcidas',
    'mic',
    'mpo',
    'pcd',
    'pixar',
    'psd',
    'qoi',
    'sun',
    'wal',
    'wmf-emf',
    'xpm',
)


def is_supported(path):
    ext = Path(path).suffix[1:]
    return is_ext_supported(ext)


def is_ext_supported(ext):
    return ext in (RW_SUPPORTED + R_SUPPORTED)


def resize_file(path):
    """Given a path, return a thumbnail filepath.
    """

    outpath = Path(settings.THUMBNAIL_ROOT) / f"thumb_{path.name}"
    url = Path(settings.MEDIA_URL) / 'thumbnails' / f"thumb_{path.name}"
    if outpath.exists():
        return url

    with Image.open(path) as stream:
        stream = resizeimage.resize_width(stream, 200)
        stream.save(outpath, stream.format)
        # fd_img.close()
    return url
