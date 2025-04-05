"""
Tests for the notifications module.
"""
import os
import time
import tempfile
from unittest import TestCase, mock

from hubqueue.notifications import (
    list_notifications, mark_notification_as_read, mark_all_notifications_as_read,
    get_notification_details, subscribe_to_thread, poll_notifications
)


class TestNotifications(TestCase):
    """Test notification management functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock environment variables
        self.env_patcher = mock.patch.dict('os.environ', {}, clear=True)
        self.env_patcher.start()

    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
        
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @mock.patch("hubqueue.notifications.Github")
    def test_list_notifications(self, mock_github):
        """Test listing notifications."""
        # Mock GitHub API
        mock_subject1 = mock.MagicMock()
        mock_subject1.type = "Issue"
        mock_subject1.title = "Test Issue"
        mock_subject1.url = "https://api.github.com/repos/test-user/test-repo/issues/1"
        mock_subject1.latest_comment_url = "https://api.github.com/repos/test-user/test-repo/issues/comments/1"
        
        mock_subject2 = mock.MagicMock()
        mock_subject2.type = "PullRequest"
        mock_subject2.title = "Test Pull Request"
        mock_subject2.url = "https://api.github.com/repos/test-user/test-repo/pulls/2"
        mock_subject2.latest_comment_url = "https://api.github.com/repos/test-user/test-repo/pulls/comments/2"
        
        mock_repo = mock.MagicMock()
        mock_repo.full_name = "test-user/test-repo"
        mock_repo.html_url = "https://github.com/test-user/test-repo"
        
        mock_notification1 = mock.MagicMock()
        mock_notification1.id = "1"
        mock_notification1.unread = True
        mock_notification1.reason = "mention"
        mock_notification1.updated_at = "2023-01-01T00:00:00Z"
        mock_notification1.subject = mock_subject1
        mock_notification1.repository = mock_repo
        
        mock_notification2 = mock.MagicMock()
        mock_notification2.id = "2"
        mock_notification2.unread = False
        mock_notification2.reason = "author"
        mock_notification2.updated_at = "2023-01-02T00:00:00Z"
        mock_notification2.subject = mock_subject2
        mock_notification2.repository = mock_repo
        
        mock_user = mock.MagicMock()
        mock_user.get_notifications.return_value = [mock_notification1, mock_notification2]
        
        mock_github.return_value.get_user.return_value = mock_user
        
        # List notifications
        notifications = list_notifications(all=True, participating=False, since=None, before=None, token="test-token")
        
        # Verify result
        self.assertEqual(len(notifications), 2)
        
        self.assertEqual(notifications[0]["id"], "1")
        self.assertEqual(notifications[0]["unread"], True)
        self.assertEqual(notifications[0]["reason"], "mention")
        self.assertEqual(notifications[0]["updated_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(notifications[0]["subject"]["type"], "Issue")
        self.assertEqual(notifications[0]["subject"]["title"], "Test Issue")
        self.assertEqual(notifications[0]["subject"]["url"], "https://api.github.com/repos/test-user/test-repo/issues/1")
        self.assertEqual(notifications[0]["subject"]["latest_comment_url"], "https://api.github.com/repos/test-user/test-repo/issues/comments/1")
        self.assertEqual(notifications[0]["repository"]["name"], "test-user/test-repo")
        self.assertEqual(notifications[0]["repository"]["url"], "https://github.com/test-user/test-repo")
        
        self.assertEqual(notifications[1]["id"], "2")
        self.assertEqual(notifications[1]["unread"], False)
        self.assertEqual(notifications[1]["reason"], "author")
        self.assertEqual(notifications[1]["updated_at"], "2023-01-02T00:00:00Z")
        self.assertEqual(notifications[1]["subject"]["type"], "PullRequest")
        self.assertEqual(notifications[1]["subject"]["title"], "Test Pull Request")
        self.assertEqual(notifications[1]["subject"]["url"], "https://api.github.com/repos/test-user/test-repo/pulls/2")
        self.assertEqual(notifications[1]["subject"]["latest_comment_url"], "https://api.github.com/repos/test-user/test-repo/pulls/comments/2")
        self.assertEqual(notifications[1]["repository"]["name"], "test-user/test-repo")
        self.assertEqual(notifications[1]["repository"]["url"], "https://github.com/test-user/test-repo")
        
        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_user.assert_called_once()
        mock_user.get_notifications.assert_called_once_with(all=True, participating=False, since=None, before=None)

    @mock.patch("hubqueue.notifications.Github")
    def test_mark_notification_as_read(self, mock_github):
        """Test marking a notification as read."""
        # Mock GitHub API
        mock_notification1 = mock.MagicMock()
        mock_notification1.id = "1"
        
        mock_notification2 = mock.MagicMock()
        mock_notification2.id = "2"
        
        mock_user = mock.MagicMock()
        mock_user.get_notifications.return_value = [mock_notification1, mock_notification2]
        
        mock_github.return_value.get_user.return_value = mock_user
        
        # Mark notification as read
        result = mark_notification_as_read("1", "test-token")
        
        # Verify result
        self.assertTrue(result)
        
        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_user.assert_called_once()
        mock_user.get_notifications.assert_called_once()
        mock_notification1.mark_as_read.assert_called_once()
        mock_notification2.mark_as_read.assert_not_called()

    @mock.patch("hubqueue.notifications.Github")
    def test_mark_all_notifications_as_read(self, mock_github):
        """Test marking all notifications as read."""
        # Mock GitHub API
        mock_user = mock.MagicMock()
        
        mock_github.return_value.get_user.return_value = mock_user
        
        # Mark all notifications as read
        result = mark_all_notifications_as_read(None, "test-token")
        
        # Verify result
        self.assertTrue(result)
        
        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_user.assert_called_once()
        mock_user.mark_notifications_as_read.assert_called_once_with()

    @mock.patch("hubqueue.notifications.Github")
    def test_mark_all_notifications_as_read_for_repo(self, mock_github):
        """Test marking all notifications as read for a repository."""
        # Mock GitHub API
        mock_repo = mock.MagicMock()
        
        mock_user = mock.MagicMock()
        
        mock_github.return_value.get_user.return_value = mock_user
        mock_github.return_value.get_repo.return_value = mock_repo
        
        # Mark all notifications as read for repository
        result = mark_all_notifications_as_read("test-user/test-repo", "test-token")
        
        # Verify result
        self.assertTrue(result)
        
        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_user.assert_called_once()
        mock_github.return_value.get_repo.assert_called_once_with("test-user/test-repo")
        mock_user.mark_notifications_as_read.assert_called_once_with(repo=mock_repo)

    @mock.patch("hubqueue.notifications.Github")
    def test_get_notification_details(self, mock_github):
        """Test getting notification details."""
        # Mock GitHub API
        mock_subject = mock.MagicMock()
        mock_subject.type = "Issue"
        mock_subject.title = "Test Issue"
        mock_subject.url = "https://api.github.com/repos/test-user/test-repo/issues/1"
        mock_subject.latest_comment_url = "https://api.github.com/repos/test-user/test-repo/issues/comments/1"
        
        mock_repo = mock.MagicMock()
        mock_repo.full_name = "test-user/test-repo"
        mock_repo.html_url = "https://github.com/test-user/test-repo"
        
        mock_issue = mock.MagicMock()
        mock_issue.number = 1
        mock_issue.state = "open"
        mock_issue.title = "Test Issue"
        mock_issue.body = "This is a test issue"
        mock_issue.created_at = "2023-01-01T00:00:00Z"
        mock_issue.updated_at = "2023-01-02T00:00:00Z"
        mock_issue.closed_at = None
        mock_issue.user.login = "test-user"
        mock_issue.user.html_url = "https://github.com/test-user"
        mock_issue.labels = []
        mock_issue.comments = 0
        
        mock_repo.get_issue.return_value = mock_issue
        
        mock_subscription = mock.MagicMock()
        mock_subscription.subscribed = True
        mock_subscription.ignored = False
        mock_subscription.reason = "manual"
        
        mock_notification = mock.MagicMock()
        mock_notification.id = "1"
        mock_notification.unread = True
        mock_notification.reason = "mention"
        mock_notification.updated_at = "2023-01-02T00:00:00Z"
        mock_notification.subject = mock_subject
        mock_notification.repository = mock_repo
        mock_notification.get_thread_subscription.return_value = mock_subscription
        
        mock_user = mock.MagicMock()
        mock_user.get_notifications.return_value = [mock_notification]
        
        mock_github.return_value.get_user.return_value = mock_user
        
        # Get notification details
        notification = get_notification_details("1", "test-token")
        
        # Verify result
        self.assertEqual(notification["id"], "1")
        self.assertEqual(notification["unread"], True)
        self.assertEqual(notification["reason"], "mention")
        self.assertEqual(notification["updated_at"], "2023-01-02T00:00:00Z")
        self.assertEqual(notification["subject"]["type"], "Issue")
        self.assertEqual(notification["subject"]["title"], "Test Issue")
        self.assertEqual(notification["subject"]["url"], "https://api.github.com/repos/test-user/test-repo/issues/1")
        self.assertEqual(notification["subject"]["latest_comment_url"], "https://api.github.com/repos/test-user/test-repo/issues/comments/1")
        self.assertEqual(notification["repository"]["name"], "test-user/test-repo")
        self.assertEqual(notification["repository"]["url"], "https://github.com/test-user/test-repo")
        self.assertEqual(notification["subscription"]["subscribed"], True)
        self.assertEqual(notification["subscription"]["ignored"], False)
        self.assertEqual(notification["subscription"]["reason"], "manual")
        
        # Verify subject content
        self.assertEqual(notification["subject"]["content"]["number"], 1)
        self.assertEqual(notification["subject"]["content"]["state"], "open")
        self.assertEqual(notification["subject"]["content"]["title"], "Test Issue")
        self.assertEqual(notification["subject"]["content"]["body"], "This is a test issue")
        self.assertEqual(notification["subject"]["content"]["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(notification["subject"]["content"]["updated_at"], "2023-01-02T00:00:00Z")
        self.assertEqual(notification["subject"]["content"]["closed_at"], None)
        self.assertEqual(notification["subject"]["content"]["user"]["login"], "test-user")
        self.assertEqual(notification["subject"]["content"]["user"]["url"], "https://github.com/test-user")
        self.assertEqual(notification["subject"]["content"]["labels"], [])
        self.assertEqual(notification["subject"]["content"]["comments"], 0)
        
        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_user.assert_called_once()
        mock_user.get_notifications.assert_called_once_with(all=True)
        mock_notification.get_thread_subscription.assert_called_once()
        mock_repo.get_issue.assert_called_once_with(1)

    @mock.patch("hubqueue.notifications.Github")
    def test_subscribe_to_thread(self, mock_github):
        """Test subscribing to a notification thread."""
        # Mock GitHub API
        mock_subscription = mock.MagicMock()
        mock_subscription.subscribed = True
        mock_subscription.ignored = False
        mock_subscription.reason = "manual"
        mock_subscription.created_at = "2023-01-01T00:00:00Z"
        mock_subscription.url = "https://api.github.com/notifications/threads/1/subscription"
        
        mock_notification = mock.MagicMock()
        mock_notification.id = "1"
        mock_notification.set_thread_subscription.return_value = mock_subscription
        
        mock_user = mock.MagicMock()
        mock_user.get_notifications.return_value = [mock_notification]
        
        mock_github.return_value.get_user.return_value = mock_user
        
        # Subscribe to thread
        subscription = subscribe_to_thread("1", True, False, "test-token")
        
        # Verify result
        self.assertEqual(subscription["subscribed"], True)
        self.assertEqual(subscription["ignored"], False)
        self.assertEqual(subscription["reason"], "manual")
        self.assertEqual(subscription["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(subscription["url"], "https://api.github.com/notifications/threads/1/subscription")
        
        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_user.assert_called_once()
        mock_user.get_notifications.assert_called_once_with(all=True)
        mock_notification.set_thread_subscription.assert_called_once_with(True, False)

    @mock.patch("hubqueue.notifications.time.sleep")
    @mock.patch("hubqueue.notifications.list_notifications")
    def test_poll_notifications(self, mock_list_notifications, mock_sleep):
        """Test polling for notifications."""
        # Mock list_notifications
        mock_list_notifications.side_effect = [
            # First call - initial notifications
            [
                {
                    "id": "1",
                    "subject": {
                        "title": "Test Issue 1",
                        "type": "Issue",
                    },
                    "repository": {
                        "name": "test-user/test-repo",
                    },
                },
            ],
            # Second call - new notifications
            [
                {
                    "id": "2",
                    "subject": {
                        "title": "Test Issue 2",
                        "type": "Issue",
                    },
                    "repository": {
                        "name": "test-user/test-repo",
                    },
                },
            ],
            # Third call - KeyboardInterrupt
            KeyboardInterrupt(),
        ]
        
        # Mock callback
        mock_callback = mock.MagicMock()
        
        # Mock time.sleep to raise KeyboardInterrupt after second call
        mock_sleep.side_effect = [None, KeyboardInterrupt()]
        
        # Poll for notifications
        try:
            poll_notifications(60, mock_callback, "test-token")
        except KeyboardInterrupt:
            pass
        
        # Verify API calls
        self.assertEqual(mock_list_notifications.call_count, 2)
        mock_list_notifications.assert_any_call(token="test-token")
        
        # Verify callback calls
        mock_callback.assert_called_once()
        self.assertEqual(len(mock_callback.call_args[0][0]), 1)
        self.assertEqual(mock_callback.call_args[0][0][0]["id"], "2")
