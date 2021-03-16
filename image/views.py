from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, UpdateView, DeleteView

from image.models import Image


class ImageForm(ModelForm):
    class Meta:
        model = Image
        fields = ['image']


class UpdateImage(LoginRequiredMixin, UpdateView):
    model = Image
    template_name = "update.html"
    form_class = ImageForm
    context_object_name = "form"

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            instance = self.get_object()
            form = self.get_form()
            if form.is_valid():
                instance.image = form.cleaned_data["image"]
                instance.save()
                last_hist = instance.imagehistory_set.order_by("-created_at").first()
                return JsonResponse({
                    "new_image": last_hist.new_image.url,
                    "created_at": last_hist.created_at,
                    "old_image": last_hist.old_image.url,
                })
            return JsonResponse(form.errors, status=400)
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.path


class DeleteImage(LoginRequiredMixin, DeleteView):
    model = Image
    success_url = "/"
    template_name = "delete.html"


class ImageList(LoginRequiredMixin, ListView):
    model = Image
    template_name = "home.html"
    context_object_name = "images"

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["form"] = ImageForm()
        return context

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            form = ImageForm(request.POST, request.FILES)
            if form.is_valid():
                form.instance.user = request.user
                form.save()
                if request.is_ajax():
                    instance = form.instance
                    return JsonResponse({"image": instance.image.url, "id": instance.id})
            return JsonResponse(form.errors, status=400)
        else:
            form = ImageForm()
        return render(request, self.template_name, {"form": form, self.context_object_name: self.get_queryset()})
