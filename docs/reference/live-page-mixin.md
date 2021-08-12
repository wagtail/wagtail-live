# Live Page Mixin

::: wagtail_live.models.LivePageMixin
    rendering:
      show_root_heading: true
      show_signature_annotations: true
      show_if_no_docstring: false
    selection:
      filters: ["!^_[^_]", "!get_next_by_last_updated_at", "!get_previous_by_last_updated_at"]
