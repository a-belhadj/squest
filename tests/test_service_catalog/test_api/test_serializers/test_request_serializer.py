from service_catalog.models import Instance, Request
from service_catalog.api.serializers import RequestSerializer, AdminRequestSerializer
from tests.test_service_catalog.base_test_request import BaseTestRequestAPI


class TestRequestSerializer(BaseTestRequestAPI):

    def setUp(self):
        super(TestRequestSerializer, self).setUp()
        self.local_test_instance = Instance.objects.create(name="test_instance_1",
                                                           service=self.service_test,
                                                           requester=self.standard_user,
                                                           quota_scope=self.test_quota_scope_org)

        # add a first request
        self.local_test_request = Request.objects.create(fill_in_survey={},
                                                         instance=self.local_test_instance,
                                                         operation=self.create_operation_test,
                                                         user=self.standard_user)

    def test_contains_expected_fields(self):
        serializer = AdminRequestSerializer(instance=self.local_test_request)
        self.assertEqual(set(serializer.data.keys()),
                         {'id', 'fill_in_survey', 'admin_fill_in_survey', 'date_submitted', 'date_complete',
                          'date_archived', 'instance', 'operation', 'state', 'tower_job_id', 'user',
                          'processed_by', 'accepted_by', 'approval_workflow_state', 'last_updated', 'created'})

    def test_request_serializer_field_content(self):
        serializer = RequestSerializer(instance=self.local_test_request)
        self.assertEqual(serializer.data['id'], self.local_test_request.id)
        self.assertEqual(serializer.data['operation'], self.local_test_request.operation.id)
        self.assertEqual(serializer.data['state'], self.local_test_request.state)

        # instance object
        self.assertEqual(serializer.data['instance']['id'],
                         self.local_test_request.instance.id)
        self.assertEqual(serializer.data['instance']['name'],
                         self.local_test_request.instance.name)
        self.assertEqual(serializer.data['instance']['service'],
                         self.local_test_request.instance.service.id)
        self.assertEqual(serializer.data['instance']['quota_scope']['id'],
                         self.local_test_request.instance.quota_scope.id)
        self.assertEqual(serializer.data['instance']['quota_scope']['name'],
                         self.local_test_request.instance.quota_scope.name)

        # user object
        self.assertEqual(serializer.data['user']['id'],
                         self.local_test_request.user.id)
        self.assertEqual(serializer.data['user']['email'],
                         self.local_test_request.user.email)
        self.assertEqual(serializer.data['user']['username'],
                         self.local_test_request.user.username)
        self.assertEqual(serializer.data['user']['is_superuser'],
                         self.local_test_request.user.is_superuser)
        self.assertEqual(serializer.data['user']['is_staff'],
                         self.local_test_request.user.is_staff)
        self.assertEqual(serializer.data['user']['profile']['request_notification_enabled'],
                         self.local_test_request.user.profile.request_notification_enabled)
