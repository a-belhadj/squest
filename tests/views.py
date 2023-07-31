from django.test import TestCase

from django.contrib.auth.models import User
from profiles.models.squest_permission import Permission
from django.urls import reverse, NoReverseMatch

from profiles.models import GlobalPermission, Role


class TestingUIViews:
    expected_status_code = None
    expected_not_allowed_status_code = 403

    def __init__(self, url, perm_str, url_kwargs=None, data=None, expected_status_code=None,
                 expected_not_allowed_status_code=None):
        if expected_not_allowed_status_code is not None:
            self.expected_not_allowed_status_code = expected_not_allowed_status_code
        if expected_status_code is not None:
            self.expected_status_code = expected_status_code
        try:
            self.url = reverse(url, kwargs=url_kwargs)
        except NoReverseMatch:
            raise NoReverseMatch(f'url: {url}, kwargs: {url_kwargs}')
        self.data = {} if data is None else data
        try:
            self.permission = Permission.objects.get(content_type__app_label=perm_str.split('.')[0],
                                                     codename=perm_str.split('.')[1])
        except Permission.DoesNotExist:
            raise Permission.DoesNotExist(f'Permission {perm_str} does not exist.')
        except Permission.MultipleObjectsReturned:
            raise Permission.MultipleObjectsReturned(
                Permission.objects.filter(content_type__app_label=perm_str.split('.')[0],
                                          codename=perm_str.split('.')[1]))

    def __str__(self):
        return f"{str(self.__class__)} - {self.url} - {self.permission}"

    def call_url(self, client):
        raise NotImplemented


class TestingGetUIViews(TestingUIViews):
    expected_status_code = 200

    def call_url(self, client):
        return client.get(self.url, self.data)


class TestingPostUIViews(TestingUIViews):
    expected_status_code = 302

    def call_url(self, client):
        return client.post(self.url, self.data)


class TestPermissionUIViews(TestCase):
    def setUp(self):
        super().setUp()
        self.global_permission = GlobalPermission.load()
        self.global_permission.user_permissions.clear()
        self.testing_user = User.objects.create_user('testing_view_user', 'testing_view_user@hpe.com', "password")
        self.empty_role = Role.objects.create(name='empty', description='empty for testing')
        self.global_permission.add_user_in_role(self.testing_user, self.empty_role)
        self.client.force_login(self.testing_user)

    def run_permissions_tests(self, testing_list):
        for test_context in testing_list:
            test_context: TestingUIViews = test_context
            response = test_context.call_url(self.client)
            self.assertEqual(test_context.expected_not_allowed_status_code, response.status_code,
                             f"{test_context}: expected: {test_context.expected_not_allowed_status_code}, got: {response.status_code}")
            self.empty_role.permissions.add(test_context.permission)
            response = test_context.call_url(self.client)
            self.assertEqual(test_context.expected_status_code, response.status_code,
                             f"{test_context}: expected: {test_context.expected_status_code}, got: {response.status_code}")
            self.empty_role.permissions.clear()
