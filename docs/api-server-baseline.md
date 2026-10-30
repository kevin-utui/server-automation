# API Server Baseline

## 1. Objective

Prepare a dedicated API server to host internally developed APIs and
vendor-supplied APIs using Docker containers.

This baseline establishes the host infrastructure. It does not deploy
API applications.

## 2. Target server

| Property | Value |
|---|---|
| Ansible inventory host | `ApiServer` |
| Inventory group | `apiservers` |
| IP address | `192.168.174.133` |
| Operating system | Ubuntu Server 24.04 LTS |
| Remote user | `apiserver` |

## 3. Implemented configuration

The reusable Ansible role is located at `roles/api/` and is invoked by
`playbooks/api.yml`.

The role performs the following tasks:

- Validates operating system compatibility.
- Validates API role configuration.
- Installs Docker Engine and Docker Compose.
- Enables and starts the Docker service.
- Creates the API project directory structure.
- Verifies Docker Engine and Compose availability.

## 4. Directory structure

The role creates:

    /opt/apis/
    ├── internal/
    └── vendor/

Directory configuration:

- Owner: `root`
- Group: `root`
- Permissions: `0750`

The directories provide separate locations for internally developed
and vendor-supplied API projects.

## 5. Deployment results

The baseline was successfully deployed on `ApiServer`.

| Component | Verified result |
|---|---|
| Docker Engine | 29.1.3 |
| Docker Compose | 2.40.3 |
| Docker service | Active |
| Docker service enabled at boot | Yes |
| API base directory | `/opt/apis` |
| Internal API directory | `/opt/apis/internal` |
| Vendor API directory | `/opt/apis/vendor` |
| Directory ownership | `root:root` |
| Directory permissions | `0750` |
| Running API containers | None |

A second execution of the API playbook completed with
`changed=0`, confirming idempotency at the time of validation.

## 6. Scope boundaries

The current baseline does not include:

- API application or vendor container deployment.
- Docker Compose project definitions.
- API image version management.
- Application environment files or secrets.
- Container logging policies.
- Nginx reverse proxy configuration.
- TLS certificate installation or management.
- Firewall changes or external access configuration.
- Database installation or migration.

No API application has been deployed as part of this milestone.

## 7. Next implementation stages

The following work remains for the API platform:

1. Define and validate per-API Docker Compose projects.
2. Establish image versioning and update procedures.
3. Define environment configuration and secrets handling.
4. Implement and validate container logging policies.
5. Configure Nginx as the reverse proxy.
6. Plan and implement TLS.
7. Review firewall rules and permitted network access.
8. Deploy a test API and validate routing, connectivity, and rollback.

Each stage should be tested in the lab before being considered ready
for production use.
