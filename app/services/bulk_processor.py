




from app.models.image_source import ImageSource


class BulkProcessor:


    def __init__(self, image_source: ImageSource, per_frame_func, process_function) -> None:
        self.source_info = image_source.info


    def start_processing(self):
        ...
