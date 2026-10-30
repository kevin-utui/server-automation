# Automated Security Updates

## 1. Objective

Configure a conservative, repeatable policy for automated security updates
on the Server Automation lab's Ubuntu Server hosts:

Original Stage 1 target hosts:

- AppServer
- DataBaseServer

> Historical inventory note: `DataBaseServer` was the original database host name. The current database inventory contains `PostgreSqlServer`, `MySQLServer`, and `MariaDBServer`. The original validation results below apply to the Stage 1 hosts listed above; they do not establish security-updates validation on the current database hosts.

Configuration is managed by Ansible through the `common` role.

## 2. Scope

The `playbooks/security_updates.yml` playbook imports
`roles/common/tasks/security_updates.yml` for all inventory hosts.

The configuration:

- Installs `unattended-upgrades`, `apt-listchanges`, and `needrestart`.
- Enables daily APT package-list updates.
- Enables scheduled unattended upgrades.
- Restricts allowed upgrade origins to security and ESM security origins.
- Explicitly disables automatic reboots.
- Disables automatic removal of unused kernel packages and dependencies.
- Configures `apt-listchanges` for non-interactive operation.
- Configures `needrestart` to report restart requirements without
  automatically restarting services.

This playbook configures the policy. It does not run a general full-system
upgrade or deliberately reboot the lab hosts.

## 3. Files

- `roles/common/defaults/main.yml`
  - Security-update feature flag, package list, periodic APT configuration,
    and `needrestart` restart mode.
- `roles/common/tasks/security_updates.yml`
  - Tasks that install packages and manage the host configuration.
- `roles/common/handlers/main.yml`
  - Runs `unattended-upgrade --dry-run --debug` when notified by relevant
    configuration changes.
- `playbooks/security_updates.yml`
  - Entry point for applying the configuration.

Managed host configuration includes:

- `/etc/apt/apt.conf.d/20auto-upgrades`
- `/etc/apt/apt.conf.d/52server-automation-unattended`
- `/etc/apt/listchanges.conf`
- `/etc/needrestart/needrestart.conf`
- `/etc/apt/apt.conf.d/50unattended-upgrades` (the allowed base-release
  origin entry is removed).

## 4. Update and reboot policy

The effective periodic APT settings are:

    APT::Periodic::Update-Package-Lists "1";
    APT::Periodic::Unattended-Upgrade "1";

The managed unattended-upgrades settings explicitly specify:

    Unattended-Upgrade::Automatic-Reboot "false";
    Unattended-Upgrade::Remove-Unused-Kernel-Packages "false";
    Unattended-Upgrade::Remove-Unused-Dependencies "false";

Automatic reboot and automatic unused-package cleanup are therefore
disabled by this configuration. Service restart requirements are reported
by `needrestart`; service restarts must be assessed and handled separately.

## 5. Security-origin limitation

The allowed origins retain the Ubuntu security origin and the ESM Apps and
ESM Infrastructure security origins. The base release origin is removed;
regular updates and backports remain excluded.

This is a conservative policy, but it can prevent some security updates
from being installed automatically when they require dependencies available
only from a non-security pocket. The dry-run result must therefore not be
interpreted as proof that every possible security update is installable.
Review the package policy and pending updates periodically.

## 6. Validation performed

The following checks completed successfully on the original Stage 1
hosts, `AppServer` and `DataBaseServer`:

- The required packages were installed and their versions were queried.
- `20auto-upgrades` contained both periodic settings set to `1`.
- The managed configuration set automatic reboot and unused-package removal
  to `false`.
- The allowed-origins configuration retained security and ESM security
  origins and excluded the base release origin.
- `apt-daily.timer` and `apt-daily-upgrade.timer` were enabled.
- `needrestart` was configured with restart mode `l`.
- `unattended-upgrade --dry-run` returned exit code 0 on both hosts.
- `apt-config dump` confirmed the effective periodic and reboot policies.
- A second run of `playbooks/security_updates.yml` was idempotent:
  - AppServer: `changed=0`, `failed=0`, `unreachable=0`
  - DataBaseServer: `changed=0`, `failed=0`, `unreachable=0`

## 7. Operational cautions

- A successful dry run validates that the command can execute; it does not
  guarantee that all security updates are available or installable.
- Automatic reboots are disabled. Plan and approve any required reboot
  through the normal maintenance process.
- Review unattended-upgrades logs and pending updates as part of routine
  maintenance.
- Test future policy changes with Ansible check mode and review the diff
  before applying them.

## 8. Acceptance criteria

- [x] Required packages installed on both hosts.
- [x] Daily package-list updates and unattended upgrades enabled.
- [x] Automatic reboot disabled.
- [x] Automatic removal of unused packages disabled.
- [x] Security-origin policy configured.
- [x] Dry-run commands return exit code 0 on both hosts.
- [x] Reapplying the playbook results in zero changes.
- [ ] Documentation reviewed and committed to Git.
