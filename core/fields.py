from ckeditor.fields import RichTextField

class RichTextSimpleField(RichTextField):
    def __init__(self, *args, **kwargs):
        kwargs["config_name"] = "basic"
        super().__init__(*args, **kwargs)