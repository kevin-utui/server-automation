Stage 1: Common OS Baseline

> Historical inventory note: The original database host name was `DataBaseServer`. Following the database-host separation, its current inventory name is `PostgreSqlServer`.

## 1. Objective

Implement and validate a reusable Ansible common role for the
Ubuntu Server lab hosts.

## 2. Target hosts

| Inventory host | Address | SSH user |
|---|---|---|
| AppServer | 192.168.174.129 | application |
| DataBaseServer | 192.168.174.130 | database |

## 3. Implemented configuration

- Ansible role discovery configured with `roles_path = ./roles`.
- Base administration packages installed.
- System timezone configured as `Africa/Maputo`.
- Chrony installed, enabled, and running.
- Existing `systemd-timesyncd` replaced by Chrony through package
  dependency resolution.
- Playbook created at `playbooks/os_baseline.yml`.
- Role defaults and tasks implemented in `roles/common/`.

## 4. Installed packages

The following packages were verified on both hosts:

- curl
- ca-certificates
- gnupg
- rsync
- git
- vim
- htop
- lsof
- tcpdump
- dnsutils
- chrony

## 5. Validation evidence

### Role discovery

The initial syntax check failed because Ansible could not locate
the `common` role.

Resolution: configured `roles_path = ./roles` in `ansible.cfg`.

The effective role path was verified as:

`/home/ansible/server-automation/roles`

### Connectivity and privilege escalation

- Ansible ping succeeded on AppServer and DataBaseServer.
- Privilege escalation returned `root` on both hosts.

### Check mode

The initial check-mode run attempted to manage Chrony before
the package was installed. The service task failed because
Chrony was not yet present.

Resolution: added a package-state check and conditioned service
management on Chrony being installed. In check mode, the service
task is skipped when package installation is only simulated.

The subsequent syntax check and check-mode preview completed
without failures.

### Time synchronisation

Both hosts reported:

- Timezone: `Africa/Maputo`
- Chrony service: active
- Chrony enabled: enabled
- Leap status: Normal

Chrony reported valid NTP references and very small system-time
offsets during verification.

### Package verification

All 11 requested packages were listed with installed versions
on both hosts.

An earlier package-verification command returned blank output
because the controller shell expanded the package-format
variable before remote execution. The check was corrected using
`dpkg-query -W` without a shell format string.

### Idempotency

The final execution of `playbooks/os_baseline.yml` reported:

AppServer:
- ok=6
- changed=0
- unreachable=0
- failed=0

DataBaseServer:
- ok=6
- changed=0
- unreachable=0
- failed=0

The role is idempotent for the implemented configuration.

## 6. Scope limitations

This stage does not implement:

- unattended security updates
- apt-listchanges or needrestart configuration
- AppArmor or auditd policy
- persistent journald or log rotation configuration
- SSH hardening
- firewall rules or Fail2ban
- database, application, API, monitoring, or backup roles

These will be addressed in subsequent stages after validation
and review of the relevant settings.

## 7. Security and operational notes

- This work targets the disposable lab hosts, not production.
- SSH and firewall changes remain deferred until recovery
  safeguards are reviewed.
- `ansible.cfg.bak` is intentionally excluded from version control.
- No secrets or decrypted Vault values are included in this document.

## 8. Completion criteria

- [x] Role discovery works.
- [x] Playbook syntax check passes.
- [x] Both hosts are reachable.
- [x] Privilege escalation works.
- [x] Required packages are installed.
- [x] Timezone is Africa/Maputo.
- [x] Chrony is active and enabled.
- [x] Check-mode preview completes without failures.
- [x] Final idempotency check reports zero changes and failures.
