# API Server Baseline and Sample Deployment

## 1. Objective

Prepare a dedicated API server to host internally developed APIs and
vendor-supplied APIs using Docker containers.

The platform uses Docker Engine and Docker Compose, managed through
Ansible. API projects are kept independent so that different applications
can use different languages and frameworks.

This milestone establishes the host infrastructure and validates the
deployment of a laboratory sample API.

## 2. Target server

| Property | Value |
|---|---|
| Ansible inventory host | `ApiServer` |
| Inventory group | `apiservers` |
| IP address | `192.168.174.133` |
| Operating system | Ubuntu Server 24.04 LTS |
| Remote user | `apiserver` |

## 3. Implemented infrastructure

The reusable Ansible role is located at `roles/api/` and is invoked by
`playbooks/api.yml`.

The role performs the following tasks:

- Validates operating system compatibility.
- Validates API role configuration.
- Installs Docker Engine and Docker Compose.
- Enables and starts the Docker service.
- Configures Docker container logging and log rotation.
- Creates the API project directory structure.
- Stages the sample API project.
- Verifies Docker Engine and Compose availability.
- Supports optional sample API deployment.

## 4. Directory structure

The role creates:

    /opt/apis/
    ├── internal/
    │   └── sample-api/
    │       ├── app/
    │       │   └── main.py
    │       ├── compose.yml
    │       ├── Dockerfile
    │       └── requirements.txt
    └── vendor/

Directory configuration:

- Owner: `root`
- Group: `root`
- Permissions: `0750`

The internal and vendor directories provide separate locations for
internally developed and vendor-supplied API projects.

Sample project files are staged from:

    api-projects/internal/sample-api/

## 5. Docker configuration

| Component | Configuration |
|---|---|
| Docker Engine | 29.1.3 |
| Docker Compose | 2.40.3 |
| Docker service | Active and enabled |
| Logging driver | `json-file` |
| Maximum log size | `10m` |
| Maximum log files | `3` |
| Log compression | Enabled |
| Docker daemon configuration | `/etc/docker/daemon.json` |

The logging policy limits container log growth through rotation.

## 6. Sample API application

A laboratory FastAPI application was created to validate the deployment
workflow.

Application:

- Framework: FastAPI
- Python image: `python:3.12-slim`
- Image tag: `server-automation/sample-api:1.0.0`
- Application server: Uvicorn
- Container user: `appuser`
- Container port: `8000`

Endpoints:

| Endpoint | Expected result |
|---|---|
| `/` | Application name, version and running status |
| `/health` | `{"status":"healthy"}` |

### 6.1 Container security and resource controls

The Compose project implements:

- Non-root container execution.
- Read-only root filesystem.
- Temporary filesystem at `/tmp`, limited to 16 MB.
- `noexec` and `nosuid` options on the temporary filesystem.
- Memory limit of 256 MB.
- CPU limit of 0.50.
- `no-new-privileges`.
- Restart policy `unless-stopped`.
- Container health check.
- Docker log rotation.

The published port is bound to:

    127.0.0.1:8000

The application is therefore not directly published on the API server's
external network interfaces. Reverse proxy integration remains a
separate implementation stage.

## 7. Ansible deployment automation

The sample deployment is controlled by:

    api_deploy_enabled

Default value:

    false

The sample project is staged by the API role, but deployment is skipped
unless explicitly enabled.

To deploy the sample API:

    ansible-playbook playbooks/api.yml \
      -e "api_deploy_enabled=true"

The deployment tasks:

1. Validate the Docker Compose configuration.
2. Build and deploy the Compose project using
   `community.docker.docker_compose_v2`.
3. Wait for the HTTP health endpoint to return status 200.

The deployment module uses:

- `state: present`
- `build: policy`
- `recreate: auto`
- `remove_orphans: false`

The controller has `community.docker` collection version 3.7.0.

The deployment was tested successfully. A subsequent execution
completed with `changed=0`, confirming idempotency for the tested
configuration.

## 8. Deployment validation results

| Verification | Result |
|---|---|
| Ansible syntax validation | Passed |
| Docker Compose configuration validation | Passed |
| Docker Engine | 29.1.3 |
| Docker Compose | 2.40.3 |
| Sample image build | Successful |
| Container startup | Successful |
| Container health status | Healthy |
| Root endpoint | HTTP 200 |
| Health endpoint | HTTP 200 |
| Container user | `appuser` |
| Read-only root filesystem | Enabled |
| Memory limit | 256 MB |
| CPU limit | 0.50 |
| Port binding | `127.0.0.1:8000` |
| Container restart test | Successful |
| Repeated Ansible deployment | `changed=0` |

The container was verified remotely on `ApiServer`, not on the
Ansible controller.

## 9. Scope boundaries and outstanding work

The following items are not yet implemented:

- Nginx reverse proxy configuration.
- TLS certificate installation and management.
- Firewall changes and external access configuration.
- API environment configuration and secrets management.
- Vendor API deployment and validation.
- Production image version and digest management.
- Application update, rollback and recovery procedures.
- Automated application testing and security scanning.
- Actual Docker log rotation stress testing.
- Validation of deployment behaviour after a container crash.

The sample API is a laboratory application and is not a production
service.

## 10. Next implementation stages

1. Establish Nginx as the API reverse proxy.
2. Configure API routing and upstream connectivity.
3. Plan and implement TLS.
4. Review firewall rules and permitted network access.
5. Define environment configuration and secrets handling.
6. Establish image versioning, update and rollback procedures.
7. Validate deployment of an additional independent API.
8. Test failure recovery, monitoring and logging.

Each stage must be validated in the lab before being considered ready
for production use.
