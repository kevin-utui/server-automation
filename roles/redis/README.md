# Redis Ansible Role

## Description

Installs and configures Redis Server on Ubuntu Server 24.04 and newer.

The role manages authentication, loopback-only network binding,
protected mode, persistence, memory limits, logging, service state
and data directory permissions.

## Requirements

- Ubuntu Server 24.04 or newer.
- Ansible.
- Redis credentials configured through Ansible Vault.
- A managed host with sudo privileges.

## Role variables

See `defaults/main.yml` for configurable defaults.

Important variables include:

- `redis_bind_address`
- `redis_port`
- `redis_protected_mode`
- `redis_auth_password`
- `redis_save_rules`
- `redis_appendonly`
- `redis_appendfsync`
- `redis_maxmemory`
- `redis_maxmemory_policy`
- `redis_logfile`
- `redis_dir`

The Redis authentication password is supplied through
`vault_redis_auth_password` in Ansible Vault.

## Dependencies

No external Ansible roles are required.

## Example playbook

    ---
    - name: Configure Redis infrastructure
      hosts: redis
      become: true
      gather_facts: true
      roles:
        - redis

## Deployment

    ansible-playbook playbooks/redis.yml --limit RedisServer

## Acceptance test

    ansible-playbook playbooks/redis_acceptance.yml --limit RedisServer

See `docs/redis-role.md` for configuration details and validation evidence.

## License

BSD
