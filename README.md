# Ansible Role: nfs

![GitHub](https://img.shields.io/github/license/jomrr/ansible-role-nfs)
![GitHub last commit](https://img.shields.io/github/last-commit/jomrr/ansible-role-nfs)
![GitHub issues](https://img.shields.io/github/issues-raw/jomrr/ansible-role-nfs)
[![dev](https://img.shields.io/github/actions/workflow/status/jomrr/ansible-role-nfs/dev.yml?branch=dev&event=push&label=dev)](https://github.com/jomrr/ansible-role-nfs/actions/workflows/dev.yml?query=branch%3Adev)
[![main](https://img.shields.io/github/actions/workflow/status/jomrr/ansible-role-nfs/main.yml?branch=main&event=push&label=main)](https://github.com/jomrr/ansible-role-nfs/actions/workflows/main.yml?query=branch%3Amain)

Configure Kerberos-protected NFSv4 exports and mounts on existing Active
Directory members.

## Purpose

Configure NFSv4 exports and persistent mounts on existing Samba AD or Microsoft
AD members. Managed exports and mounts require Kerberos, with authentication,
integrity protection, and encryption by default.

## Scope

### Managed

- NFS packages, NFSv4 protocol configuration, server services, and client GSS
  authentication.
- Exclusive ownership of /etc/exports, export directories, and explicitly
  declared fstab entries.
- The nfs/FQDN service principal on the existing AD computer account and its
  system-keytab entries.
- The computer account's DNS hostname, aligned with nfs_host_fqdn when adding
  NFS credentials.

### Not Managed

- Domain joining, Kerberos realm configuration, DNS, SSSD, and user or group
  identity mapping.
- Firewall rules and storage provisioning.

## Requirements

- Hosts must already have working AD Kerberos authentication and consistent
  user/group lookup. For example, apply jomrr.samba_ad_sssd first, using
  /etc/krb5.keytab and the same canonical FQDN.
- Servers require an existing Samba machine trust in /etc/samba/smb.conf and
  secrets.tdb, and host/FQDN@REALM keys in /etc/krb5.keytab. The machine account
  needs permission to add its own NFS SPN.
- The existing membership service must renew every service principal in
  /etc/krb5.keytab during password rotation. SSSD with adcli preserves these
  entries; Samba machine credentials must remain synchronized.
- NFS clients must resolve the server's canonical FQDN and users need valid
  Kerberos tickets. Network policy must permit TCP 2049 and the existing
  Kerberos/DNS services.
- Kernel NFS server and mount support are required. Rootless containers cannot
  provide the kernel NFS integration fixture.

## Dependencies

```yaml
collections:
  - name: community.general
    version: '>=12.0.0'
  - name: ansible.posix
    version: '>=2.0.0'
  - name: jomrr.samba
    version: '>=2.0.0'
```

## Role Variables

### `nfs_client`

Type: `bool`. Required: `false`.

Install the NFS client and manage declared mounts.

Default:

```yaml
nfs_client: true
```

### `nfs_server`

Type: `bool`. Required: `false`.

Install and run the NFSv4 server and manage /etc/exports exclusively.

Default:

```yaml
nfs_server: false
```

### `nfs_realm`

Type: `str`. Required: `true`.

Existing AD Kerberos realm with working host credentials and identity lookup.

### `nfs_host_fqdn`

Type: `str`. Required: `false`.

Canonical DNS name matching the existing host principal and AD computer account.

Default:

```yaml
nfs_host_fqdn: '{{ ansible_facts.fqdn | lower }}'
```

### `nfs_security`

Type: `str`. Required: `false`.

Kerberos security flavor required for every managed export and mount; krb5p also
encrypts traffic.

Default:

```yaml
nfs_security: krb5p
```

### `nfs_rpcbind_enabled`

Type: `bool`. Required: `false`.

Keep rpcbind available for other RPC applications; NFSv3 remains disabled.

Default:

```yaml
nfs_rpcbind_enabled: false
```

### `nfs_export_owner`

Type: `str`. Required: `false`.

Default export directory owner; individual exports can override owner.

Default:

```yaml
nfs_export_owner: root
```

### `nfs_export_group`

Type: `str`. Required: `false`.

Default export directory group; individual exports can override group.

Default:

```yaml
nfs_export_group: root
```

### `nfs_export_mode`

Type: `str`. Required: `false`.

Non-recursive export directory permissions; individual exports can override
mode.

Default:

```yaml
nfs_export_mode: '0750'
```

### `nfs_export_options`

Type: `list`. Required: `false`.

Base export options; per-host options follow these defaults. The sec option is
role-owned.

Default:

```yaml
nfs_export_options:
  - ro
  - sync
  - root_squash
  - no_subtree_check
```

### `nfs_exports`

Type: `dict`. Required: `false`.

Export paths mapped to directory attributes and a required hosts dictionary.
Each hosts key is an allowed client or network; its value is a list of export
options.
Optional owner, group, and mode override the corresponding role defaults.
Removing exports revokes access but preserves the directories and stored data.

Default:

```yaml
nfs_exports: {}
```

### `nfs_mount_options`

Type: `list`. Required: `false`.

Default mount options; per-mount opts replaces this list. Security and NFS
version are role-owned.

Default:

```yaml
nfs_mount_options:
  - hard
  - _netdev
  - nosuid
  - nodev
  - noexec
```

### `nfs_mount_state`

Type: `str`. Required: `false`.

Default state for declared mounts; each mount can override state.

Default:

```yaml
nfs_mount_state: mounted
```

### `nfs_mounts`

Type: `dict`. Required: `false`.

Mount paths mapped to required src, optional opts (list), and optional state.
Use the NFS server's canonical DNS name in src so Kerberos selects its
registered principal.
Specify state absent to remove a mount and its fstab entry; removing a
dictionary entry leaves it unmanaged.

Default:

```yaml
nfs_mounts: {}
```

## Managed Files

- `/etc/exports`
- `/etc/nfs.conf.d/90-nfs.conf`
- `/etc/gssproxy/24-nfs-server.conf`
- `/etc/systemd/system/nfs-mountd.service.d/90-nfs.conf`
- `/etc/fstab (declared mount entries only)`

## Check Mode

Package, file, service, and mount changes support check mode. SPN registration
and keytab updates are skipped; existing AD principals and keytab entries are
read to determine the required changes.

- The existing Kerberos/Samba membership must be operational even in check mode.

## Service Behavior

Services converge to enabled and started. Export changes use exportfs -ra; NFS
protocol changes restart the server. The role is idempotent when the declared
state, membership credentials, and service state are unchanged.

### Handlers

- Reload systemd before restarting the NFS server after a mount daemon override
  change.
- Reload gssproxy and restart rpc-gssd when NFS credentials are added.
- Apply changed exports without restarting unrelated client services.

## Security Notes

- Server management requires nfs_server=true; the role manages clients by
  default.
- nfs_security defaults to krb5p. krb5i provides integrity without encryption;
  krb5 provides authentication only. AUTH_SYS is not accepted for managed
  exports or mounts, and native options cannot override sec.
- Export defaults are read-only, synchronous, and root-squashed. Per-host rw
  must be requested explicitly.
- Client mounts default to nosuid, nodev, and noexec. Per-mount opts replaces
  the complete option list; mounts that require executable files can omit noexec
  while retaining the other restrictions.
- SPN registration uses machine credentials with Kerberos required. No
  administrator password is accepted by this role. Keytab updates are redacted
  and /etc/krb5.keytab is restricted to root with mode 0600.

## Operational Notes

- If the NFS SPN or its keytab entry is missing, adcli update adds it and
  synchronizes Samba credentials. Its native password-age policy can also renew
  an overdue machine password during this operation.
- Key renewal remains the responsibility of the existing membership service. The
  role does not compare key versions or replace an existing keytab entry solely
  because its key version is outdated.
- adcli aligns the AD computer's DNS hostname before adding the SPN. The role
  verifies the SPN directly in AD because adcli can return success after an LDAP
  update error.
- /etc/exports is replaced in full, including when nfs_exports is empty.
  Existing files under /etc/exports.d remain externally managed.
- Removing an export preserves its data. Remove client mounts explicitly with
  state absent before withdrawing an export.
- exports, nfs.conf, and gssproxy have no suitable side-effect-free
  candidate-file validator in the supported tooling. Native activation reports
  errors; systemd validates the mount daemon override before installation.

## Supported Platforms

| OS Family | Distribution | Version | Container Image |
| --------- | ------------ | ------- | --------------- |
| RedHat | AlmaLinux | latest | [jomrr/molecule-almalinux:latest](https://hub.docker.com/r/jomrr/molecule-almalinux) |
| Debian | Debian | latest | [jomrr/molecule-debian:latest](https://hub.docker.com/r/jomrr/molecule-debian) |
| RedHat | Fedora | latest | [jomrr/molecule-fedora:latest](https://hub.docker.com/r/jomrr/molecule-fedora) |
| Suse | OpenSuse Leap | latest | [jomrr/molecule-opensuse-leap:latest](https://hub.docker.com/r/jomrr/molecule-opensuse-leap) |
| Suse | OpenSuse Tumbleweed | latest | [jomrr/molecule-opensuse-tumbleweed:latest](https://hub.docker.com/r/jomrr/molecule-opensuse-tumbleweed) |
| Debian | Ubuntu | latest | [jomrr/molecule-ubuntu:latest](https://hub.docker.com/r/jomrr/molecule-ubuntu) |

## Example Playbook

### Kerberos-protected file server

Apply after the host has joined AD, for example with jomrr.samba_ad_sssd.

```yaml
- name: Configure NFS exports
  hosts: file_servers
  gather_facts: true
  roles:
    - role: jomrr.nfs
      nfs_realm: AD.EXAMPLE.COM
      nfs_client: false
      nfs_server: true
      nfs_exports:
        /srv/nfs/projects:
          group: file-writers@ad.example.com
          mode: '2770'
          hosts:
            192.0.2.0/24: [rw]
```

### Persistent encrypted mount

The existing AD membership and user tickets provide client authentication.

```yaml
- name: Configure NFS mounts
  hosts: workstations
  gather_facts: true
  roles:
    - role: jomrr.nfs
      nfs_realm: AD.EXAMPLE.COM
      nfs_server: false
      nfs_mounts:
        /mnt/projects:
          src: files.ad.example.com:/srv/nfs/projects
```

## References

- [Samba net: service principals](https://www.samba.org/samba/docs/current/man-html/net.8.html)
- [NFS export security options](https://manpages.debian.org/trixie/nfs-kernel-server/exports.5.en.html)

## Author

[Jonas Mauer](https://github.com/jomrr)

## License

This project is licensed under the MIT License.
See [LICENSE](LICENSE) for the full license text.

Copyright (c) 2019 Jonas Mauer.
