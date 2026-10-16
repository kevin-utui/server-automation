# Server Automation Lab

## Purpose

A VMware-based lab for developing, testing and documenting
Ansible automation for database, application and API servers.

## Infrastructure

| Host | Role | IP address |
|---|---|---|
| ansserver | Ansible controller | 192.168.174.128 |
| AppServer | Application server | 192.168.174.129 |
| DataBaseServer | Database server | 192.168.174.130 |

## Project structure

- inventory/: managed hosts and groups
- playbooks/: automation playbooks
- group_vars/: group-level variables
- host_vars/: host-specific variables
- roles/: reusable automation roles
- files/: static files
- templates/: Jinja2 templates
- reports/: generated reports
- docs/: technical documentation

## Safety principles

- Test changes in the lab before considering production use.
- Use Ansible Vault for sensitive variables.
- Validate playbooks before execution.
- Keep configuration changes under version control.
- Never commit private keys or passwords.
