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
| role_nfs_enabled | false | determine whether role is enabled (true) or not (false) |

## Dependencies

None.

## Example Playbook

```yaml
---
# role: ansible-role-nfs
# file: site.yml

- hosts: nfs-servers
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