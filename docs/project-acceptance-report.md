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
| 5 | Desenvolvimento dos playbooks | Core implementation and documentation complete |
| 6 | CI/CD GitHub Actions | GitHub repository created; remote connection and pipeline implementation pending |
| 7 | Segurança/performance | Lab controls implemented; production security findings remain documented and deferred |
| 8 | Testes/validação | Core, idempotency, API resilience, logging and Redis persistence validation completed; historical integrated validation documented |
| 9 | Documentação/entrega | Documentation substantially complete; final report review and handover pending |

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
operations, RDB persistence, restart recovery and idempotency were
successfully validated.

A separate isolated AOF recovery test also passed. The test copied the
active multipart AOF dataset to a temporary directory, started an
independent Redis 7.0.15 instance with RDB snapshots disabled, and
successfully recovered a fresh test marker from the copied AOF files.
The isolated instance, temporary files and test marker were subsequently
removed. The original Redis data remained intact.

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
- Docker restart-policy behaviour validated using a disposable container.
- Actual `sample-api` crash-recovery test completed: the Uvicorn process
  was terminated with SIGTERM and Docker restarted the container.
- Recovery completed in approximately 9 seconds.
- Container returned to running and healthy state; RestartCount increased
  from 0 to 1 and restart policy remained `unless-stopped`.
- Nginx reverse-proxy health endpoint returned HTTP 200 after recovery.
- API-06, API-07, API-08, API-09, API-10 and API-11 acceptance activities
  are documented as complete in `docs/api-platform-security-review.md`.

API and Nginx role idempotency checks completed with zero changes.

### 5.5 Actual API Crash-Recovery Validation

An application-specific recovery test was performed against the actual
`sample-api` container. The Uvicorn process running as the application
user was terminated with SIGTERM.

Docker automatically restarted the container under its configured
`unless-stopped` policy. Recovery completed in approximately 9 seconds.
The container returned to running and healthy state, with RestartCount
increasing from 0 to 1.

The Nginx reverse-proxy health endpoint returned HTTP 200 after recovery.
This test is documented as API-11 and passed.

A separate disposable-container restart-policy test was also performed
previously. The actual application recovery test provides the stronger
application-specific acceptance evidence.

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

An isolated AOF recovery test passed using a copied multipart AOF
dataset and a separate Redis instance with RDB snapshots disabled.
The recovery marker was successfully restored. All temporary test
resources and the live test marker were removed after validation.

Redis remains intended for local access only; external access has
not been configured or approved.

### 6.2 Security and Performance

The security review identified the following outstanding findings:

- API-01 — Host firewall: pending network design and approval.
- API-02 — TLS/HTTPS: pending hostname, DNS and certificate decisions.
- API-03 — API authentication and authorization: pending application
  requirements.
- API-04 — API-to-database connectivity: pending integration and network
  design.
- API-05 — Historical MariaDB installation on PostgreSqlServer:
  package cleanup is complete; residual-data and backup review remain
  pending.

Nginx continues to use the placeholder hostname `api.example.com` and
listen on all interfaces. Both settings require production-specific
review.

API-06 through API-11 are documented as complete in
`docs/api-platform-security-review.md`. API-09 was closed through an
approved design decision distinguishing project-file staging from
application deployment; no additional staging variable was required.

The outstanding findings are not represented as completed security
controls. They remain subject to design decisions, requirements and
approval before production deployment.

### 6.3 CI/CD

A personal GitHub repository is available and currently empty. Local remote
configuration, SSH authentication, pipeline configuration and pipeline
execution remain to be completed. The planned initial pipeline will validate
Ansible syntax and project structure only; automatic deployment to
managed servers is outside its initial scope.

### 6.4 Production Readiness

The laboratory implementation is not approved for direct production
deployment. Production use requires a separate review of network
access, firewall policy, DNS, TLS certificates, API authentication,
database access, credentials, monitoring, backup and recovery,
and operational change control.

## 7. Acceptance Assessment

The core laboratory automation and integrated health validation
have been implemented successfully.

The evidence supports completion of the core database, application,
API and reverse-proxy automation paths. Historical integrated validation
and idempotency checks passed. Separate acceptance evidence now also
covers Redis AOF recovery, API crash recovery, container hardening,
dependency reproducibility and sustained log rotation.

Remaining laboratory closure activities are GitHub Actions implementation,
final documentation review and formal handover. Production security
findings remain documented and deferred where they require architecture,
business requirements or explicit approval.

**Assessment:** Core laboratory implementation and the documented
acceptance tests are substantially complete. GitHub Actions and formal
handover remain open. Production readiness is not approved.

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
