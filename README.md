# ansible-role-nfs

Ansible role for setting up nfs.

## Supported Platforms

* Ubuntu 18.04

## Requirements

Ansible 2.7 or higher is recommended.

## Variables

Variables for this

| variable | default value in defaults/main.yml | description |
| -------- | ---------------------------------- | ----------- |
| role_nfs_enabled | False | determine whether role is enabled (True) or not (False) |
| nfs_client | False | Install and configure NFS Client |
| nfs_server | False | Install and configure NFS Server |
| nfs_exports | {} | Exports for NFS Server, see example below table |
| nfs_rpcbind_enabled | no | Enable RPC Bind |

```yaml
---
# nfs_exports example
nfs_exports:
    '/srv/nfs_export1':
        owner: root
        group: root
        mode: '0750'
        hosts:
            127.0.0.1:
                - rw
                - async
                - no_subtree_check
                - secure
```

## Dependencies

None.

## Example Playbook

```yaml
---
# role: ansible-role-nfs
# file: site.yml

- hosts: nfs_servers
  roles:
    - role: ansible-role-nfs
```

## License and Author

- Author:: Jonas Mauer (<jam@kabelmail.net>)
- Copyright:: 2019, Jonas Mauer

Licensed under MIT License;
See LICENSE file in repository.

## References

[ArchWiki](https://wiki.archlinux.org/)
