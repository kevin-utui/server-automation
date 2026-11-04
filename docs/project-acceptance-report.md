# Server Automation Lab — Project Acceptance Report

## 1. Purpose and Scope

This report records the implementation status, validation evidence,
known limitations and outstanding activities for the VMware-based
Server Automation Lab.

The report covers laboratory implementation and testing only.
It does not constitute approval or acceptance for production deployment.

Production deployment remains subject to authorization, production-specific
inventory and credentials, security review, testing and formal change control.

## 2. Laboratory Environment

| Host | Role | IP address |
|---|---|---|
| ansserver | Ansible controller | 192.168.174.128 |
| AppServer | Application server | 192.168.174.129 |
| PostgreSqlServer | PostgreSQL server | 192.168.174.130 |
| MySQLServer | MySQL server | 192.168.174.131 |
| MariaDBServer | MariaDB server | 192.168.174.132 |
| ApiServer | API server and reverse proxy | 192.168.174.133 |
| RedisServer | Redis server | 192.168.174.134 |

- Virtualization: VMware Workstation
- Managed operating system: Ubuntu Server 24.04 LTS
- Ansible Core: 2.16.3
- Python: 3.12.3

## 3. Implementation Summary

The laboratory contains eight reusable Ansible roles:

1. common
2. postgresql
3. mysql
4. mariadb
5. redis
6. app
7. api
8. nginx

The multi-engine database playbook, `playbooks/database.yml`,
selects the database role according to each host's `db_engine` variable.

Redis has a dedicated inventory group and standalone deployment
playbook, `playbooks/redis.yml`. It is managed independently on
RedisServer. The optional Redis inclusion in the database playbook
remains disabled by default.

The application and API roles install and configure Docker Engine
and Docker Compose. The API environment includes a sample API deployment
and an Nginx reverse proxy.

## 4. Status Against the Original Project Plan

| Stage | Description | Current status |
|---|---|---|
| 1 | Preparação do ambiente | Complete |
| 2 | Planeamento técnico | Complete |
| 3 | Criação das máquinas virtuais | Complete |
| 4 | Instalação/configuração do Ansible | Complete |
| 5 | Desenvolvimento dos playbooks | Core implementation and documentation complete; formal handover pending |
| 6 | CI/CD GitLab | Deferred pending access to the correct personal GitLab account |
| 7 | Segurança/performance | Partially implemented; review findings and further work remain |
| 8 | Testes/validação | Core validation and idempotency checks passed; advanced tests remain |
| 9 | Documentação/entrega | Documentation complete; formal handover pending |

## 5. Validation Evidence

### 5.1 Integrated Laboratory Validation

The integrated validation playbook, `playbooks/validate_lab.yml`,
was executed successfully against the five application, API and
relational database servers. RedisServer is excluded from this
integrated run and is validated separately.

| Host | Successful tasks | Changed | Failed | Unreachable |
|---|---:|---:|---:|---:|
| ApiServer | 13 | 0 | 0 | 0 |
| AppServer | 5 | 0 | 0 | 0 |
| MariaDBServer | 5 | 0 | 0 | 0 |
| MySQLServer | 5 | 0 | 0 | 0 |
| PostgreSqlServer | 5 | 0 | 0 | 0 |

The validation confirmed host connectivity, expected services,
API container health, direct API health endpoint and Nginx
reverse-proxy health endpoint.

The validation playbook completed without changing managed systems.

### 5.2 Database Services

| Database engine | Validated version | Service status | Port |
|---|---|---|---:|
| PostgreSQL | 16 | Active | 5432 |
| MySQL | 8.0.46 | Active | 3306 |
| MariaDB | 10.11.14 | Active | 3306 |

Database role check-mode, normal execution and subsequent
idempotency checks completed successfully with no reported changes
during the final validation runs.

Redis was deployed and runtime-tested separately on RedisServer.
Authentication, loopback-only listening, service state, basic data
operations, persistence, restart recovery and idempotency were
successfully validated. A separate isolated AOF recovery test remains
outstanding.

### 5.3 Application Platform

AppServer validation confirmed:

- Docker Engine 29.1.3.
- Docker Compose 2.40.3.
- Docker service active.
- Application deployment and environment-file creation remain
  disabled by default.

Normal execution and the subsequent idempotency run completed
successfully with zero changes.

### 5.4 API Platform and Reverse Proxy

ApiServer validation confirmed:

- Docker container `sample-api` running and healthy.
- Sample API image `server-automation/sample-api:1.0.0`.
- API endpoint returned HTTP 200.
- Nginx 1.24.0 active.
- Nginx reverse proxy returned HTTP 200 for the API health endpoint.
- Nginx configuration syntax validated successfully.
- Docker automatic restart policy tested using a disposable container.
- Test process exited unexpectedly with code 1.
- Docker automatically restarted the disposable container;
  RestartCount increased to 1.
- The original sample-api container remained running and healthy
  throughout the isolated restart-policy test.
- Final API health endpoint verification returned HTTP 200.

API and Nginx role idempotency checks completed with zero changes.

### 5.5 Container Restart-Policy Validation

A controlled test was performed using a disposable container created
from the sample API image with the `unless-stopped` restart policy.

The test process exited with code 1. Docker automatically restarted
the disposable container, confirming that the configured restart
policy functions as expected.

The test container was subsequently removed. The actual `sample-api`
container remained healthy, and its API health endpoint returned
HTTP 200.

This test validates Docker restart-policy behaviour independently.
It does not constitute an application-specific crash-recovery test
of the actual `sample-api` container.

### 5.6 Container Log Rotation Validation

Docker's `json-file` logging configuration was inspected on the
actual `sample-api` container. The configured options were:

- Maximum log file size: `10m`.
- Maximum retained files: `3`.
- Compression of rotated files: enabled.

A disposable test container was created with the same logging
configuration and generated sufficient output to trigger log rotation.

The test confirmed that Docker retained three log files: one active
log and two compressed rotated files (`.gz`). The total retained
size was approximately 2.54 MB. The test output was also successfully
retrieved using `docker logs`.

The disposable test container was removed after validation.
The actual `sample-api` container remained running and healthy,
and its health endpoint returned HTTP 200.

This validates Docker log rotation and compression behaviour
independently without flooding the actual API logs.

## 6. Outstanding Work and Known Limitations

### 6.1 Redis

Redis is deployed on the dedicated RedisServer VM (192.168.174.134).

The following checks passed:

- Redis package installation and service activation.
- Authentication enforcement and authenticated PING.
- Loopback-only listening and protected mode.
- Basic SET, GET and DEL operations.
- RDB snapshot creation and restart recovery.
- AOF enabled with runtime write status reported as ok.
- Memory limit of 256 MiB and configured noeviction policy.
- Redis configuration and data/log directory permissions.
- Ansible idempotency (`changed=0` on the second deployment run).
- Acceptance playbook syntax and RDB recovery test.

The acceptance test successfully recovered a temporary key after
forcing an RDB snapshot and restarting Redis. The temporary key
was subsequently removed.

A separate isolated AOF recovery test has not yet been performed.
Redis remains intended for local access only; external access has
not been configured or approved.

### 6.2 Security and Performance

The security and performance review identified work that remains
before production consideration:

- TLS/HTTPS is not configured.
- API authentication has not been implemented.
- API-to-database connectivity and access requirements require
  an explicit design.
- Firewall policy remains outside the current laboratory scope.
- Nginx currently uses the placeholder hostname `api.example.com`.
- Nginx listens on all interfaces.
- Application-specific crash and recovery testing of the actual
  `sample-api` container remains outstanding. Docker's restart policy
  was verified independently using a disposable test container.

These findings are not represented as completed controls.

### 6.3 CI/CD

GitLab CI/CD implementation is deferred until the correct personal
GitLab account is available.

### 6.4 Production Readiness

The laboratory implementation is not approved for direct production
deployment. Production use requires a separate review of network
access, firewall policy, DNS, TLS certificates, API authentication,
database access, credentials, monitoring, backup and recovery,
and operational change control.

## 7. Acceptance Assessment

The core laboratory automation and integrated health validation
have been implemented successfully.

The evidence supports completion of the core DB, application,
API and reverse-proxy automation paths. It also demonstrates
successful integrated validation and idempotency checks.

However, the project remains subject to the outstanding work
identified in this report. In particular, isolated AOF recovery
testing, advanced resilience testing, security review actions,
formal handover and GitLab CI/CD remain open.

**Assessment:** Core laboratory implementation validated;
final project closure and production readiness are not yet approved.

## 8. Supporting Documentation

The following documents provide implementation details, configuration
references, validation evidence and security considerations supporting
this acceptance assessment.

### 8.1 Infrastructure and Security Baselines

- `docs/common-os-baseline.md` — Common operating system configuration,
  installed packages, time synchronisation and baseline validation.
- `docs/security-updates.md` — Automated security update configuration,
  reboot policy, validation and operational limitations.
- `docs/security-secrets.md` — Ansible Vault configuration, credential
  management and security-related implementation decisions.

### 8.2 Database Automation

- `docs/database-automation.md` — Database automation architecture,
  inventory organisation, deployment and validation strategy.
- `docs/postgresql-role.md` — PostgreSQL role implementation,
  application database provisioning and validation.
- `docs/mysql-role.md` — MySQL role configuration, application database
  management and validation.
- `docs/mariadb-role.md` — MariaDB role configuration, application
  database management and validation.
- `docs/redis-role.md` — Redis deployment, authentication, persistence,
  memory configuration and validation.

### 8.3 Application and API Platform

- `docs/api-server-baseline.md` — API server infrastructure, Docker
  configuration, sample API deployment and validation.
- `docs/api-platform-security-review.md` — API platform architecture,
  verified implementation evidence, security findings and remediation
  recommendations.
- `docs/nginx-reverse-proxy.md` — Nginx reverse proxy configuration,
  deployment and connectivity validation.

### 8.4 Project Overview

- `README.md` — Project objectives, laboratory topology, automation
  architecture, implemented roles, execution instructions and
  operational scope.
