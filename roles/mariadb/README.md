# MariaDB Ansible Role

## Purpose

Installs and configures MariaDB on supported Ubuntu Server hosts.

## Requirements

- Ubuntu Server 24.04 or later.
- Ansible privilege escalation (`become: true`).
- A working APT package repository.

## Role defaults

Defined in `defaults/main.yml`:

- `mariadb_packages`: server and client packages.
- `mariadb_service_name`: `mariadb`.
- `mariadb_bind_address`: `127.0.0.1`.
- `mariadb_port`: `3306`.
- `mariadb_slow_query_log_enabled`: `true`.
- `mariadb_slow_query_time`: `1`.
- `mariadb_slow_query_log_file`: `/var/log/mysql/mariadb-slow.log`.

## Usage

The project selects this role through `playbooks/database.yml` by setting
`db_engine: mariadb` for the target host or inventory group.

Deploy to the dedicated lab host:

```bash
ansible-playbook playbooks/database.yml --limit MariaDBServer --diff
```

## Security

The default listener is loopback-only. This role does not create application
users or credentials, configure remote access, or manage firewall exceptions.
Review these requirements separately before enabling remote connectivity.

## Validation

Verify service status, listening address, managed configuration, and
idempotency after deployment. A second unchanged run should report
`changed=0`.
