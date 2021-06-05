from django import forms
from django.views.generic import FormView
from .receivers import DebugMessageReceiver


class DebugForm(forms.Form):
    channel = forms.CharField()
    message_id = forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea)

    def save(self):
        receiver = DebugMessageReceiver(**self.cleaned_data)
        receiver.process()


class DebugView(FormView):
    form_class = DebugForm
    template_name = "wagtail_live/debug_view.html"
    success_url = "/debug/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
