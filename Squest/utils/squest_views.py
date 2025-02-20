import traceback
from time import strftime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import ProtectedError
from django.urls import reverse_lazy, NoReverseMatch, reverse
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django_tables2.export import ExportMixin

from Squest.utils.squest_rbac import SquestPermissionRequiredMixin


class SquestPermissionDenied(PermissionDenied):
    def __init__(self, permission, *args, **kwargs):
        self.permission = permission
        super().__init__(mark_safe(f"Permission <b>{permission}</b> required"))


class SquestView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.django_content_type = ContentType.objects.get_by_natural_key(app_label=self.model._meta.app_label,
                                                                          model=self.model._meta.model_name)

    def get_generic_url_kwargs(self):
        return {}

    def get_generic_url(self, action):
        try:
            return reverse_lazy(f'{self.app_label}:{self.django_content_type.model}_{action}',
                                kwargs=self.get_generic_url_kwargs())
        except AttributeError:
            try:
                return reverse(f'{self.django_content_type.app_label}:{self.django_content_type.model}_{action}',
                                    kwargs=self.get_generic_url_kwargs())
            except NoReverseMatch:
                return '#'


class SquestExportMixin(ExportMixin):
    export_formats = ("csv",)
    export_csv = False

    def get_export_filename(self, export_format):
        return f'{self.django_content_type.model}{strftime("%Y-%m-%d-%Hh%M")}.{export_format}'


class SquestListView(LoginRequiredMixin, SquestPermissionRequiredMixin, SquestExportMixin, SingleTableMixin, SquestView,
                     FilterView):
    table_pagination = {'per_page': 10}
    template_name = 'generics/list.html'
    no_data_message = "There is no data to show or you don't have required permission"
    ordering = None

    def get_permission_required(self):
        return f"{self.django_content_type.app_label}.list_{self.django_content_type.model}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.django_content_type.name.capitalize()
        context['no_data_message'] = self.no_data_message
        context['html_button_path'] = "generics/buttons/add_button.html"
        context['add_url'] = self.get_generic_url("create")
        context['django_content_type'] = self.django_content_type
        context['export_csv'] = self.export_csv

        return context

    def get_queryset(self):
        try:
            qs = self.model.get_queryset_for_user(
                self.request.user,
                f"{self.django_content_type.app_label}.view_{self.django_content_type.model}"
            )
        except AttributeError as e:
            traceback.print_exc()
            qs = self.model.objects.all()
        if self.ordering is not None:
            qs = qs.order_by(self.ordering)
        return qs


class SquestCreateView(LoginRequiredMixin, SquestPermissionRequiredMixin, SquestView, CreateView):
    template_name = 'generics/generic_form.html'

    def get_permission_required(self):
        return f"{self.django_content_type.app_label}.add_{self.django_content_type.model}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {
                'text': self.django_content_type.name.capitalize(),
                'url': self.get_generic_url('list')
            },
            {
                'text': f'New {self.django_content_type.name}',
                'url': ""
            },
        ]
        context['action'] = "create"
        return context


class SquestUpdateView(LoginRequiredMixin, SquestPermissionRequiredMixin, SquestView, UpdateView):
    template_name = 'generics/generic_form.html'
    context_object_name = "object"

    def get_permission_required(self):
        return f"{self.django_content_type.app_label}.change_{self.django_content_type.model}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            object_url = self.object.get_absolute_url()
        except AttributeError:
            object_url = ""
        context['breadcrumbs'] = [
            {
                'text': self.django_content_type.name.capitalize(),
                'url': self.get_generic_url('list')
            },
            {
                'text': self.object,
                'url': object_url
            },
            {
                'text': 'Edit',
                'url': ""
            },
        ]
        context['action'] = "edit"
        return context


class SquestDeleteView(LoginRequiredMixin, SquestPermissionRequiredMixin, SquestView, DeleteView):
    template_name = 'generics/confirm-delete-template.html'
    context_object_name = "object"

    def get_permission_required(self):
        return f"{self.django_content_type.app_label}.delete_{self.django_content_type.model}"

    def get_success_url(self):
        return self.get_generic_url('list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            object_url = self.object.get_absolute_url()
        except AttributeError:
            object_url = ""
        context['breadcrumbs'] = [
            {
                'text': self.django_content_type.name.capitalize(),
                'url': self.get_generic_url('list')
            },
            {
                'text': self.object,
                'url': object_url
            },
            {
                'text': 'Delete',
                'url': ""
            },
        ]
        context['details'] = {
            'warning_sentence': 'Following objects will be deleted or impacted:',
            'details_list': self.object.get_related_objects_cascade()
        }
        context['confirm_text'] = mark_safe(f"Confirm deletion of <strong>{self.object}</strong>?")
        context['action_url'] = self.get_generic_url("delete")
        context['button_text'] = 'Delete'
        return context

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            error_message = f"Cannot delete {self.object} because it is referenced in protected relationship with the following objects:"
            context = self.get_context_data(object=self.object, error_message=error_message,
                                            protected_objects=e.protected_objects)
            return self.render_to_response(context)


class SquestDetailView(LoginRequiredMixin, SquestPermissionRequiredMixin, SquestView, DetailView):
    # Django will add "request" (resp "instance") in context when using SquestDetailView on Request (resp Instance)
    # It cause conflicts with request object
    context_object_name = "object"

    def get_permission_required(self):
        if self.permission_required is not None:
            return self.permission_required
        return f"{self.django_content_type.app_label}.view_{self.django_content_type.model}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {
                'text': self.django_content_type.name.capitalize(),
                'url': self.get_generic_url('list')
            },
            {
                'text': str(self.get_object()),
                'url': ""
            },
        ]
        return context


class SquestFormView(LoginRequiredMixin, SquestPermissionRequiredMixin, SingleObjectMixin, SquestView, FormView):
    template_name = 'generics/generic_form.html'
    context_object_name = "object"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_permission_required(self):
        return f"{self.django_content_type.app_label}.change_{self.django_content_type.model}"

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {
                'text': self.django_content_type.name.capitalize(),
                'url': self.get_generic_url('list')
            },
            {
                'text': self.object,
                'url': self.object.get_absolute_url()
            },
            {
                'text': "New",
                'url': ""
            },
        ]
        context['action'] = "edit"
        return context
