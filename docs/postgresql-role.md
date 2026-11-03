# PostgreSQL Automation Role

## 1. Purpose

The PostgreSQL role automates the installation and configuration of PostgreSQL on supported Ubuntu servers using Ansible. It provides a reusable, version-controlled approach to database server preparation and optional application database provisioning.

## 2. Current Lab Configuration

- **Inventory group:** `databases`
- **Target host:** `PostgreSqlServer`
- **Operating system:** Ubuntu Server 24.04
- **PostgreSQL cluster:** `16/main`
- **PostgreSQL port:** `5432`
- **Listening address:** `localhost`
- **Slow-query logging threshold:** `1000` milliseconds
- **Service:** `postgresql`, enabled and running

## 3. Implemented Automation

The PostgreSQL role currently includes:

1. Validation of the supported operating system.
2. Installation of PostgreSQL and `postgresql-contrib`.
3. Installation of the `python3-psycopg2` dependency.
4. Discovery of PostgreSQL configuration files.
5. Configuration of the listening address.
6. Configuration of the slow-query logging threshold.
7. Enabling and starting the PostgreSQL service.
8. Conditional application database and user provisioning.
9. PostgreSQL service restart when configuration changes require it.

### 3.1 Application Database Provisioning

The optional task file `roles/postgresql/tasks/application_database.yml` has been implemented.

It supports:

- Validation of database and username formats.
- Validation that the application password is available through Ansible Vault.
- Creation of an application database user with restricted attributes:
  - `LOGIN`
  - `NOSUPERUSER`
  - `NOCREATEDB`
  - `NOCREATEROLE`
- Creation of the application database with the application user as its owner.

The feature is controlled by:

```yaml
postgresql_manage_application_database: false
```

The application database and user defaults are:

```yaml
postgresql_application_database: appdb
postgresql_application_user: appuser
```

The application password is retrieved from:

```yaml
vault_postgresql_appuser_password
```

Passwords must never be stored in plaintext or exposed in execution logs.

**Validation status:** The automation code has passed syntax and YAML validation, but application database provisioning has not yet been runtime-validated.

Existing `appdb` and `appuser` objects were identified during preliminary checks. They have been preserved and must not be modified or replaced without a separate review and explicit approval.

## 4. Security Decisions

- PostgreSQL listens on localhost only.
- Remote database access remains disabled.
- Application database provisioning is disabled by default.
- Application credentials are managed through Ansible Vault.
- The application user is configured without superuser or database/role creation privileges.
- Application credentials must not be exposed in logs.
- No firewall exceptions or remote authentication changes have been introduced.

Remote access must not be enabled until the approved application/API network requirements, authentication approach, and database privileges have been defined.

## 5. Validation Performed

The following baseline validations have been completed:

- Ansible playbook syntax check passed.
- PostgreSQL installation completed successfully.
- PostgreSQL cluster `16/main` reported online.
- PostgreSQL service reported active.
- Port `5432` was verified listening on `127.0.0.1`.
- Configuration values were verified.
- The second playbook run completed with `changed=0` and `failed=0`.
- The target Python PostgreSQL driver dependency was verified.

Additional validation status:

| Component | Status |
|---|---|
| PostgreSQL installation | Validated |
| Service and cluster | Validated |
| Localhost-only listening | Validated |
| Slow-query configuration | Validated |
| Baseline idempotency | Validated |
| Application provisioning syntax | Validated |
| Application provisioning runtime | Pending |
| Remote access configuration | Not implemented |

## 6. Execution

The PostgreSQL engine is selected for this host through:

`inventory/group_vars/postgresql_servers/vars.yml`

Configuration:

```yaml
db_engine: postgresql
db_redis_enabled: false
```

### 6.1 Deploy the PostgreSQL baseline

```bash
ansible-playbook playbooks/database.yml \
  --limit PostgreSqlServer \
  -e postgresql_manage_application_database=false
```

### 6.2 Validate syntax and preview changes

```bash
ansible-playbook --syntax-check playbooks/database.yml

ansible-playbook playbooks/database.yml \
  --limit PostgreSqlServer \
  --check \
  -e postgresql_manage_application_database=false
```

### 6.3 Application provisioning

Application database and user management must remain disabled until:

1. The existing database and user have been reviewed.
2. The intended ownership and privilege requirements have been confirmed.
3. The provisioning tasks have been reviewed against the existing PostgreSQL objects.
4. Explicit approval has been obtained for the intended changes.

Do not use the baseline deployment procedure to change application credentials or existing database data.

## 7. Outstanding Activities

- Review application provisioning behaviour against the existing `appdb` and `appuser` objects.
- Define and approve the required application database privileges.
- Obtain approval before runtime-testing application provisioning.
- Validate application connectivity when application/API requirements are available.
- Update this document with runtime test results after validation.

## 8. Completion Assessment

The PostgreSQL server installation and baseline configuration are implemented and validated. Optional application database provisioning has been implemented at the Ansible role level, but remains pending runtime validation and approval.

The role is suitable for controlled PostgreSQL baseline deployment in the lab, with application provisioning and remote access remaining disabled by default.
