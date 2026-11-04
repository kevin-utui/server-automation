# MySQL Automation Role

## Purpose

The `roles/mysql` role installs and configures MySQL on the dedicated
`MySQLServer` lab host. The shared `playbooks/database.yml` playbook
selects this role using the inventory variable `db_engine`.

The role also supports optional, Vault-backed application database and
user provisioning.

## Target host

| Property | Value |
|---|---|
| Inventory host | `MySQLServer` |
| IP address | `192.168.174.131` |
| Operating system | Ubuntu Server 24.04.5 LTS |
| MySQL version validated | 8.0.46 |
| Service | `mysql` |
| Default port | TCP 3306 |
| Default bind address | `127.0.0.1` |

## Role defaults

Defined in `roles/mysql/defaults/main.yml`:

- Packages: `mysql-server`, `mysql-client`, `python3-pymysql`
- Service name: `mysql`
- Bind address: `127.0.0.1`
- Port: `3306`
- Slow-query logging: enabled
- Slow-query threshold: one second
- Slow-query log: `/var/log/mysql/mysql-slow.log`
- Application database management: disabled by default

The `python3-pymysql` package provides the Python driver required by
the `community.mysql` Ansible modules on the managed host.

Managed configuration:
`/etc/mysql/mysql.conf.d/60-server-automation.cnf`

## Deployment

Check playbook syntax:

    ansible-playbook --syntax-check playbooks/database.yml

Deploy only to the MySQL host:

    ansible-playbook playbooks/database.yml --limit MySQLServer

Application database provisioning remains disabled unless explicitly
enabled for a deployment.

## Optional application database management

The role can create an application database and a dedicated application
user. The feature is controlled by:

- `mysql_manage_application_database`
- `mysql_application_database`
- `mysql_application_user`
- `mysql_application_user_password`

The default setting for `mysql_manage_application_database` is `false`.

The application password is sourced from Ansible Vault through
`vault_mysql_appuser_password`. Password-handling tasks use `no_log`
to prevent credentials from appearing in Ansible output.

Example of explicitly enabling provisioning for the lab MySQL host:

    ansible-playbook playbooks/database.yml \
      --limit MySQLServer \
      --extra-vars '{
        "db_engine": "mysql",
        "mysql_manage_application_database": true,
        "mysql_application_database": "appdb",
        "mysql_application_user": "appuser"
      }'

The application user is restricted to `localhost` and receives
privileges on the selected application database only. It does not
receive global administrative privileges.

Review existing databases and users before enabling provisioning.
Do not reuse an existing application account without reviewing its
current permissions and credentials.

## Security boundaries

The default configuration binds MySQL to loopback. Remote database
access and firewall exceptions are not configured by this role.

Application provisioning is optional and disabled by default.
The application account is separate from the MySQL administrative
account. Its permissions are scoped to its designated database.

## Validation checklist

After deployment, verify that:

- The MySQL service is active and enabled.
- The listener is bound to `127.0.0.1:3306`.
- The managed configuration contains the intended slow-query settings.
- The log directory permissions are appropriate.
- The Python MySQL driver is available.
- A second Ansible run reports `changed=0`.

Example checks:

    systemctl is-active mysql
    systemctl is-enabled mysql
    mysql --version
    python3 -c 'import pymysql; print(pymysql.__version__)'
    sudo ss -lntp | grep ':3306'
    sudo cat /etc/mysql/mysql.conf.d/60-server-automation.cnf
    sudo stat -c '%U:%G %a %n' /var/log/mysql

For optional application database provisioning, verify:

    mysql --protocol=socket -NBe \
      "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='appdb';"

The following account lookup requires administrative database access.
Do not run it using the restricted application account.

    mysql --protocol=socket -NBe \
      "SELECT User, Host FROM mysql.user WHERE User='appuser';"

    mysql --protocol=socket -NBe \
      "SELECT GRANTEE, PRIVILEGE_TYPE, IS_GRANTABLE \
       FROM information_schema.USER_PRIVILEGES \
       WHERE GRANTEE LIKE '%appuser%';"

    mysql --protocol=socket -NBe \
      "SELECT GRANTEE, TABLE_SCHEMA, PRIVILEGE_TYPE, IS_GRANTABLE \
       FROM information_schema.SCHEMA_PRIVILEGES \
       WHERE GRANTEE LIKE '%appuser%';"

## Validation performed

The MySQL deployment completed successfully on the dedicated lab host.
MySQL 8.0.46 was validated. Runtime checks confirmed that the service
was active and enabled, the listener was `127.0.0.1:3306`, and the
managed slow-query settings were present.

The optional application provisioning capability was tested successfully:

- Verified and reconciled application database `appdb`.
- Verified and reconciled application user `appuser@localhost`.
- Verified that the account has `USAGE` globally.
- Verified that `ALL PRIVILEGES` are scoped to `appdb.*`.
- Confirmed that the account has no global administrative privileges.
- Authenticated successfully using the application account.
- Completed temporary-table creation, insertion, reading, and cleanup.
- Confirmed that the application account cannot access `mysql.user`.
- Repeated provisioning reported `changed=0`.

The Python driver dependency was initially missing and was installed
during troubleshooting. It is now included in the role package defaults
so future deployments install it automatically.

The application provisioning feature remains disabled by default.
