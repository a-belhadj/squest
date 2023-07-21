from django.utils.encoding import force_str
from django_tables2 import tables
from django_tables2.utils import A
class SquestTable(tables.Table):

    def __init__(self, *args, **kwargs):
        hide_field = list()
        if 'hide_fields' in kwargs:
            hide_field = kwargs.pop("hide_fields")
        super(SquestTable, self).__init__(*args, **kwargs)

        for field in hide_field:
            self.columns.hide(field)

    #
    # def as_values(self, exclude_columns=None):
    #     """
    #     Return a row iterator of the data which would be shown in the table where
    #     the first row is the table headers.
    #
    #     arguments:
    #         exclude_columns (iterable): columns to exclude in the data iterator.
    #
    #     This can be used to output the table data as CSV, excel, for example using the
    #     `~.export.ExportMixin`.
    #
    #     If a column is defined using a :ref:`table.render_FOO`, the returned value from
    #     that method is used. If you want to differentiate between the rendered cell
    #     and a value, use a `value_Foo`-method::
    #
    #         class Table(tables.Table):
    #             name = tables.Column()
    #
    #             def render_name(self, value):
    #                 return format_html('<span class="name">{}</span>', value)
    #
    #             def value_name(self, value):
    #                 return value
    #
    #     will have a value wrapped in `<span>` in the rendered HTML, and just returns
    #     the value when `as_values()` is called.
    #
    #     Note that any invisible columns will be part of the row iterator.
    #     """
    #     if exclude_columns is None:
    #         exclude_columns = ()
    #
    #     columns = [
    #         column
    #         for column in self.columns.iterall()
    #         if not (column.column.exclude_from_export or column.name in exclude_columns)
    #     ]
    #
    #     yield [force_str(column.header, strings_only=True) for column in columns]
    #     for row in self.rows:
    #         for column in columns:
    #             force_str(str(A(row.table.columns[column.name].accessor).penultimate(row.record)[0]), strings_only=True)
    #
    #
    #     for row in self.rows:
    #         yield [
    #             force_str(A(row.table.columns[column.name].accessor).penultimate(row.record)[0], strings_only=True) for column in columns
    #         ]
