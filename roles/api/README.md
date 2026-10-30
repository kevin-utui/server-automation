# API Server Preparation Role

## Description

The `api` role prepares Ubuntu servers to host internally developed
and externally supplied APIs using Docker containers.

It installs Docker Engine and Docker Compose, ensures the Docker
service is enabled and running, creates the API project directory
structure, and verifies the installed Docker tools.

This role prepares host infrastructure. It does not deploy API
applications or vendor containers.

## Requirements

- Ubuntu 24.04 LTS or later.
- SSH connectivity to the target host.
- Privilege escalation (`become: true`).
- Access to configured Ubuntu package repositories.

## What the role configures

1. Validates the operating system.
2. Validates role configuration.
3. Installs Docker Engine and Docker Compose.
4. Enables and starts Docker.
5. Creates API project directories.
6. Verifies Docker Engine and Compose availability.

## Directory structure

The default structure is:

    /opt/apis/
    ├── internal/
    └── vendor/

Both category directories use root:root ownership and mode 0750.

Individual API projects can later be organised under the relevant category.

## Role variables

| Variable | Default | Description |
|---|---|---|
| `api_supported_os` | `Ubuntu` | Supported operating system |
| `api_minimum_os_version` | `24.04` | Minimum Ubuntu version |
| `api_docker_packages` | `docker.io`, `docker-compose-v2` | Docker packages |
| `api_docker_service` | `docker` | Docker service |
| `api_base_dir` | `/opt/apis` | API base directory |
| `api_project_categories` | `internal`, `vendor` | Project categories |
| `api_directory_owner` | `root` | Directory owner |
| `api_directory_group` | `root` | Directory group |
| `api_base_dir_mode` | `0750` | Base directory permissions |
| `api_category_dir_mode` | `0750` | Category directory permissions |

## Security and operational notes

- Docker is enabled and started by this role.
- The role does not add users to the Docker group.
- Docker administration remains subject to privilege controls.
- API containers are not deployed.
- No public container ports are configured.
- Nginx, TLS termination, firewall rules, and API routing are not
  configured by this role.
- Container logging policies are not configured by this role.
- No application secrets or vendor credentials are managed here.
- The role does not modify database servers.

Docker group membership can effectively grant root-level control
over the host.

## Dependencies

No other Ansible roles are required.

## Example playbook

The API role is invoked through `playbooks/api.yml`:

    ---
    - name: Prepare API servers
      hosts: apiservers
      become: true
      gather_facts: true

      roles:
        - role: api

Execute with:

    ansible-playbook playbooks/api.yml --limit ApiServer

## Validation

The role validates:

- Operating system compatibility.
- Role configuration values.
- Docker Engine availability.
- Docker Compose availability.

A successful second execution should report `changed=0`,
provided the host configuration has not changed.

## Future scope

The following capabilities are outside the current baseline:

1. API container deployment and lifecycle management.
2. Per-project Docker Compose definitions.
3. Container image version management.
4. Environment configuration and secrets management.
5. Container logging policies.
6. Nginx reverse proxy and TLS configuration.
7. Firewall and external access controls.

### Deployment verification

The API server baseline was deployed and verified on `ApiServer`.

- Docker Engine: 29.1.3.
- Docker Compose: 2.40.3.
- Docker service: enabled and active.
- API base directory: `/opt/apis`.
- Project directories: `/opt/apis/internal` and `/opt/apis/vendor`.
- Directory ownership: `root:root`.
- Directory permissions: `0750`.
- No API containers were deployed as part of this baseline.
- A second Ansible execution completed with `changed=0`.

These results confirm the infrastructure baseline only. They do not
validate API application deployment, reverse proxy, TLS, or external
connectivity.
