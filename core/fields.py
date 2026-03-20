from django_ckeditor_5.fields import CKEditor5Field

class RichTextMediumField(CKEditor5Field):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("config_name", "medium")
        super().__init__(*args, **kwargs)