from detection.Form import Form


class Generator:
    def __init__(self, form):
        self.form = form
        self.compos = form.get_detection_result()