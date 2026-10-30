# MySQL Automation Role

## Purpose

The `roles/mysql` role installs and configures MySQL on the dedicated
`MySQLServer` lab host. The shared `playbooks/database.yml` playbook
selects this role using the inventory variable `db_engine`.

## Target host

| Property | Value |
|---|---|
| Inventory host | `MySQLServer` |
| IP address | `192.168.174.131` |
| Operating system | Ubuntu Server 24.04.5 LTS |
| Service | `mysql` |
| Default port | TCP 3306 |
| Default bind address | `127.0.0.1` |

## Role defaults

Defined in `roles/mysql/defaults/main.yml`:

- Packages: `mysql-server`, `mysql-client`
- Service name: `mysql`
- Bind address: `127.0.0.1`
- Port: `3306`
- Slow-query logging: enabled
- Slow-query threshold: one second
- Slow-query log: `/var/log/mysql/mysql-slow.log`

Managed configuration:
`/etc/mysql/mysql.conf.d/60-server-automation.cnf`

## Deployment

Check playbook syntax:

    ansible-playbook --syntax-check playbooks/database.yml

Deploy only to the MySQL host:

    ansible-playbook playbooks/database.yml --limit MySQLServer --diff

## Security boundaries

The default configuration binds MySQL to loopback. The role does not
configure application users, credentials, remote access, or firewall
exceptions. Review these requirements separately when needed.

## Validation checklist

After deployment, verify that:

- The MySQL service is active and enabled.
- The listener is bound to `127.0.0.1:3306`.
- The managed configuration contains the intended slow-query settings.
- Log directory permissions are appropriate.
- A second Ansible run reports `changed=0`.

Example checks:

    systemctl is-active mysql
    systemctl is-enabled mysql
    mysql --version
    sudo ss -lntp | grep ':3306'
    sudo cat /etc/mysql/mysql.conf.d/60-server-automation.cnf
    sudo stat -c '%U:%G %a %n' /var/log/mysql

## Validation performed

The deployment completed successfully on the dedicated MySQL host.
MySQL 8.0.46 was validated. Runtime checks confirmed that the service was
active and enabled, the listener was `127.0.0.1:3306`, and the managed
slow-query settings were present. A second Ansible run reported
`changed=0`, with no failed or unreachable hosts.

The log directory was also checked during operational validation.
