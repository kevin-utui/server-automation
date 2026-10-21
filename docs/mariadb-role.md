# MariaDB Automation Role

## Purpose

Installs and configures MariaDB on supported Ubuntu servers through
Ansible, using repeatable and version-controlled configuration.

## Defaults

- Packages: mariadb-server and mariadb-client
- Service: mariadb
- Bind address: 127.0.0.1
- Port: 3306
- Slow-query logging: enabled
- Slow-query threshold: 1 second
- Configuration file: /etc/mysql/mariadb.conf.d/60-server-automation.cnf
- Slow-query log: /var/log/mysql/mariadb-slow.log

## Implemented tasks

1. Validate the operating system.
2. Install MariaDB packages.
3. Ensure the log directory exists with controlled ownership and permissions.
4. Configure listening address, port, and slow-query logging.
5. Enable and start the MariaDB service.
6. Restart the service when its managed configuration changes.

## Security

MariaDB is configured to listen on localhost by default. Remote access,
database users, application credentials, and firewall exceptions are
not configured by this role at this stage.

Verify the effective listening socket and log-file permissions after
installation. Do not enable remote access until client requirements
and least-privilege database grants have been reviewed.

## Validation plan

- Playbook syntax check
- Successful package installation
- Service enabled and active
- Effective bind address and port verified
- Slow-query logging configuration verified
- Repeat run returns changed=0

## Execution

Set `db_engine: mariadb` in `inventory/group_vars/databases.yml`
when the database host is ready for MariaDB testing, then run:

```bash
ansible-playbook playbooks/database.yml

## Validation results

Tested on the lab database host running Ubuntu Server 24.04.

- Package installation completed successfully.
- MariaDB service is active and enabled.
- PostgreSQL remained active during the temporary co-installation test.
- MariaDB listens on 127.0.0.1:3306.
- PostgreSQL listens on 127.0.0.1:5432.
- Effective MariaDB bind address is 127.0.0.1.
- Slow-query logging is enabled with a one-second threshold.
- Slow-query log directory permissions are mysql:adm, mode 0750.
- Slow-query log file permissions are mysql:mysql, mode 0660.
- Second Ansible run returned changed=0 and failed=0.

## Lab test limitation

MariaDB and PostgreSQL were temporarily installed on the same host
to validate the MariaDB role. The intended architecture remains one
selected database engine per host or project. The inventory selection
has been restored to PostgreSQL after testing. MariaDB has not been
uninstalled, and its data has not been removed.
