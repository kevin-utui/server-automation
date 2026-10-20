Security Baseline and Secret Management

**Project:** Server Automation Lab  
**Environment:** VMware lab — Ubuntu Server 24.04 LTS  
**Controller:** ansserver  
**Managed hosts:** AppServer, DataBaseServer  
**Status:** Implementation and validation passed; documentation and Git commit pending.

## 1. Objectives

- Establish a read-only security baseline for managed servers.
- Configure Ansible Vault password-file access.
- Keep the local Vault password file out of Git.
- Centralise shared encrypted lab variables.
- Configure host-specific privilege-escalation variables.
- Validate connectivity, Vault variable availability and privilege escalation.
- Record security findings without automatically changing server configuration.

## 2. Configuration implemented

### Ansible configuration

The project configuration includes:
- Inventory: `./inventory/hosts.yml`
- Host-key checking enabled.
- Connection timeout: 10 seconds.
- Python interpreter discovery: `auto_silent`.
- Vault password file: `~/.vault_pass`.
- SSH connection multiplexing enabled.

### Secret management

- Shared encrypted variables: `inventory/group_vars/all/vault.yml`
- AppServer variables: `inventory/host_vars/AppServer/vars.yml`
- AppServer encrypted variable file: `inventory/host_vars/AppServer/vault.yml`
- DataBaseServer variables: `inventory/host_vars/DataBaseServer/vars.yml`
- DataBaseServer encrypted variable file: `inventory/host_vars/DataBaseServer/vault.yml`

The host-specific variable files reference `vault_become_password`.
The host-specific Vault files use inline `!vault` encryption.
The shared Vault file is encrypted as a complete file.

The local Vault password file is `~/.vault_pass`. It must remain outside Git, with restrictive filesystem permissions. `.gitignore` now excludes `.vault_pass`.

Do not print decrypted Vault values or publish the local Vault password.

## 3. Security baseline playbook

Playbook: `playbooks/security_baseline.yml`

The playbook gathers and reports:
- Operating-system distribution and version.
- Kernel and Python interpreter.
- SSH service state.
- UFW and nftables service states.
- UFW status and firewall rules.
- Effective SSH security settings.
- Number of available package updates.

The playbook is observational. It does not enable firewalls, change SSH configuration or install updates.

## 4. Issues encountered and resolutions

### 4.1 Ansible Vault password-file configuration

**Issue:** Ansible needed a consistent way to access the Vault password during routine operations.

**Resolution:** Configured `vault_password_file = ~/.vault_pass` in `ansible.cfg` and added `.vault_pass` to `.gitignore`.

**Validation:** `ansible-config dump --only-changed` identified `/home/ansible/.vault_pass` as the effective Vault password file.

### 4.2 Privilege escalation

**Issue:** The lab needed to verify that the configured credentials permitted privileged tasks on both managed hosts.

**Resolution:** Configured `ansible_become_password` to reference `vault_become_password`.

**Validation:** The command `ansible all -b -m ansible.builtin.command -a 'id -u' -o` returned UID `0` on both hosts.

### 4.3 Host-specific Vault file inspection

**Issue:** Running `ansible-vault view` directly against each host-specific `vault.yml` returned `input is not vault encrypted data`.

**Cause:** These files use inline Vault encryption (`!vault`), rather than whole-file encryption.

**Resolution:** Inspected the file structure without exposing the encrypted payload and validated variable availability through Ansible.

**Validation:** A temporary assertion playbook confirmed that `vault_become_password` was defined and non-empty on both hosts.

### 4.4 Incorrect ad hoc assertion invocation

**Issue:** An attempt to invoke `ansible.builtin.assert` with `ansible` ad hoc command syntax failed with an extra-parameters error.

**Cause:** The `assert` module is a task module and is not suitable for that ad hoc invocation.

**Resolution:** Created `/tmp/validate_vault.yml` and ran it using `ansible-playbook`.

**Validation:** Both hosts passed the assertion. The temporary playbook was stored outside the project repository.

### 4.5 Duplicate host variable files

**Issue:** Root-level files `inventory/host_vars/AppServer.yml` and `inventory/host_vars/DataBaseServer.yml` contained plaintext privilege-escalation password assignments, duplicating the directory-based host variable configuration.

**Resolution:** Backed up the files outside the repository to `~/server-automation-review-backup/` with restrictive permissions, then removed the duplicates from the project.

**Control:** Do not restore these files to Git. Keep the backups outside the repository and handle them as sensitive material.

### 4.6 Secret exposure during inventory inspection

**Issue:** `ansible-inventory --host ... --yaml` displayed decrypted lab credential values.

**Resolution:** Stop using full inventory dumps when secrets are present. Use targeted validation that reports only whether a variable is defined or whether a task succeeds.

**Follow-up:** Keep lab credentials unique to the lab. Rotate any credentials reused outside it. Do not include secret values in logs, screenshots, documentation or Git.

## 5. Validation results

| Test | Result |
|---|---|
| Shared Vault file inspection with `ansible-vault view` | Passed |
| Host-specific Vault variable assertion | Passed on both hosts |
| Privilege escalation (`id -u`) | UID 0 on both hosts |
| Security baseline syntax check | Passed |
| Security baseline execution | Passed on both hosts |
| AppServer baseline recap | 9 OK, 0 changed, 0 unreachable, 0 failed |
| DataBaseServer baseline recap | 9 OK, 0 changed, 0 unreachable, 0 failed |
| `ansible-config dump --only-changed` | Correct project config and Vault password-file path |
| `git diff --cached --check` | Passed at the last staged review |

## 6. Baseline observations

Both hosts reported:
- Ubuntu 24.04.
- Kernel `6.8.0-147-generic`.
- Python interpreter `/usr/bin/python3`.
- SSH service active.
- UFW service unit active, but UFW status inactive.
- nftables service inactive.
- SSH effective settings: root login `without-password`, public-key authentication enabled, password authentication enabled, X11 forwarding enabled, empty passwords prohibited.
- 22 available package updates at the time of testing.

These observations are not automatic remediation instructions. Review the intended access model, firewall requirements and maintenance window before changing settings or applying updates.

## 7. Outstanding hardening actions

- Review firewall policy and required SSH access before enabling UFW.
- Assess whether SSH password authentication is required.
- Assess whether X11 forwarding is required.
- Review and schedule available package updates.
- Confirm that all credentials are lab-only and rotate any reused credentials.
- Avoid exposing decrypted inventory values in command output.
- Review whether shared and host-specific Vault variables are appropriately separated and consistently named.

## 8. Scope and acceptance criteria

Milestone 3 is considered technically validated when:
- Vault variable availability is confirmed without printing secret values.
- Both managed hosts support Ansible privilege escalation.
- The read-only security baseline completes with zero failures and zero unreachable hosts.
- Intended changes pass staged-diff and secret-handling review.
- Documentation is saved and the intended files are committed.
