# MySQL Role

## Purpose

Automates the baseline installation and configuration of MySQL Server on
Ubuntu Server 24.04 or newer.

## Requirements

- A supported Ubuntu managed host.
- Ansible privilege escalation (`become: true`) with valid sudo credentials.
- Network access to the configured Ubuntu package repositories.

## Managed configuration

The role:

- Installs `mysql-server` and `mysql-client`.
- Enables and starts the `mysql` service.
- Configures MySQL to listen on `127.0.0.1:3306` by default.
- Enables slow-query logging with a default threshold of one second.
- Creates `/var/log/mysql` with owner `mysql`, group `adm`, and mode `0750`.
- Places its managed configuration in
  `/etc/mysql/mysql.conf.d/60-server-automation.cnf`.

The role does not currently create application databases, database users,
grants, backups, or remote database access rules.

## Default variables

| Variable | Default |
|---|---|
| `mysql_packages` | `mysql-server`, `mysql-client` |
| `mysql_service_name` | `mysql` |
| `mysql_bind_address` | `127.0.0.1` |
| `mysql_port` | `3306` |
| `mysql_slow_query_log_enabled` | `true` |
| `mysql_slow_query_time` | `1` |
| `mysql_slow_query_log_file` | `/var/log/mysql/mysql-slow.log` |

Override defaults through role variables or inventory variables when required.
Keep database access loopback-only unless remote access is explicitly approved
and protected by appropriate network controls.

## Usage

The project uses `playbooks/mysql.yml`, which targets the `mysql_servers`
inventory group:

```bash
ansible-playbook --syntax-check playbooks/mysql.yml
ansible-playbook --check --diff playbooks/mysql.yml
ansible-playbook playbooks/mysql.yml
```

Verify the service, listener, configuration, and repeat-run idempotency after
deployment.

## Dependencies

None.
