from django.utils.html import format_html
from django_tables2 import TemplateColumn, tables, LinkColumn, A

from service_catalog.models import ApprovalWorkflow


class ApprovalWorkflowTable(tables.Table):
    name = LinkColumn("service_catalog:approvalworkflow_details", args=[A("id")])
    actions = TemplateColumn(template_name='generics/custom_columns/generic_actions.html', orderable=False)

    class Meta:
        model = ApprovalWorkflow
        attrs = {"id": "approval_workflow_table", "class": "table squest-pagination-tables "}
        fields = ("name", "operation", "scopes", "actions")

    def render_scopes(self, value, record):
        scopes = record.scopes.all().distinct()
        html = ""
        for scope in scopes:
            html += f"<span class=\"badge bg-primary\">{scope.name}</span>  "
        return format_html(html)
