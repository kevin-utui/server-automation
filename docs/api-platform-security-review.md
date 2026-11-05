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
- The custom API error log and an older rotated access log initially had
  inconsistent ownership and permissions.
- Ubuntu's existing Nginx logrotate policy covers /var/log/nginx/*.log and
  creates new logs with mode 0640, owner www-data, and group adm.

Remediation:
- Updated the Ansible Nginx role to discover active and rotated custom API
  log files and enforce www-data:adm ownership with mode 0640.
- Applied the role to ApiServer.
- Confirmed the second Ansible execution returned changed=0.
- Forced a controlled Nginx log rotation using the existing Ubuntu policy.
- Verified that the new active log and archived logs retained the intended
  ownership and permissions.
- Generated another API health request after rotation and confirmed HTTP 200.
- Verified that the new active access log received the request and Nginx
  remained active.

Acceptance criteria:
- Custom logs follow the approved ownership and permission policy: PASS.
- Rotated logs preserve the intended policy: PASS.
- Nginx continues writing logs after rotation: PASS.
- Ansible deployment is idempotent: PASS.

Status: Complete — remediation and acceptance testing passed.

### API-07 — Default container capabilities not explicitly dropped

Priority: Medium

Evidence:
- The sample API runs as the non-root user appuser.
- The container is not privileged and uses a read-only root filesystem.
- Before remediation, Docker's default capabilities were not explicitly
  restricted.
- The application uses FastAPI and Uvicorn, listening on port 8000.
  No application requirement for additional Linux capabilities was identified.

Remediation:
- Updated the sample API Compose configuration with cap_drop: ALL.
- Staged the updated configuration on ApiServer.
- Validated the effective Compose configuration before deployment.
- Recreated the sample API container with all Linux capabilities dropped.
- Confirmed CapDrop contains ALL and CapAdd is empty.
- Confirmed the container remains non-privileged and runs as appuser.
- Confirmed the read-only root filesystem remains enabled.
- Verified the container is running and healthy, with RestartCount 0.
- Verified the direct API health endpoint returns HTTP 200.
- Verified the Nginx reverse-proxy health endpoint returns HTTP 200.
- Confirmed application startup and health requests in the container logs.
- Repeated the Ansible deployment and confirmed changed=0.

Acceptance criteria:
- All Linux capabilities are dropped: PASS.
- No additional capabilities are added: PASS.
- Application starts and remains healthy: PASS.
- Direct API health endpoint returns HTTP 200: PASS.
- Nginx reverse proxy remains functional: PASS.
- Ansible deployment is idempotent: PASS.

Status: Complete — remediation and acceptance testing passed.

### API-08 — Container image and dependency reproducibility

Priority: Medium

Evidence:
- The original Dockerfile used the floating python:3.12-slim base-image tag.
- FastAPI and Uvicorn were pinned, but transitive Python dependencies
  were not fully locked.
- The base image is now pinned to the verified linux/amd64 manifest digest:
  sha256:05a994d2344eb364cc186910f4fc8786a38215f39f00d0acc25bff33a08f4177.
- A requirements.lock file was generated using pip-tools 7.6.2.
- The lock file contains 18 resolved Python packages with SHA-256 hashes
  (604 package hash entries).
- The Dockerfile installs dependencies from requirements.lock using
  pip's --require-hashes option.
- A pip dry-run with --require-hashes and --only-binary=:all: completed
  successfully before the Docker build.
- A fresh candidate image was built successfully using the pinned base
  image and hash-locked dependencies.
- The candidate container ran as appuser with a read-only root filesystem,
  256 MiB memory limit, 0.5 CPU limit, all Linux capabilities dropped,
  no-new-privileges enabled, and localhost-only port publication.
- Candidate API tests passed:
  - /health returned HTTP 200.
  - / returned HTTP 200.
- The candidate's installed package versions matched the locked dependency
  set.
- The original sample-api container was not replaced or redeployed.
  Its container and image IDs remained unchanged, it stayed healthy,
  and both direct and Nginx-proxied health checks returned HTTP 200.

Risk:
A future rebuild using uncontrolled base-image or dependency versions may
produce a different image, potentially introducing vulnerabilities or
incompatibilities.

Recommendation:
- Keep the base image pinned by digest and application dependencies
  hash-locked.
- Review and test base-image and dependency updates before promotion.
- Establish an ongoing vulnerability-review and image-update process.
- Rebuild and retest candidate images before replacing the running service.

Acceptance criteria:
- Builds use a controlled base-image version: PASS.
- Application dependencies are reproducible and hash-verified: PASS.
- A fresh candidate image builds and passes runtime endpoint tests: PASS.
- The existing service remains unaffected during candidate validation: PASS.
- Ongoing image-update and vulnerability-review governance remains
  an operational responsibility.

Implementation notes:
- The pinned base-image digest is for linux/amd64 and must be reviewed
  separately if the deployment architecture changes.
- The Docker build completed using Docker's legacy builder. The builder
  emitted a deprecation warning because Buildx is not installed; this
  did not prevent the candidate build or validation.
- The candidate was tested separately on localhost port 18000.
  It was not promoted to the sample-api:1.0.0 production-like lab service.

Status: Complete — current image and dependency reproducibility
hardening implemented and candidate validation passed. Ongoing
update and vulnerability-review governance remains operational work.

### API-09 — Project files staged when deployment is disabled

Priority: Low

Evidence:
- Sample API files are copied to the API server by the API role.
- Deployment tasks are skipped when api_deploy_enabled is false.

Risk:
The variable name may lead operators to assume that no project files are
transferred when deployment is disabled.

Approved design decision:
- Retain project-file staging as an independent preparation operation.
- `api_deploy_enabled` controls only application deployment.
- Its default remains `false`.
- When disabled, the role may install/configure Docker, create project
  directories and stage project files, but does not build or start the
  sample API container.
- When enabled, the role validates Compose configuration, builds/deploys
  the application and checks its health endpoint.
- No additional staging variable is required.

Acceptance criteria:
- Variable behavior is explicit and documented: PASS.
- Deployment remains disabled by default: PASS.
- Deployment tasks are conditional on `api_deploy_enabled`: PASS.
- Check-mode and normal execution behavior are documented separately;
  check-mode is not treated as proof of deployment.

Validation evidence:
- `roles/api/defaults/main.yml` sets `api_deploy_enabled: false`.
- `roles/api/tasks/main.yml` stages project files before the conditional
  deployment include.
- `roles/api/tasks/deploy_sample.yml` contains Compose validation,
  deployment and health-check tasks.

Status: Complete — design decision documented; no code change required.

### API-10 — Container log rotation stress test

Priority: Medium

Evidence:
- Docker uses the json-file logging driver with a 10 MB maximum
  file size, a maximum of three retained files, and compression enabled.
- A controlled disposable-container rotation test passed.
- A sustained logging test was performed against the actual sample-api
  container using 4,200 HTTP requests with 8,000-character query strings.
- All 4,200 requests returned HTTP 200, with zero failed requests.
  The test ran for approximately 71 seconds at 59.21 requests per second.
- Docker retained exactly three log files: one active file and two
  compressed archives.
- The two compressed archives had original uncompressed sizes of
  10,001,481 bytes and 10,001,594 bytes respectively.
- Compression reduced the archives to 22,052 bytes and 22,063 bytes.
- Docker log retrieval remained functional after rotation.
- The API continued returning HTTP 200 after rotation. The container
  remained running and healthy.
- Approximately 12 GB of disk space remained available after the test.

Risk:
The configured logging policy has been validated under controlled
sustained application logging. This test does not represent every
possible production logging workload.

Recommendation:
- Retain the configured Docker logging limits.
- Monitor container log volume and host disk capacity during operation.
- Reassess the limits if application logging volume changes materially.

Acceptance criteria:
- Rotation occurs at approximately the configured 10 MB threshold: PASS.
- Retained file count does not exceed three: PASS.
- Rotated archives are compressed and readable: PASS.
- Docker log retrieval remains functional after rotation: PASS.
- The API continues operating and logging after rotation: PASS.
- Sustained test traffic completes without failed requests: PASS.

Status: Complete — sustained logging stress test passed against the
actual sample-api container.

### API-11 — Container crash recovery

Priority: Medium

Evidence:
- The sample API uses the Docker restart policy unless-stopped.
- A controlled disposable-container test previously confirmed that Docker
  restarts a container after its main process exits with code 1.
- The actual sample-api container was subsequently tested.
- Before the test, the container was running and healthy, with RestartCount 0.
- Uvicorn was sent SIGTERM as the configured non-root application user
  (UID 999), causing the main application process to shut down gracefully.
- Docker automatically restarted the actual sample-api container.
- RestartCount increased from 0 to 1.
- The container returned to running and healthy status.
- The measured recovery time was 9 seconds.
- Application logs confirmed Uvicorn shutdown followed by a fresh startup.
- The direct API health endpoint returned HTTP 200 after recovery.
- The Nginx reverse-proxy health endpoint also returned HTTP 200.
- The restart policy remained unless-stopped.

Test limitation:
- An earlier SIGKILL issued through the Docker CLI left the container
  stopped and did not demonstrate automatic recovery. The container was
  manually started and restored before the successful process-level test.
- The successful SIGTERM test is the acceptance evidence for this finding.

Acceptance criteria:
- The actual sample API recovers after application-process termination: PASS.
- Docker automatically restarts the container: PASS.
- The container returns to running and healthy status: PASS.
- Recovery completes within the observed 9 seconds: PASS.
- Nginx can reach the API after recovery: PASS.
- No application configuration or persistent data was changed: PASS.

Status: Complete — actual sample API crash-recovery testing passed.

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
