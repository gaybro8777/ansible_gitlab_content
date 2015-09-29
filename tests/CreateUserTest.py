# -*- coding: utf-8 -*-

import unittest
import mock
import library.gitlab_user


class CreateUserTest(unittest.TestCase):

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifNoneExists_sendCreateRequest(self, send_request_mock):
        send_request_mock.side_effect = (
            ({'status': '200 OK'}, '[{"username":"someuser"}]'),
            ({'status': '201 Created'}, '{"username":"testusername","id":12}')
        )
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'password': '98765btzf',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            False
        )
        self.assertTrue(result)
        self.assertEquals(2, send_request_mock.call_count)
        self.assert_get_users_request(send_request_mock)
        self.assert_create_user_request(send_request_mock)

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifNoneExistsAndCheckMode_dontSendRequest(self, send_request_mock):
        send_request_mock.return_value = {'status': '200 OK'}, '[{"username":"someuser"}]'
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'password': '98765btzf',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            True
        )
        self.assertTrue(result)
        self.assertEquals(1, send_request_mock.call_count)

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifNoneExistsAndSshKeyGiven_sendCreateUserAndAddSshKeyRequests(self, send_request_mock):
        send_request_mock.side_effect = (
            ({'status': '200 OK'}, '[{"username":"someuser"}]'),
            ({'status': '201 Created'}, '{"username":"testusername","id":12}'),
            ({'status': '201 Created'}, '{"id":1,"key":"ghkjfasdkjadh","title":"sometitle"}')
        )
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'password': '98765btzf',
                'ssh_key_title': 'sometitle',
                'ssh_key': 'ghkjfasdkjadh',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            False
        )
        self.assertTrue(result)
        self.assertEquals(3, send_request_mock.call_count)
        self.assert_get_users_request(send_request_mock)

        self.assert_create_user_request(send_request_mock)

        self.assertEquals('http://something.com/api/v3/users/12/keys', send_request_mock.call_args_list[2][0][1])
        self.assertEquals(
            {'PRIVATE-TOKEN': 'abc123', 'Content-Type': 'application/json'},
            send_request_mock.call_args_list[2][0][2]
        )
        self.assertEquals('POST', send_request_mock.call_args_list[2][0][0])
        self.assertEquals(
            '{"id": 12, "key": "ghkjfasdkjadh", "title": "sometitle"}',
            send_request_mock.call_args_list[2][0][3]
        )

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifNoneExistsAndSshKeyGivenAndCheckMode_dontSendCreateRequests(
            self,
            send_request_mock):

        send_request_mock.return_value = {'status': '200 OK'}, '[{"username":"someuser"}]'
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'password': '98765btzf',
                'ssh_key_title': 'sometitle',
                'ssh_key': 'ghkjfasdkjadh',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            True
        )
        self.assertTrue(result)
        self.assertEquals(1, send_request_mock.call_count)
        self.assert_get_users_request(send_request_mock)

    def assert_get_users_request(self, send_request_mock):
        self.assertEquals('http://something.com/api/v3/users', send_request_mock.call_args_list[0][1]['url'])
        self.assertEquals(
            {'PRIVATE-TOKEN': 'abc123'},
            send_request_mock.call_args_list[0][1]['headers']
        )
        self.assertEquals('GET', send_request_mock.call_args_list[0][1]['method'])

    def assert_create_user_request(self, send_request_mock):
        self.assertEquals('http://something.com/api/v3/users', send_request_mock.call_args_list[1][0][1])
        self.assertEquals(
            {'PRIVATE-TOKEN': 'abc123', 'Content-Type': 'application/json'},
            send_request_mock.call_args_list[1][0][2]
        )
        self.assertEquals('POST', send_request_mock.call_args_list[1][0][0])
        self.assertEquals(
            '{"username": "testusername", "password": "98765btzf", "email": "someone@something.com", "name": "Test"}',
            send_request_mock.call_args_list[1][0][3]
        )