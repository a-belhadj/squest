from django.utils.html import format_html
from django_tables2 import TemplateColumn, LinkColumn, CheckBoxColumn, Column

from Squest.utils.squest_table import SquestTable
from service_catalog.models import Request


class RequestTable(SquestTable):
    selection = CheckBoxColumn(accessor='pk', attrs={"th__input": {"onclick": "toggle(this)"}},
                               exclude_from_export=True)
    id = LinkColumn(verbose_name="Request")
    date_submitted = TemplateColumn(template_name='generics/custom_columns/generic_date_format.html')
    instance__quota_scope__name = LinkColumn(verbose_name="Quota scope")
    operation = LinkColumn()
    instance = LinkColumn()

    def before_render(self, request):
        if not request.user.has_perm("service_catalog.delete_instance"):
            self.columns.hide('selection')

    def render_id(self, value, record):
        return format_html(f'<a title={value} href="{record.get_absolute_url()}">{record}</a>')

    def render_instance__quota_scope__name(self, value, record):
        return format_html(f'<a title={value} href="{record.instance.quota_scope.get_absolute_url()}">{value}</a>')

    class Meta:
        model = Request
        attrs = {"id": "request_table", "class": "table squest-pagination-tables"}
        fields = ("selection", "id", "user__username", "instance__quota_scope__name", "date_submitted",
                  "instance__service", "operation", "state", "instance")

    def render_state(self, record, value):
        from service_catalog.views import map_request_state
        return format_html(f'<strong class="text-{map_request_state(value)}">{value}</strong>')

    # # For CSV export
    # def value_instance__quota_scope__name(self, record, value):
    #     return str(value)
    #
    # def value_state(self, record, value):
    #     return str(value)
    #
    # def value_id(self, value, record):
    #     return value
    # def value(self, value, record):
    #     return str(value)
