from django.db import models
from django.db.models import ForeignKey, Sum

from Squest.utils.squest_model import SquestModel


class Quota(SquestModel):
    class Meta:
        unique_together = ('scope', 'attribute_definition')
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    scope = ForeignKey("Scope",
                       blank=False,
                       help_text="The attribute definitions linked to this quota.",
                       related_name="quotas",
                       related_query_name="quota",
                       verbose_name="Quota",
                       on_delete=models.CASCADE
                       )
    limit = models.PositiveIntegerField(default=0)
    attribute_definition = ForeignKey(
        "resource_tracker_v2.AttributeDefinition",
        blank=False,
        help_text="The attribute definitions linked to this quota.",
        related_name="quotas",
        related_query_name="quota",
        verbose_name="Quota",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.attribute_definition.name

    def get_absolute_url(self):
        return self.scope.get_absolute_url() + "#quotas"

    def get_scopes(self):
        return self.scope.get_scopes()

    @property
    def name(self):
        return self.attribute_definition.name

    @property
    def available(self):
        return self.limit - self.consumed

    @property
    def consumed(self):
        from resource_tracker_v2.models import ResourceAttribute
        # get the consumption of instances at scope level (org or team)
        consumed = ResourceAttribute.objects.filter(attribute_definition=self.attribute_definition,
                                                    resource__service_catalog_instance__quota_scope=self.scope) \
            .values("resource__service_catalog_instance__quota_scope") \
            .aggregate(consumed=Sum('value')) \
            .get("consumed", 0)
        if consumed is None:  # the previous call has returned None if there is no instance linked to the org
            consumed = 0

        # if the scope is an org, we subtract the limit of each team to the global consumption
        class_name = self.scope.get_object().__class__.__name__
        if class_name == "Organization":
            target_org = self.scope.get_object()
            team_consumed = Quota.objects.filter(scope__in=target_org.teams.all(),
                                                 attribute_definition=self.attribute_definition) \
                .aggregate(limit=Sum('limit')) \
                .get("limit", 0)
            if team_consumed is not None:
                consumed = consumed + team_consumed

        return consumed
