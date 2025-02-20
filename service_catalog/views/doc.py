from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from Squest.utils.squest_views import SquestListView
from service_catalog.filters.doc_filter import DocFilter
from service_catalog.models import Doc
from service_catalog.tables.doc_tables import DocTable


class DocListView(SquestListView):
    table_class = DocTable
    model = Doc
    filterset_class = DocFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['html_button_path'] = ""
        context['extra_html_button_path'] = "service_catalog/buttons/manage_docs.html"
        return context


@login_required
def doc_details(request, pk):
    doc = get_object_or_404(Doc, id=pk)
    if not request.user.has_perm('service_catalog.view_doc', doc):
        raise PermissionDenied
    breadcrumbs = [
        {'text': 'Documentations', 'url': reverse('service_catalog:doc_list')},
        {'text': doc.title, 'url': ""}
    ]
    context = {
        "doc": doc,
        "breadcrumbs": breadcrumbs
    }
    return render(request,
                  'service_catalog/common/documentation/doc-show.html', context)
