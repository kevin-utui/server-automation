# Redis Ansible Role

## 1. Purpose

Provides a reusable Redis Server baseline for Ubuntu Server 24.04 and newer.

Redis is managed independently through the `redis` inventory group and
`playbooks/redis.yml`.

## 2. Architecture

| Component | Configuration |
|---|---|
| Inventory group | redis |
| Managed host | RedisServer |
| IP address | 192.168.174.134 |
| Operating system | Ubuntu Server 24.04 |
| Service | redis-server |
| Port | 6379 |
| Deployment playbook | playbooks/redis.yml |
| Acceptance playbook | playbooks/redis_acceptance.yml |

## 3. Security

- Authentication is managed through Ansible Vault.
- Password length requirement: at least 32 characters.
- Listening restricted to 127.0.0.1 and ::1.
- Protected mode enabled.
- Redis configuration permissions: root:redis, mode 0640.
- Authentication task uses no_log.

## 4. Persistence and memory

- RDB snapshots enabled.
- AOF persistence enabled.
- AOF fsync policy: everysec.
- Memory limit: 256 MB.
- Memory policy: noeviction.

## 5. Deployment

Run:

    ansible-playbook playbooks/redis.yml --limit RedisServer

## 6. Validation evidence

| Test | Result |
|---|---|
| Installation | Passed |
| Service enabled and active | Passed |
| Authentication enforcement | Passed |
| Authenticated PING | PONG |
| Loopback-only listening | Passed |
| RDB persistence | Passed |
| AOF enabled | Passed |
| Basic SET, GET and DEL | Passed |
| RDB restart recovery | Passed |
| Idempotency | Passed, changed=0 |
| Recent journal error/warning check | No matches |

The recovery test forced an RDB snapshot, restarted Redis and confirmed
that a temporary test key was recovered successfully.

A separate isolated AOF recovery test has not yet been performed.
AOF is enabled and its runtime write status reports ok.

## 7. Idempotency

The second deployment run completed with:

    ok=22 changed=0 unreachable=0 failed=0

## 8. Operational considerations

- The 256 MB memory limit is an initial lab setting.
- noeviction causes write operations to fail when the memory limit is reached.
- Monitor memory, disk utilisation, persistence status and service logs.
- Redis is currently intended for local access only.
- Lab validation does not establish production readiness.

## 9. Current status

Redis deployment, security configuration, runtime validation,
idempotency and RDB restart recovery have passed in the VMware lab.
