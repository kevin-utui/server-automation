# PostgreSQL Automation Role

## 1. Purpose

The PostgreSQL role automates the installation and configuration of PostgreSQL on supported Ubuntu servers using Ansible. It provides a reusable, version-controlled approach to database server preparation and optional application database provisioning.

## 2. Current Lab Configuration

- **Inventory group:** `postgresql_servers` (child of `databases`)
- **Target host:** `PostgreSqlServer`
- **Operating system:** Ubuntu Server 24.04
- **PostgreSQL cluster:** `16/main`
- **PostgreSQL port:** `5432`
- **Listening address:** `localhost`
- **Slow-query logging threshold:** `1000` milliseconds
- **Service:** `postgresql`, enabled and running

## 3. Implemented Automation

The PostgreSQL role includes:

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

The optional task file `roles/postgresql/tasks/application_database.yml` implements application database and user management.

It supports:

- Validation of database and username formats.
- Validation that the application password is available through Ansible Vault.
- Management of an application database user with restricted attributes:
  - `LOGIN`
  - `NOSUPERUSER`
  - `NOCREATEDB`
  - `NOCREATEROLE`
- Management of an application database with the application user as its owner.

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

**Existing resources:** The `appdb` database and `appuser` account existed before the Ansible application provisioning test. They were verified and reconciled against the intended configuration; this milestone does not claim that they were newly created.

**Password reconciliation:** The user task uses `no_password_changes: true`. This avoids repeated change reports caused by password comparison limitations in `community.postgresql` 3.3.0. Existing account passwords are not automatically rotated by this task. Password rotation must be handled through a separate, explicitly controlled procedure.

## 4. Security Decisions

- PostgreSQL listens on localhost only.
- Remote database access remains disabled.
- Application database provisioning is disabled by default.
- Application credentials are managed through Ansible Vault.
- The application user has no superuser, database-creation or role-creation privileges.
- Application credentials are protected with `no_log` in the provisioning and authentication tasks.
- The application account was tested for database operations and denied access to the PostgreSQL authentication catalog (`pg_authid`).
- No firewall exceptions or remote authentication changes have been introduced.

Remote access must not be enabled until the approved application/API network requirements, authentication approach and database privileges have been defined.

## 5. Validation Performed

### 5.1 Baseline validation

- Ansible playbook syntax check passed.
- PostgreSQL installation completed successfully.
- PostgreSQL cluster `16/main` reported online.
- PostgreSQL service reported active.
- Port `5432` was verified listening on `127.0.0.1`.
- Configuration values were verified.
- Baseline deployment was verified as idempotent.
- The target Python PostgreSQL driver dependency was verified.

### 5.2 Application validation

The following application-level tests were completed:

- Vault password successfully authenticated as `appuser` against `appdb`.
- A temporary table was created in the `public` schema.
- A test record was inserted and read successfully.
- The temporary table was dropped successfully.
- Access to `pg_catalog.pg_authid` was denied to the application account.
- The authentication test was repeated successfully after application provisioning.

### 5.3 Provisioning and idempotency

Application provisioning was executed against `PostgreSqlServer` only, with `db_engine=postgresql` and `postgresql_manage_application_database=true`.

The first run reconciled the application user and reported one change. Investigation identified the password-comparison behaviour of `community.postgresql` version `3.3.0`.

After adding `no_password_changes: true`, the subsequent provisioning run completed with:

```text
ok=14
changed=0
unreachable=0
failed=0
skipped=1
```

The Redis role was skipped as expected because Redis is independently managed and disabled in the database group configuration.

### 5.4 Validation summary

| Component | Status |
|---|---|
| PostgreSQL installation | Validated |
| Service and cluster | Validated |
| Localhost-only listening | Validated |
| Slow-query configuration | Validated |
| Baseline idempotency | Validated |
| Application provisioning syntax | Validated |
| Application database and user reconciliation | Validated |
| Vault-based application authentication | Passed |
| Application CRUD operations | Passed |
| Authentication catalog access restriction | Passed |
| Application provisioning idempotency | Passed (`changed=0`) |
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
  --extra-vars "db_engine=postgresql postgresql_manage_application_database=false"
```

### 6.2 Validate syntax

```bash
ansible-playbook --syntax-check playbooks/database.yml \
  --extra-vars "db_engine=postgresql"
```

### 6.3 Enable application provisioning

Application provisioning is opt-in. Before enabling it, review existing database ownership, account attributes and intended privileges.

For the validated lab configuration:

```bash
ansible-playbook playbooks/database.yml \
  --limit PostgreSqlServer \
  --extra-vars "db_engine=postgresql postgresql_manage_application_database=true"
```

Always use `--limit PostgreSqlServer` when selecting this engine through the shared database playbook.

Password rotation is not performed automatically for existing users because `no_password_changes` is enabled. Use a separately reviewed and approved rotation procedure.

## 7. Outstanding Activities

- Define and approve the application/API connectivity and database access requirements.
- Validate application connectivity when the API integration design is available.
- Define any additional application-specific database privileges before granting them.
- Develop a controlled application credential rotation procedure.
- Keep remote PostgreSQL access disabled until the network and security design is approved.

## 8. Completion Assessment

The PostgreSQL installation, baseline configuration and optional application database provisioning have been implemented and runtime-validated in the lab.

The existing appdb and appuser resources were reconciled successfully. Authentication, CRUD operations, restricted catalog access and provisioning idempotency were verified.

The role is suitable for controlled PostgreSQL baseline deployment in the lab. Application provisioning remains disabled by default, remote access remains disabled, and credential rotation requires a separate controlled procedure.
