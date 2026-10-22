# Database Server Automation

## Purpose

This project uses Ansible to configure database servers through reusable,
engine-specific roles. Each database VM selects its engine independently.

## Lab topology

| Inventory host | IP address | Database engine | Inventory group |
|---|---|---|---|
| `DataBaseServer` | `192.168.174.130` | PostgreSQL | `postgresql_servers` |
| `MySQLServer` | `192.168.174.131` | MySQL | `mysql_servers` |
| `MariaDBServer` | `192.168.174.132` | MariaDB | `mariadb_servers` |
| `AppServer` | `192.168.174.129` | Application server | `applications` |

The three database hosts belong to the parent group `databases`.
The application host is managed separately.

## Architecture

The main entry point is `playbooks/database.yml`.

The playbook:

1. Gathers host facts and validates the selected `db_engine`.
2. Accepts `mariadb`, `mysql`, or `postgresql`.
3. Includes the corresponding role.
4. Includes Redis only when `db_redis_enabled` is true.

Database engine selection is configured in inventory group variables.
The child groups select their respective engines. The shared database
group provides common database-server settings.

Redis is optional and disabled by default.

## Database roles

- `roles/postgresql`: PostgreSQL installation and configuration.
- `roles/mysql`: MySQL installation and configuration.
- `roles/mariadb`: MariaDB installation and configuration.
- `roles/redis`: optional role; do not enable without reviewing its
  configuration and validating its requirements.

Engine-specific settings and validation instructions are documented in
`docs/postgresql-role.md`, `docs/mysql-role.md`, and
`docs/mariadb-role.md`.

## Deployment

Check syntax:

    ansible-playbook --syntax-check playbooks/database.yml

List the hosts targeted by the playbook:

    ansible-playbook playbooks/database.yml --list-hosts

Deploy to one database host at a time during lab validation:

    ansible-playbook playbooks/database.yml --limit DataBaseServer --diff
    ansible-playbook playbooks/database.yml --limit MySQLServer --diff
    ansible-playbook playbooks/database.yml --limit MariaDBServer --diff

Review the proposed changes and validate the target service after each
deployment. Do not run a broad database deployment without first checking
the inventory and selected engine for every target host.

## Security baseline

- Secrets are stored using Ansible Vault.
- Vault password files must remain protected and must not be committed.
- Database listeners default to loopback unless explicitly configured
  otherwise.
- Remote database access and firewall exceptions require a separate
  review of application requirements and access controls.
- Production changes must follow an approved change process.

## Validation strategy

For each database host:

1. Confirm inventory mapping and the effective `db_engine`.
2. Run playbook syntax and inventory checks.
3. Deploy only to the intended host.
4. Verify service status, listening address, and managed configuration.
5. Run the playbook again and confirm idempotency where applicable.
6. Record runtime results and resolve failures before proceeding.

MariaDB has passed a dedicated-host deployment and runtime validation,
including a second run with `changed=0`. Consult each engine's role
documentation for its specific validation details. Do not treat the
existence of a role or documentation as proof of a fresh runtime test.

## Scope and change control

This is a lab automation project. Database backups, replication,
application-specific database provisioning, remote access, and production
firewall changes should be implemented and validated as separate tasks.
Keep changes version-controlled, review diffs, and commit only files
related to the completed milestone.
