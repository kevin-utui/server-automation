# PostgreSQL Automation Role

## Purpose

The PostgreSQL role installs and configures PostgreSQL on supported
Ubuntu servers through Ansible. It is intended for repeatable,
version-controlled lab automation.

## Current lab configuration

- Inventory group: `databases`
- Target host: `DataBaseServer`
- Operating system: Ubuntu Server 24.04
- PostgreSQL cluster: `16/main`
- PostgreSQL port: `5432`
- Listening address: `localhost`
- Slow-query logging threshold: `1000` milliseconds
- Service: `postgresql`, enabled and running

## Implemented tasks

1. Validate the supported operating system.
2. Install PostgreSQL and `postgresql-contrib`.
3. Discover the PostgreSQL configuration files.
4. Configure the listening address.
5. Configure the slow-query logging threshold.
6. Enable and start the PostgreSQL service.
7. Restart PostgreSQL when configuration changes require it.

## Security decisions

PostgreSQL listens on localhost only. Remote database access, database
users, application credentials, authentication rules, and firewall
exceptions have not yet been configured.

Do not enable remote access until the approved application/API network
requirements and database privileges have been defined.

## Validation performed

- Ansible playbook syntax check passed.
- PostgreSQL installation completed successfully.
- PostgreSQL cluster `16/main` reported online.
- PostgreSQL service reported active.
- Port 5432 was verified listening on `127.0.0.1`.
- Configuration values were verified.
- Second playbook run completed with `changed=0` and `failed=0`.

## Execution

Select the PostgreSQL engine for the database host in
`inventory/group_vars/databases.yml`:

```yaml
db_engine: postgresql
db_redis_enabled: false
```

Deploy only to the PostgreSQL lab host:

```bash
ansible-playbook playbooks/database.yml --limit DataBaseServer -e postgresql_manage_application_database=false
```

Validate syntax and preview changes before deployment:

```bash
ansible-playbook --syntax-check playbooks/database.yml
ansible-playbook playbooks/database.yml --limit DataBaseServer --check -e postgresql_manage_application_database=false
```

Application database and user management are disabled by default.
Keep them disabled unless the requirements and task behaviour have been
reviewed and explicitly approved. Do not use this procedure to change
application credentials or existing database data.
