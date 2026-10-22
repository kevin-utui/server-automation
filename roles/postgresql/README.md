# PostgreSQL Role

## Purpose
Installs and configures PostgreSQL on Ubuntu Server 24.04 and newer, including service management, localhost listening, slow-query logging, and optional application database management.

## Requirements
- Ansible Core and the `community.postgresql` collection.
- Python PostgreSQL driver on the managed server.
- Root and PostgreSQL-user privilege escalation.
- Ansible Vault for application credentials.
- The `acl` package on the managed server.

## Default Configuration
- `postgresql_listen_addresses`: `localhost`
- `postgresql_log_min_duration_statement`: `1000` milliseconds
- `postgresql_manage_application_database`: `true`
- `postgresql_application_database`: `appdb`
- `postgresql_application_user`: `appuser`
- Application password: `vault_postgresql_appuser_password`

The application role has LOGIN but is not a superuser and cannot create databases or roles. It owns its application database.

Set `postgresql_manage_application_database: false` to disable application database and user management.

## Security
- PostgreSQL listens on localhost by default.
- Application credentials are stored in Ansible Vault.
- The password-management task uses `no_log: true`.
- Review authentication, backups, monitoring, and access controls before production use.

## Dependencies
Uses `community.postgresql.postgresql_user` and `community.postgresql.postgresql_db`.

## Usage
Set `db_engine: postgresql` in the database inventory variables.

Validate and apply:
    ansible-playbook --syntax-check playbooks/database.yml
    ansible-playbook playbooks/database.yml

Repeat the playbook to verify idempotency. An already-configured host should report `changed=0` and `failed=0`.

## License
Project license to be determined.

## Maintainer
Server Automation lab.
