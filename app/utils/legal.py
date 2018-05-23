ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png', 'bmp', 'tiff'}


def allowed_upload_filename(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
