from service_catalog.models import InstanceState
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.permission_endpoint import TestingGetContextView, TestingPostContextView, TestPermissionEndpoint


class TestServiceCatalogInstancePermissionsStateMachineViews(BaseTestRequest, TestPermissionEndpoint):
    def setUp(self):
        super().setUp()
        self.test_instance.state = InstanceState.DELETED
        self.test_instance.save()

    def test_state_machine_views(self):
        testing_view_list = [
            TestingGetContextView(
                url='service_catalog:instance_archive',
                perm_str='service_catalog.archive_instance',
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingPostContextView(
                url='service_catalog:instance_archive',
                perm_str='service_catalog.archive_instance',
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingGetContextView(
                url='service_catalog:instance_unarchive',
                perm_str='service_catalog.unarchive_instance',
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingPostContextView(
                url='service_catalog:instance_unarchive',
                perm_str='service_catalog.unarchive_instance',
                url_kwargs={'pk': self.test_instance.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)
