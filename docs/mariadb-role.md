# MariaDB Automation Role

## Purpose

The `roles/mariadb` role installs and configures MariaDB on a dedicated
Ubuntu Server database host. The shared `playbooks/database.yml` playbook
selects this role through the inventory variable `db_engine`.

## Target host

| Property | Value |
|---|---|
| Inventory host | `MariaDBServer` |
| IP address | `192.168.174.132` |
| Operating system | Ubuntu Server 24.04.5 LTS |
| MariaDB version validated | 10.11.14 |
| Service | `mariadb` |
| Database port | TCP 3306 |
| Bind address | `127.0.0.1` |

## Managed configuration

The role installs `mariadb-server`, `mariadb-client`, and
`python3-pymysql` (the Python driver required by Ansible database modules).
It prepares the
slow-query log directory, deploys the server configuration, and ensures
that the MariaDB service is enabled and running.

Configuration file:
`/etc/mysql/mariadb.conf.d/60-server-automation.cnf`

Expected settings:
- Bind address: `127.0.0.1`
- Port: `3306`
- Slow-query logging: enabled
- Slow-query threshold: one second
- Slow-query log: `/var/log/mysql/mariadb-slow.log`
- Log directory owner and group: `mysql:adm`
- Log directory permissions: `0750`

Configuration changes notify the MariaDB restart handler.

## Optional application database and user

Application database provisioning is controlled by:

`mariadb_manage_application_database: false`

The feature remains disabled unless explicitly enabled.

Default settings:
- Database: `appdb`
- Application user: `appuser`
- Password variable: `vault_mariadb_appuser_password`

The password is stored in the encrypted host Vault file:
`inventory/host_vars/MariaDBServer/vault.yml`

When enabled, the role validates the database and username, checks that
the Vault password is present, creates the database, and creates the
application user for `localhost`.

The application user receives privileges on the configured database
only (`<database>.*`), not global database administration privileges.
Credential-sensitive tasks use `no_log`.

## Security boundaries

MariaDB listens on loopback by default. This role does not configure
remote database access or firewall exceptions. Review connectivity
requirements, access controls, and firewall rules before considering
remote access.

## Deployment

Validate the shared playbook:

```bash
ansible-playbook --syntax-check playbooks/database.yml
```

Deploy only to the dedicated MariaDB host:

```bash
ansible-playbook playbooks/database.yml --limit MariaDBServer --diff
```

Redis remains optional and disabled by default.

## Validation performed

The deployment completed successfully on the dedicated MariaDB host.
Runtime checks confirmed that the service was active and enabled, the
listener was `127.0.0.1:3306`, and the managed slow-query settings were
present. The log directory had owner `mysql`, group `adm`, and mode
`0750`. A second Ansible run reported `changed=0` and `failed=0`.

### Application database provisioning

Status: **Successfully deployed and validated.**

Explicit approval was obtained before creating `appdb` and `appuser`
on `MariaDBServer`. Provisioning was enabled only for the deployment
run using the Ansible extra variable.

Validation results:

| Test | Result |
|---|---|
| Application database `appdb` verified and reconciled | PASS |
| Application user `appuser@localhost` verified and reconciled | PASS |
| TCP authentication using the application account | PASS |
| Create, insert, select and drop operations in `appdb` | PASS |
| Access to `mysql.user` denied | PASS |
| Global privileges limited to `USAGE` | PASS |
| Application privileges scoped to `appdb.*` | PASS |
| Global grant option not assigned | PASS |
| Repeat provisioning run reported `changed=0` | PASS |

The application user can perform database operations within `appdb`
but cannot read the MariaDB system users table. No global administrative
privileges or grant option were assigned.

The role default remains
`mariadb_manage_application_database: false`. Provisioning is opt-in
and is not automatically enabled for future deployments.

Passwords and credential hashes are excluded from this documentation.

Useful checks:

```bash
systemctl is-active mariadb
systemctl is-enabled mariadb
mariadb --version
sudo ss -lntp | grep ':3306'
sudo cat /etc/mysql/mariadb.conf.d/60-server-automation.cnf
sudo stat -c '%U:%G %a %n' /var/log/mysql
```

## Check-mode limitation

Check mode does not install packages. A service task can therefore fail
in check mode when MariaDB is not yet installed. Use check mode for
supported predictive checks, followed by deployment and runtime tests.

## Scope

This role manages the MariaDB server baseline and provides optional,
explicitly enabled application database and user provisioning.

Backups, replication, remote access, and production firewall changes
require separate, explicitly reviewed automation.
