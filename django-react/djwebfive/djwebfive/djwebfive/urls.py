from django import http
from django import forms
from django.utils import simplejson as json
from django.conf.urls import patterns, url
from django.views.generic import TemplateView, FormView
from django.views.decorators.csrf import csrf_exempt

## Putting forms and views in urls. Don't do that at home, please.


class ContactForm(forms.Form):
    author = forms.CharField()
    text = forms.CharField(widget=forms.Textarea)


class CommentView(FormView):
    form_class = ContactForm
    template_name = ''
    response_class = http.HttpResponse
    # JSON data is set as a class attr to simplify
    data = [{'author': 'Pete Hunt', 'text': 'Hey there!'}]

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(
            self.convert_context_to_json(context),
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        return json.dumps(context)

    def get_context_data(self, **kwargs):
        return self.data

    def form_valid(self, form):
        self.data.append(form.cleaned_data)
        return self.render_to_response(self.get_context_data())


urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='base.html')),
    url(r'^comments/$', csrf_exempt(CommentView.as_view())),
)
