"""Run the native Ansible input gate against temporary paths, without privilege."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

IDENTITY = Path(__file__).resolve().parents[1]
ANSIBLE = Path(sys.executable).parent / 'ansible-playbook'


@unittest.skipUnless(ANSIBLE.is_file(), 'Use the platform Ansible virtual environment')
class PrivateInputGate(unittest.TestCase):
    def run_prepare(self, root, enabled):
        playbook = root / 'check.yaml'
        playbook.write_text(yaml.safe_dump([{
            'hosts': 'localhost', 'connection': 'local', 'gather_facts': False,
            'vars': {
                'ansible_python_interpreter': sys.executable,
                'application_name': 'knowbench',
                'services_config_dir': str(root / 'primary'),
                'services_backup_dir': str(root / 'backup'),
                'cfg': {'public_signup': {'enabled': enabled, 'smtp_host': 'smtpdm.aliyun.com',
                                          'smtp_port': 465, 'smtp_username': 'noreply@notify.sunmoonai.com'}},
            },
            'tasks': [{'ansible.builtin.import_tasks': str(IDENTITY / 'signup-prepare.yaml')}],
        }]))
        env = dict(os.environ, ANSIBLE_LOCAL_TEMP=str(root / 'ansible'), ANSIBLE_NOCOLOR='1')
        return subprocess.run([str(ANSIBLE), '-i', 'localhost,', str(playbook)],
                              capture_output=True, text=True, env=env, timeout=40)

    def test_disabled_needs_no_password_or_private_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.run_prepare(root, False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((root / 'primary').exists())
            self.assertFalse((root / 'backup').exists())

    def test_enabled_without_password_stops_without_generating_one(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.run_prepare(root, True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Stop if neither copy', result.stdout)
            self.assertFalse((root / 'primary').exists())
            self.assertFalse((root / 'backup').exists())

    def test_symlink_password_is_rejected_without_disclosure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'primary').mkdir()
            target = root / 'operator-input'
            marker = 'SYNTHETIC-DO-NOT-LOG-INPUT'
            target.write_text(marker)
            (root / 'primary/casdoor-smtp-password').symlink_to(target)
            result = self.run_prepare(root, True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Require root-only regular', result.stdout)
            self.assertNotIn(marker, result.stdout + result.stderr)
            self.assertFalse((root / 'backup').exists())


if __name__ == '__main__':
    unittest.main()
