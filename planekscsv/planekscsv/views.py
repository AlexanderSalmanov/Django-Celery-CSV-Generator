from django.views import generic

class HelloPage(generic.TemplateView):
    template_name = 'hello.html'
