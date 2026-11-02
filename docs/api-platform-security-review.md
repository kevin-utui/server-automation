# API Platform Integration and Security Review

## 1. Objective

This document records the integration and security review of the API platform
implemented in the Server Automation laboratory.

The review evaluates the API server, Docker runtime, sample API deployment,
Nginx reverse proxy, database-server architecture, and Ansible automation.

The purpose is to identify security gaps, document verified implementation
evidence, and define controlled remediation work.

This review is an assessment of the current laboratory configuration. It is
not a production security certification or a penetration-test report.

## 2. Review scope

The review covers:

- API server operating system and network listeners.
- Docker Engine and container runtime configuration.
- Sample FastAPI application and Docker Compose deployment.
- Nginx reverse proxy and HTTP exposure.
- Container isolation, resource limits, and logging.
- API-to-database network architecture.
- Ansible deployment controls and configuration management.
- Operational validation, recovery, and outstanding tests.

No production systems are in scope.

No firewall, network, application, database, or service configuration changes
are authorized by this assessment document.

## 3. Environment and architecture

### 3.1 Laboratory servers

| Server | Address | Purpose |
|---|---|---|
| AppServer | 192.168.174.129 | Application platform and Docker baseline |
| PostgreSqlServer | 192.168.174.130 | PostgreSQL database server |
| MySQLServer | 192.168.174.131 | MySQL database server |
| MariaDBServer | 192.168.174.132 | MariaDB database server |
| ApiServer | 192.168.174.133 | Docker API platform and Nginx reverse proxy |

Operating system on ApiServer: Ubuntu Server 24.04.5 LTS.

### 3.2 Intended API architecture

The API server is designed to host independently managed Docker Compose
projects for internally developed APIs and APIs supplied by external
vendors or systems.

Nginx acts as the reverse proxy in front of the API containers.

The sample API is published on the host loopback interface at
127.0.0.1:8000. Nginx proxies HTTP requests to this local endpoint.

Database services are hosted on dedicated database VMs. Database services
currently bind to loopback interfaces and are not remotely accessible through
their database ports.

The intended architecture is:

    API clients
        |
        v
    Nginx reverse proxy
        |
        v
    127.0.0.1:8000
        |
        v
    Sample API container
        |
        v
    Future project-specific database connectivity
        |
        v
    Dedicated database servers

The final API-to-database network design remains pending.

## 4. Verified implementation and evidence

### 4.1 API server and network listeners

The following were verified on ApiServer:

- Ubuntu Server 24.04.5 LTS.
- Docker service active.
- Nginx service active.
- Nginx configuration test successful.
- SSH listening on TCP port 22 on all interfaces.
- Nginx listening on TCP port 80 on IPv4 and IPv6 interfaces.
- Sample API published on 127.0.0.1:8000.
- UFW status: inactive.

The API container port is bound to loopback and is not directly published
on the server's external interfaces.

The presence of listeners on all interfaces does not, by itself, prove
exposure to the public internet. VMware networking and upstream network
controls must also be assessed.

### 4.2 Docker daemon logging

The Docker daemon uses the following logging configuration:

    {
      "log-driver": "json-file",
      "log-opts": {
        "max-size": "10m",
        "max-file": "3",
        "compress": "true"
      }
    }

This limits individual container log files to 10 MB and retains up to
three files, with compression enabled.

The configuration was validated as JSON and applied through Ansible.

An actual log-rotation stress test remains outstanding.

### 4.3 Sample API container

The sample API container was verified as running and healthy.

| Control | Verified configuration |
|---|---|
| Image | server-automation/sample-api:1.0.0 |
| Container user | appuser |
| Memory limit | 256 MiB |
| CPU limit | 0.5 CPU |
| Root filesystem | Read-only |
| Temporary filesystem | /tmp, 16 MiB, noexec, nosuid |
| Privileged mode | Disabled |
| Additional capabilities | None added |
| Security option | no-new-privileges:true |
| Restart policy | unless-stopped |
| Logging | json-file, 10 MB, 3 files, compressed |
| Published port | 127.0.0.1:8000 |
| Health check | Configured and healthy |
| Host mounts | None |

Docker's default capability set has not been explicitly dropped.
The container uses the docker-default AppArmor profile.

The API root and health endpoints returned HTTP 200 during validation.
A container restart test also completed successfully.

### 4.4 Nginx reverse proxy

Nginx is configured with:

- HTTP listener on port 80.
- Placeholder server name api.example.com.
- Reverse proxy to 127.0.0.1:8000.
- Forwarding headers.
- Dedicated API access and error log paths.
- Configured proxy timeouts.

Validation confirmed:

- nginx -t successful.
- Nginx service active and enabled.
- Requests sent to ApiServer with Host: api.example.com reached the
  sample API successfully.
- The API health endpoint returned HTTP 200 through Nginx.

The hostname api.example.com is a laboratory placeholder, not a confirmed
production DNS name.

HTTPS and TLS certificates have not been configured.

### 4.5 API deployment automation

Ansible manages the API server baseline and sample API deployment.

The deployment control variable is:

    api_deploy_enabled: false

The deployment tasks are conditionally included when this variable is enabled.
The sample API project files are currently staged by the role even when
deployment is disabled.

The deployment workflow includes:

- Compose configuration validation.
- Docker Compose deployment through the community.docker collection.
- API health-check validation.
- Controlled deployment through an explicit variable.

A deployment was successfully performed with the deployment variable
explicitly enabled.

### 4.6 Database server network state

The database services currently bind to loopback:

| Server | Database service | Listener |
|---|---|---|
| PostgreSqlServer | PostgreSQL | 127.0.0.1:5432 |
| MySQLServer | MySQL | 127.0.0.1:3306 and 127.0.0.1:33060 |
| MariaDBServer | MariaDB | 127.0.0.1:3306 |

UFW is inactive on the reviewed database servers.

The current loopback bindings prevent direct remote connections through
these database listeners. API-to-database connectivity has not yet been
implemented or validated.

### 4.7 Historical MariaDB cleanup on PostgreSqlServer

A historical MariaDB installation was identified on PostgreSqlServer after
the database engines were separated onto dedicated VMs.

The MariaDB service was stopped and disabled. A logical backup was created
before package removal.

The MariaDB server, client, and provider packages were subsequently purged.

Post-cleanup verification confirmed:

- PostgreSQL service active.
- PostgreSQL 16 cluster main online on port 5432.
- PostgreSQL database appdb still present and owned by appuser.
- No MariaDB server/client packages remaining.
- MariaDB service inactive and not found.
- No MariaDB listener on port 3306.
- MariaDB data directory still retained at /var/lib/mysql.
- Logical backup retained at /root/mariadb-cleanup-backup/mariadb-all-databases.sql.

The backup SHA-256 checksum is:

    a2a28b7102b5c7466c82eed1fbddc7fedddfc8ebe7dfcd9f90be4beb477ed6ab

The backup has not been restore-tested. The retained data directory and
logical backup must not be deleted until recovery requirements are reviewed.

## 5. Security findings and recommendations

The following findings describe the state observed during this review.
Priority indicates the importance of addressing the issue before production
use; it does not imply confirmed exploitation.

### API-01 — Host firewall inactive

Priority: High

Evidence:
- UFW is inactive on ApiServer.
- SSH and Nginx listen on all interfaces.

Risk:
The host is not enforcing an inbound access policy through UFW. Actual
reachability depends on VMware and upstream network controls.

Recommendation:
- Identify the management source network and authorized administrators.
- Define the permitted inbound traffic.
- Restrict SSH to approved management sources.
- Permit HTTPS when TLS is implemented.
- Retain HTTP only where required for redirection or certificate validation.
- Validate access before and after enabling firewall rules.

Acceptance criteria:
- Approved management access remains functional.
- Unapproved inbound traffic is denied.
- Required HTTP/HTTPS services remain reachable from authorized networks.
- Firewall rules are documented and managed through Ansible.

Status: Pending network design and approval.

### API-02 — HTTPS and TLS not implemented

Priority: High

Evidence:
- Nginx currently listens on HTTP port 80.
- No TLS certificate or HTTPS listener has been configured.
- api.example.com is a placeholder hostname.

Risk:
HTTP does not provide transport encryption or server identity validation.
Credentials, tokens, and application data would not be protected in transit
if sensitive traffic were sent over an untrusted network.

Recommendation:
- Confirm the real DNS name and ownership.
- Define the certificate authority and certificate renewal process.
- Configure TLS and HTTPS.
- Redirect HTTP to HTTPS where appropriate.
- Define minimum TLS versions and secure cipher policy.
- Protect private keys and prevent them from entering Git.

Acceptance criteria:
- The approved hostname resolves to the intended endpoint.
- HTTPS certificate validation succeeds.
- HTTP is redirected or restricted according to the approved design.
- Certificate renewal and expiry monitoring are documented.

Status: Pending hostname, DNS, and certificate decisions.

### API-03 — No application authentication or authorization

Priority: High for production APIs

Evidence:
- The sample API exposes GET / and GET /health.
- No authentication or authorization mechanism is implemented.

Risk:
The sample application is suitable for laboratory validation but does not
demonstrate access control for business APIs.

Recommendation:
- Define authentication and authorization requirements per API.
- Select an approved identity provider or token-validation mechanism.
- Define service-to-service authentication where required.
- Avoid embedding credentials in container images or Compose files.
- Keep health endpoints appropriately scoped and avoid exposing sensitive
  operational information.

Acceptance criteria:
- Each production API has an approved authentication and authorization design.
- Unauthorized requests are rejected.
- Credentials and tokens are handled through an approved secret-management
  mechanism.

Status: Pending application requirements.

### API-04 — API-to-database connectivity not designed

Priority: High before deploying database-dependent APIs

Evidence:
- PostgreSQL, MySQL, and MariaDB bind to loopback on their respective VMs.
- No API-to-database connectivity test has been performed.

Risk:
Changing database listeners without a defined network policy could expose
database services more broadly than intended.

Recommendation:
- Identify which API projects require which database engines.
- Define the source address or network for each API-to-database connection.
- Restrict database listeners and firewall rules to approved API sources.
- Use database accounts with least-privilege permissions.
- Require encrypted database connections where supported and appropriate.
- Keep database credentials outside source control and container images.

Acceptance criteria:
- Only approved API hosts can reach the required database ports.
- Database authentication uses dedicated least-privilege accounts.
- Unnecessary database ports remain inaccessible.
- Connectivity and denial tests are documented.

Status: Pending integration and network design.

### API-05 — Historical MariaDB installation on PostgreSqlServer

Priority: Medium

Evidence:
- MariaDB was historically installed on PostgreSqlServer.
- The packages have been purged after backup.
- PostgreSQL remains online and appdb is preserved.
- MariaDB data remains under /var/lib/mysql.

Risk:
Residual data and configuration may cause confusion or consume disk space.
The retained backup has not been restore-tested.

Recommendation:
- Retain the backup and residual data until formally reviewed.
- Review remaining MariaDB-related packages and configuration.
- Do not run autoremove without reviewing its proposed package list.
- Delete residual data only after explicit approval.

Acceptance criteria:
- PostgreSqlServer runs only its intended database engine.
- PostgreSQL remains healthy.
- Backup retention or disposal is formally decided.
- No unrelated dependencies are removed.

Status: Package cleanup complete; residual-data review pending.

### API-06 — Custom Nginx log permissions inconsistent

Priority: Medium

Evidence:
- Standard Nginx access and error logs use www-data:adm with mode 0640.
- Custom API logs were observed as root:root with mode 0644.
- The Nginx logrotate policy covers *.log files.

Risk:
The custom log files have broader read permissions than the standard Nginx
logs. Access logs may contain sensitive request metadata.

Recommendation:
- Define consistent ownership and permissions for custom logs.
- Manage the policy through Ansible.
- Confirm logrotate creates rotated files with the intended ownership and mode.
- Review retention and access requirements.

Acceptance criteria:
- Custom logs follow the approved ownership and permission policy.
- Rotated logs preserve the intended policy.
- Nginx continues writing logs after rotation.

Status: Pending Ansible remediation.

### API-07 — Default container capabilities not explicitly dropped

Priority: Medium

Evidence:
- No additional capabilities are added.
- The default Docker capability set remains in place.

Risk:
The container retains capabilities that may not be required by the sample API.

Recommendation:
- Test dropping all Linux capabilities.
- Add back only capabilities proven necessary.
- Validate application startup, health checks, and normal operation.

Acceptance criteria:
- The sample API runs successfully with the minimum required capabilities.
- The Compose security policy is documented.

Status: Pending controlled testing.

### API-08 — Container image and dependency reproducibility

Priority: Medium

Evidence:
- Dockerfile uses the floating python:3.12-slim base-image tag.
- FastAPI and Uvicorn versions are pinned.
- Transitive Python dependencies are not fully locked.

Risk:
A future rebuild may retrieve different base-image or transitive dependency
versions, changing the resulting image and potentially introducing
unexpected vulnerabilities or incompatibilities.

Recommendation:
- Pin the base image by digest.
- Use a fully resolved dependency lock file.
- Define a controlled image update and vulnerability-review process.
- Rebuild and retest images before promotion.

Acceptance criteria:
- Builds use controlled base-image versions.
- Application dependencies are reproducible.
- Image updates are reviewed and tested.

Status: Pending build-hardening work.

### API-09 — Project files staged when deployment is disabled

Priority: Low

Evidence:
- Sample API files are copied to the API server by the API role.
- Deployment tasks are skipped when api_deploy_enabled is false.

Risk:
The variable name may lead operators to assume that no project files are
transferred when deployment is disabled.

Recommendation:
- Decide whether file staging should have a separate control variable.
- Document the distinction between staging and deployment.

Acceptance criteria:
- Variable behavior is explicit and documented.
- Check-mode and normal execution match the approved behavior.

Status: Pending design decision.

### API-10 — Container log rotation stress test outstanding

Priority: Medium

Evidence:
- Docker logging limits are configured.
- Actual rotation under sustained log generation has not been tested.

Risk:
Configuration validation alone does not prove that rotation behaves as
expected during sustained application logging.

Recommendation:
- Perform a controlled test in the laboratory.
- Generate sufficient test output to trigger rotation.
- Verify file count, size, compression, and continued logging.
- Avoid generating excessive disk usage.

Acceptance criteria:
- Rotation occurs at the configured size.
- Retained file count is within the configured limit.
- Compressed files are readable.
- The container continues logging after rotation.

Status: Pending test.

### API-11 — Container crash recovery test outstanding

Priority: Medium

Evidence:
- Restart policy is unless-stopped.
- A normal container restart was tested.
- Recovery after an unexpected process/container failure has not been tested.

Risk:
A configured restart policy does not by itself prove recovery behavior
under failure conditions.

Recommendation:
- Perform a controlled failure test in the laboratory.
- Verify Docker restarts the container as expected.
- Verify the API health endpoint recovers.
- Record recovery time and logs.

Acceptance criteria:
- The container returns to running and healthy state after the approved test.
- Nginx can reach the API after recovery.
- No persistent data or configuration is lost.

Status: Pending test.

## 6. Remediation order

The proposed order is:

1. Confirm network topology and authorized management source addresses.
2. Design and approve host firewall policy.
3. Confirm the production DNS name and TLS certificate approach.
4. Define API authentication and authorization requirements.
5. Design restricted API-to-database connectivity.
6. Correct Nginx custom log ownership and permissions through Ansible.
7. Test container capability reduction.
8. Improve image and dependency reproducibility.
9. Clarify API project staging behavior.
10. Perform container log rotation and crash-recovery tests.

Firewall and database network changes must not be made until the relevant
source networks, access requirements, and rollback procedures are known.

## 7. Change-control requirements

Before remediation:

- Inspect the current configuration.
- Record the proposed change and expected impact.
- Validate the Ansible syntax and target hosts.
- Use check mode where supported.
- Confirm backups and rollback steps.
- Obtain approval before applying changes.

After remediation:

- Verify service health.
- Verify expected network listeners.
- Test allowed and denied access.
- Run relevant application health checks.
- Check Ansible idempotency.
- Update the documentation and Git history.

No production changes are authorized by this document.

## 8. Overall assessment

The laboratory API platform has a working Docker runtime, a healthy sample
API, automated deployment controls, and an operational Nginx reverse proxy.

The sample container already applies several useful hardening controls,
including non-root execution, a read-only root filesystem, resource limits,
a temporary filesystem, and no-new-privileges.

However, the platform is not yet production-ready. The principal outstanding
items are host firewall policy, HTTPS/TLS, application authentication and
authorization, and a controlled API-to-database network design.

Additional hardening and operational tests are also required.

## 9. Milestone 4.6 status

Status: Assessment documented; remediation pending review and approval.

Completed:
- API server baseline inspection.
- Docker and container security inspection.
- Nginx reverse-proxy inspection.
- Database listener inspection.
- Historical MariaDB package cleanup and PostgreSQL verification.
- Security findings and remediation recommendations documented.

Outstanding:
- Review and approval of findings.
- Network and firewall design.
- TLS and DNS design.
- Authentication and authorization design.
- API-to-database connectivity design.
- Ansible remediation tasks.
- Container hardening and operational tests.
- Final validation and idempotency checks.
