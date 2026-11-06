# Server Automation Lab

## 1. Project Overview

The Server Automation Lab is a VMware-based environment for developing, testing, validating and documenting reusable Ansible automation for database, application and API infrastructure.

The project aims to establish consistent server configuration, improve operational reliability, apply security baselines, and provide repeatable automation through Ansible roles and playbooks.

All development and validation activities are performed in the laboratory environment. Production deployment is a separate activity subject to authorization, change control and production-specific inventory and credential configuration.

## 2. Infrastructure

### Ansible Controller

| Host | Role | IP address |
|---|---|---|
| ansserver | Ansible controller | 192.168.174.128 |

### Managed Servers

| Host | Role | IP address |
|---|---|---|
| AppServer | Application server | 192.168.174.129 |
| PostgreSqlServer | PostgreSQL database server | 192.168.174.130 |
| MySQLServer | MySQL database server | 192.168.174.131 |
| MariaDBServer | MariaDB database server | 192.168.174.132 |
| ApiServer | API server and reverse proxy | 192.168.174.133 |
| RedisServer | Redis server | 192.168.174.134 |

**Virtualization:** VMware Workstation
**Managed operating system:** Ubuntu Server 24.04 LTS
**Automation platform:** Ansible Core 2.16.3
**Python:** 3.12.3

## 3. Automation Architecture

The project uses reusable Ansible roles, inventory groups, group variables, host-specific variables and Ansible Vault.

### Implemented roles

| Role | Purpose |
|---|---|
| common | Common OS baseline and security-update configuration |
| postgresql | PostgreSQL installation and configuration |
| mysql | MySQL installation and configuration |
| mariadb | MariaDB installation and configuration |
| redis | Redis installation, authentication and persistence |
| app | Application server Docker and Compose baseline |
| api | API server baseline and sample API automation |
| nginx | Nginx reverse proxy configuration |

Redis is managed independently through its dedicated `redis` inventory
group and `playbooks/redis.yml` playbook. It runs on RedisServer.
The optional Redis inclusion in `database.yml` remains disabled by default.

## 4. Project Structure

- `inventory/` — managed hosts, groups and variables
- `inventory/group_vars/` — group-level configuration
- `inventory/host_vars/` — host-specific configuration and Vault files
- `playbooks/` — automation and validation playbooks
- `roles/` — reusable Ansible roles
- `api-projects/` — sample API application source
- `docs/` — technical documentation and security reviews
- `files/` — static automation files
- `templates/` — reusable configuration templates
- `reports/` — generated project reports

## 5. Main Playbooks

| Playbook | Purpose |
|---|---|
| `os_baseline.yml` | Apply common OS configuration |
| `security_updates.yml` | Configure automated security updates |
| `database.yml` | Configure the selected database engine |
| `redis.yml` | Configure the dedicated Redis server |
| `redis_acceptance.yml` | Validate Redis persistence and restart recovery |
| `app.yml` | Configure AppServer |
| `api.yml` | Configure ApiServer |
| `nginx.yml` | Configure the API reverse proxy |
| `security_baseline.yml` | Collect security baseline information |
| `validate_lab.yml` | Validate connectivity, services and API health |

`database.yml` is the authoritative database deployment playbook. It selects
PostgreSQL, MySQL or MariaDB through `db_engine`. Redis is managed separately
through `redis.yml`; its optional inclusion in `database.yml` remains disabled
by default.

## 6. Execution and Validation

Run commands from the Ansible controller in the project root directory.

Check connectivity:

    ansible all -m ansible.builtin.ping

Validate syntax:

    ansible-playbook --syntax-check playbooks/validate_lab.yml

Apply the common OS baseline:

    ansible-playbook playbooks/os_baseline.yml

Configure database servers:

    ansible-playbook playbooks/database.yml

Configure the application server:

    ansible-playbook playbooks/app.yml

Configure the API server:

    ansible-playbook playbooks/api.yml

Configure Nginx:

    ansible-playbook playbooks/nginx.yml

Run integrated laboratory validation:

    ansible-playbook playbooks/validate_lab.yml

Use Ansible Vault for encrypted variables. Never expose decrypted values in terminal output, logs or documentation.

## 7. Security Principles

- Use Ansible Vault for sensitive variables.
- Keep Vault password files outside version control.
- Restrict SSH access and use authorized accounts.
- Preserve SSH host-key verification.
- Keep database services bound to localhost unless access is explicitly approved.
- Protect Redis with Ansible Vault authentication credentials.
- Keep Redis bound to loopback interfaces unless external access is explicitly
  designed, secured and approved.
- Do not expose private keys, passwords or application secrets in Git.
- Validate configuration changes before applying them.
- Review service restarts and configuration changes before production deployment.

## 8. Testing and Acceptance

The laboratory validation programme includes:

- Ansible connectivity across the five servers included in the integrated validation run.
- Operating-system and service checks.
- Database service validation.
- Docker Engine and Docker Compose role validation.
- API container and health-endpoint checks.
- Nginx reverse-proxy health validation.
- Docker automatic restart-policy validation using a disposable container.
- Docker log rotation and compression stress testing using a disposable container.
- Ansible idempotency checks.

The integrated validation playbook has passed on the five application,
API and database servers included in that validation run. It verifies host
connectivity, expected service states and the API health path on ApiServer.
RedisServer is validated separately and is not included in that historical
five-server integrated validation result.

The application, API, Nginx, database, common OS and security-update
components have also undergone their respective role-level validation
procedures. Docker's `unless-stopped` restart policy and `json-file`
log rotation with compression were verified using disposable test
containers. Application-specific crash recovery of the actual API container was
validated: SIGTERM triggered Docker restart, the container returned to a
healthy state in approximately 9 seconds, and the Nginx health endpoint
returned HTTP 200.

Redis runtime acceptance passed separately, including authentication,
loopback-only listening, basic data operations, RDB snapshot creation,
restart recovery and Ansible idempotency. A separate isolated AOF
recovery test also passed using a copied multipart AOF dataset and an
independent Redis instance. Temporary test
resources were removed and the original Redis data remained intact.

## 9. Scope and Production Deployment

This project establishes a validated laboratory automation baseline.

Production deployment is not performed automatically by the laboratory playbooks.

Before production use:

1. Confirm production server inventory and SSH access.
2. Configure production-specific encrypted credentials.
3. Review host-specific variables and application requirements.
4. Validate playbooks against the intended production configuration.
5. Obtain the required approvals and change window.
6. Execute controlled deployment and post-change validation.

No production network or firewall changes are included in the current laboratory scope.

## 10. Related Documentation

Detailed implementation and validation records are maintained in `docs/`, including:

- Common OS baseline
- Security updates
- Ansible Vault and secrets management
- PostgreSQL, MySQL and MariaDB automation
- Redis role
- API server baseline
- API platform security review
- Nginx reverse proxy

## 11. Current Project Status

The laboratory infrastructure, Ansible configuration, core automation roles, service configurations and integrated validation are implemented.

GitHub Actions syntax validation is implemented and has passed.
Remaining activities are final documentation review and formal handover.
Production-specific security findings and architecture decisions remain
deferred pending requirements, review and authorization.
