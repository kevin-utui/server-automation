# Application Server Role

## Purpose

Prepare Ubuntu application servers with Docker Engine and the Docker Compose
plugin. The role validates the operating system, installs the required
packages, ensures Docker is enabled and running, and verifies both CLI tools.

Compose deployment and environment-file management are disabled by default.
This role does not currently deploy application containers.

## Requirements

- Ansible Core with the built-in modules used by the role.
- SSH access to the target host.
- Privilege escalation through `become`.
- A supported Ubuntu installation and access to package repositories.

## Default Variables

| Variable | Default | Purpose |
|---|---|---|
| `app_supported_os` | `Ubuntu` | Expected operating system |
| `app_minimum_os_version` | `"24.04"` | Minimum supported version |
| `app_docker_packages` | `docker.io`, `docker-compose-v2` | Packages to install |
| `app_docker_service` | `docker` | Docker service name |
| `app_compose_deploy_enabled` | `false` | Enable Compose configuration validation |
| `app_compose_project_name` | `application` | Compose project name |
| `app_compose_project_dir` | `/opt/application` | Project directory |
| `app_compose_file` | `compose.yml` | Compose filename |
| `app_env_file_enabled` | `false` | Enable environment-file management |
| `app_env_file_path` | `/opt/application/.env` | Environment-file path |
| `app_env_file_mode` | `"0600"` | Required file permissions |
| `app_env_file_owner` | `root` | File owner |
| `app_env_file_group` | `root` | File group |
| `app_env_vars` | `{}` | Environment values |
| `app_compose_project_dir_mode` | `"0750"` | Project directory permissions |

The variables `app_container_log_driver`, `app_container_log_max_size`,
and `app_container_log_max_file` are defined as defaults but are not currently
applied to containers.

## Environment File Safety

Environment-file creation requires an absolute path, mode `0600`, and a
non-empty mapping of environment values. Variable names and values are
validated, and sensitive task output is suppressed.

Environment-file serialization has not yet been validated for all special
characters. Keep this feature disabled until serialization has been corrected
and tested. Store secrets in Ansible Vault, not in plaintext defaults.

## Compose Validation

When enabled, the role validates Compose settings, requires an existing
Compose file, and runs `docker compose config --quiet`. This validates the
configuration without deploying containers.

Actual Compose deployment is not implemented by this role.

## Example Playbook

```yaml
---
- name: Prepare application servers
  hosts: applications
  become: true
  gather_facts: true
  roles:
    - role: app
```

## Validation

The lab AppServer has been tested with this role. The recorded run confirmed
Docker and Compose availability, with `changed=0` and `failed=0`.
Environment-file and Compose validation tasks were skipped because both
features were disabled.

## Dependencies

No external roles are currently declared.

## Limitations

- Application containers are not deployed.
- Environment-file serialization requires further testing.
- Container logging defaults are not applied.
- Production deployment has not been validated by this role.
