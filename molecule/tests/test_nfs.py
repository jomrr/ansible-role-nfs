import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_system_info(host):
    cmd = host.run('umount /mnt; mount -t nfs 127.0.0.1:/srv/nfs_export1 /mnt')
    assert cmd.rc == 0
