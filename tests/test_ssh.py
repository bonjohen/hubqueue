"""
Tests for the ssh module.
"""
import os
import tempfile
from unittest import TestCase, mock

from hubqueue.ssh import (
    list_ssh_keys, list_local_ssh_keys, generate_ssh_key,
    upload_ssh_key, delete_ssh_key, validate_ssh_key
)


class TestSSH(TestCase):
    """Test SSH key management functions."""

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

    @mock.patch("hubqueue.ssh.Github")
    def test_list_ssh_keys(self, mock_github):
        """Test listing SSH keys."""
        # Mock GitHub API
        mock_key1 = mock.MagicMock()
        mock_key1.id = 1
        mock_key1.title = "Test Key 1"
        mock_key1.key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."
        mock_key1.url = "https://api.github.com/user/keys/1"
        mock_key1.created_at = "2023-01-01T00:00:00Z"
        mock_key1.verified = True

        mock_key2 = mock.MagicMock()
        mock_key2.id = 2
        mock_key2.title = "Test Key 2"
        mock_key2.key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI..."
        mock_key2.url = "https://api.github.com/user/keys/2"
        mock_key2.created_at = "2023-01-02T00:00:00Z"
        mock_key2.verified = True

        mock_user = mock.MagicMock()
        mock_user.get_keys.return_value = [mock_key1, mock_key2]

        mock_github.return_value.get_user.return_value = mock_user

        # List SSH keys
        keys = list_ssh_keys("test-token")

        # Verify result
        self.assertEqual(len(keys), 2)

        self.assertEqual(keys[0]["id"], 1)
        self.assertEqual(keys[0]["title"], "Test Key 1")
        self.assertEqual(keys[0]["key"], "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...")
        self.assertEqual(keys[0]["url"], "https://api.github.com/user/keys/1")
        self.assertEqual(keys[0]["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(keys[0]["verified"], True)

        self.assertEqual(keys[1]["id"], 2)
        self.assertEqual(keys[1]["title"], "Test Key 2")
        self.assertEqual(keys[1]["key"], "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI...")
        self.assertEqual(keys[1]["url"], "https://api.github.com/user/keys/2")
        self.assertEqual(keys[1]["created_at"], "2023-01-02T00:00:00Z")
        self.assertEqual(keys[1]["verified"], True)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_user.assert_called_once()
        mock_user.get_keys.assert_called_once()

    def test_list_local_ssh_keys(self):
        """Test listing local SSH keys."""
        # Create test SSH directory
        ssh_dir = os.path.join(self.temp_dir, "ssh")
        os.makedirs(ssh_dir, exist_ok=True)

        # Create test SSH keys
        with open(os.path.join(ssh_dir, "id_rsa"), "w") as f:
            f.write("-----BEGIN OPENSSH PRIVATE KEY-----\ntest\n-----END OPENSSH PRIVATE KEY-----")

        with open(os.path.join(ssh_dir, "id_rsa.pub"), "w") as f:
            f.write("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... test@example.com")

        with open(os.path.join(ssh_dir, "id_ed25519"), "w") as f:
            f.write("-----BEGIN OPENSSH PRIVATE KEY-----\ntest\n-----END OPENSSH PRIVATE KEY-----")

        with open(os.path.join(ssh_dir, "id_ed25519.pub"), "w") as f:
            f.write("ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... test@example.com")

        # Create non-key files
        with open(os.path.join(ssh_dir, "known_hosts"), "w") as f:
            f.write("github.com ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...")

        with open(os.path.join(ssh_dir, "config"), "w") as f:
            f.write("Host github.com\n  User git\n  IdentityFile ~/.ssh/id_rsa")

        # Mock ssh-keygen command
        with mock.patch("subprocess.run") as mock_run:
            mock_result = mock.MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "2048 SHA256:abcdef123456 test@example.com (RSA)"
            mock_run.return_value = mock_result

            # List local SSH keys
            keys = list_local_ssh_keys(ssh_dir)

            # Verify result
            self.assertEqual(len(keys), 4)

            # Sort keys by file name for consistent testing
            keys.sort(key=lambda k: k["file"])

            self.assertEqual(keys[0]["file"], "id_ed25519")
            self.assertEqual(keys[0]["type"], "private")

            self.assertEqual(keys[1]["file"], "id_ed25519.pub")
            self.assertEqual(keys[1]["type"], "public")

            self.assertEqual(keys[2]["file"], "id_rsa")
            self.assertEqual(keys[2]["type"], "private")

            self.assertEqual(keys[3]["file"], "id_rsa.pub")
            self.assertEqual(keys[3]["type"], "public")

    def test_generate_ssh_key(self):
        """Test generating an SSH key."""
        # Mock subprocess.run
        with mock.patch("subprocess.run") as mock_run:
            # Set up mock for ssh-keygen command
            mock_result1 = mock.MagicMock()
            mock_result1.returncode = 0

            # Set up mock for fingerprint command
            mock_result2 = mock.MagicMock()
            mock_result2.returncode = 0
            mock_result2.stdout = "4096 SHA256:abcdef123456 test@example.com (RSA)"

            # Configure mock to return different results for different calls
            mock_run.side_effect = [mock_result1, mock_result2]

            # Mock open to read public key
            with mock.patch("builtins.open", mock.mock_open(read_data="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... test@example.com")) as mock_file:
                # Generate SSH key
                key = generate_ssh_key("id_test", None, "rsa", 4096, self.temp_dir)

                # Verify result
                self.assertEqual(key["name"], "id_test")
                self.assertEqual(key["type"], "rsa")
                self.assertEqual(key["bits"], 4096)
                self.assertEqual(key["public_key"], "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... test@example.com")
                self.assertEqual(key["private_key_file"], os.path.join(self.temp_dir, "id_test"))
                self.assertEqual(key["public_key_file"], os.path.join(self.temp_dir, "id_test.pub"))

                # Verify subprocess calls
                self.assertEqual(mock_run.call_count, 2)
                mock_run.assert_any_call(
                    ["ssh-keygen", "-t", "rsa", "-b", "4096", "-f", os.path.join(self.temp_dir, "id_test"), "-N", ""],
                    stdout=mock.ANY, stderr=mock.ANY, text=True
                )

    @mock.patch("hubqueue.ssh.Github")
    def test_upload_ssh_key(self, mock_github):
        """Test uploading an SSH key."""
        # Mock GitHub API
        mock_key = mock.MagicMock()
        mock_key.id = 1
        mock_key.title = "Test Key"
        mock_key.key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."
        mock_key.url = "https://api.github.com/user/keys/1"
        mock_key.created_at = "2023-01-01T00:00:00Z"
        mock_key.verified = True

        mock_user = mock.MagicMock()
        mock_user.create_key.return_value = mock_key

        mock_github.return_value.get_user.return_value = mock_user

        # Create test key file
        key_path = os.path.join(self.temp_dir, "id_test.pub")
        with open(key_path, "w") as f:
            f.write("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... test@example.com")

        # Upload SSH key
        key = upload_ssh_key("Test Key", key_path, None, "test-token")

        # Verify result
        self.assertEqual(key["id"], 1)
        self.assertEqual(key["title"], "Test Key")
        self.assertEqual(key["key"], "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...")
        self.assertEqual(key["url"], "https://api.github.com/user/keys/1")
        self.assertEqual(key["created_at"], "2023-01-01T00:00:00Z")
        self.assertEqual(key["verified"], True)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_user.assert_called_once()
        mock_user.create_key.assert_called_once_with("Test Key", "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... test@example.com")

    @mock.patch("hubqueue.ssh.Github")
    def test_delete_ssh_key(self, mock_github):
        """Test deleting an SSH key."""
        # Mock GitHub API
        mock_key1 = mock.MagicMock()
        mock_key1.id = 1

        mock_key2 = mock.MagicMock()
        mock_key2.id = 2

        mock_user = mock.MagicMock()
        mock_user.get_keys.return_value = [mock_key1, mock_key2]

        mock_github.return_value.get_user.return_value = mock_user

        # Delete SSH key
        result = delete_ssh_key(1, "test-token")

        # Verify result
        self.assertTrue(result)

        # Verify API calls
        mock_github.assert_called_once_with("test-token")
        mock_github.return_value.get_user.assert_called_once()
        mock_user.get_keys.assert_called_once()
        mock_key1.delete.assert_called_once()
        mock_key2.delete.assert_not_called()

    @mock.patch("subprocess.run")
    def test_validate_ssh_key_public(self, mock_run):
        """Test validating a public SSH key."""
        # Create test key file
        key_path = os.path.join(self.temp_dir, "id_test.pub")
        with open(key_path, "w") as f:
            f.write("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... test@example.com")

        # Mock subprocess.run
        mock_result = mock.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "4096 SHA256:abcdef123456 test@example.com (RSA)"
        mock_run.return_value = mock_result

        # Validate SSH key
        result = validate_ssh_key(key_path)

        # Verify result
        self.assertTrue(result["valid"])
        self.assertEqual(result["bits"], 4096)
        self.assertEqual(result["fingerprint"], "SHA256:abcdef123456")
        self.assertEqual(result["comment"], "test@example.com")
        self.assertEqual(result["type"], "RSA")

        # Verify subprocess calls
        mock_run.assert_called_once_with(
            ["ssh-keygen", "-lf", key_path],
            stdout=mock.ANY, stderr=mock.ANY, text=True
        )

    @mock.patch("subprocess.run")
    def test_validate_ssh_key_private(self, mock_run):
        """Test validating a private SSH key."""
        # Create test key file
        key_path = os.path.join(self.temp_dir, "id_test")
        with open(key_path, "w") as f:
            f.write("-----BEGIN OPENSSH PRIVATE KEY-----\ntest\n-----END OPENSSH PRIVATE KEY-----")

        # Mock subprocess.run for extracting public key
        mock_result1 = mock.MagicMock()
        mock_result1.returncode = 0
        mock_result1.stdout = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."

        # Mock subprocess.run for validating public key
        mock_result2 = mock.MagicMock()
        mock_result2.returncode = 0
        mock_result2.stdout = "4096 SHA256:abcdef123456 test@example.com (RSA)"

        mock_run.side_effect = [mock_result1, mock_result2]

        # Validate SSH key
        result = validate_ssh_key(key_path)

        # Verify result
        self.assertTrue(result["valid"])
        self.assertEqual(result["bits"], 4096)
        self.assertEqual(result["fingerprint"], "SHA256:abcdef123456")
        self.assertEqual(result["comment"], "test@example.com")
        self.assertEqual(result["type"], "RSA")

        # Verify subprocess calls
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_any_call(
            ["ssh-keygen", "-yf", key_path],
            stdout=mock.ANY, stderr=mock.ANY, text=True
        )
        # Second call is to ssh-keygen -lf with a temporary file
