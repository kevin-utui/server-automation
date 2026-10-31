# Nginx Reverse Proxy — API Server

## 1. Purpose

This document describes the Ansible-managed Nginx reverse proxy
implemented on the API server as part of Milestone 4.5 of the
Server Automation Lab.

Nginx provides the HTTP entry point for API services hosted in
Docker containers on the API server.

## 2. Environment

| Component | Configuration |
|---|---|
| Operating system | Ubuntu 24.04.5 LTS |
| API server | ApiServer |
| API server IP | 192.168.174.133 |
| Nginx version | 1.24.0 |
| HTTP listener | TCP port 80 |
| Server name | api.example.com |
| Backend address | 127.0.0.1:8000 |
| Backend application | FastAPI Sample API |
| Backend deployment | Docker Compose |

The hostname api.example.com is a laboratory placeholder.
Public DNS configuration is not part of this implementation.

## 3. Architecture

The request flow is:

Client
  -> Nginx on ApiServer (TCP port 80)
  -> FastAPI container (127.0.0.1:8000)

Nginx forwards incoming HTTP requests to the local API container.

The FastAPI container remains bound to the loopback interface.
Its application port is not directly exposed on the server's
network interfaces.

## 4. Ansible implementation

The Nginx configuration is managed through a dedicated reusable role.

Role structure:

- roles/nginx/defaults/main.yml
- roles/nginx/handlers/main.yml
- roles/nginx/tasks/main.yml
- roles/nginx/templates/api-reverse-proxy.conf.j2

Deployment playbook:

- playbooks/nginx.yml

The playbook targets the apiservers inventory group and uses
privilege escalation.

## 5. Configuration variables

| Variable | Default | Purpose |
|---|---|---|
| nginx_package_name | nginx | Ubuntu package |
| nginx_service_name | nginx | System service |
| nginx_api_server_name | api.example.com | HTTP virtual host |
| nginx_api_listen_port | 80 | HTTP listener |
| nginx_api_backend_host | 127.0.0.1 | Backend address |
| nginx_api_backend_port | 8000 | Backend port |
| nginx_api_disable_default_site | true | Disable default site |
| nginx_api_proxy_connect_timeout | 5s | Backend connection timeout |
| nginx_api_proxy_read_timeout | 60s | Backend read timeout |
| nginx_api_proxy_send_timeout | 60s | Backend send timeout |

## 6. Nginx configuration

The Ansible template generates:

/etc/nginx/sites-available/api-reverse-proxy.conf

The enabled site is:

/etc/nginx/sites-enabled/api-reverse-proxy.conf

The configuration:

- Listens on IPv4 and IPv6 port 80.
- Uses api.example.com as the server name.
- Forwards requests to http://127.0.0.1:8000.
- Preserves the original Host header.
- Forwards client IP information using X-Real-IP and
  X-Forwarded-For.
- Forwards the original protocol using X-Forwarded-Proto.
- Defines connection, read and send timeouts.
- Uses dedicated API access and error logs.

The default Nginx site is disabled.

## 7. Deployment

Deploy the role using:

    ansible-playbook playbooks/nginx.yml

The role performs the following operations:

1. Validates the operating system.
2. Validates the Nginx configuration variables.
3. Installs Nginx.
4. Deploys the reverse-proxy site.
5. Enables the site.
6. Disables the default site.
7. Validates the complete Nginx configuration.
8. Enables and starts the Nginx service.
9. Verifies that the service is active.

Configuration changes notify handlers that validate the Nginx
configuration before reloading the service.

## 8. Validation and test results

### 8.1 Ansible validation

- Playbook syntax check: passed.
- Inventory targeting: ApiServer confirmed.
- Deployment: successful.
- Second execution: changed=0.
- Failed hosts: 0.
- Unreachable hosts: 0.

### 8.2 Nginx service

Command:

    systemctl is-active nginx

Result:

    active

### 8.3 Nginx configuration

Command:

    nginx -t

Result:

    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    nginx: configuration file /etc/nginx/nginx.conf test is successful

### 8.4 Network listener

Nginx was verified listening on:

- 0.0.0.0:80
- [::]:80

### 8.5 Local API health through Nginx

Request:

    curl -i -H "Host: api.example.com" http://127.0.0.1/health

Result:

    HTTP 200 OK

Response:

    {"status":"healthy"}

### 8.6 Controller-to-API integration test

Request:

    curl -i -H "Host: api.example.com" http://192.168.174.133/health

Result:

    HTTP 200 OK

Response:

    {"status":"healthy"}

### 8.7 API root endpoint

Request:

    curl -i -H "Host: api.example.com" http://192.168.174.133/

Result:

    HTTP 200 OK

Response:

    {"application":"Server Automation Sample API",
     "version":"1.0.0",
     "status":"running"}

## 9. Security considerations

The implementation includes:

- Backend application bound to loopback.
- Nginx as the HTTP entry point.
- Default Nginx site disabled.
- Configuration validation before reload.
- Dedicated access and error logs.

The following items are not yet implemented:

- TLS certificates and HTTPS.
- Public DNS configuration.
- Firewall restrictions for HTTP and HTTPS.
- Production hostname and certificate validation.
- Additional access controls and API-specific security policies.

Nginx currently listens on all IPv4 and IPv6 interfaces on
port 80. UFW was previously found inactive. Network exposure
must therefore be reviewed before production use.

## 10. Milestone status

Milestone 4.5 — Nginx Reverse Proxy:

IMPLEMENTED AND VALIDATED.

The role was deployed successfully, both API endpoints returned
HTTP 200 through Nginx, and the second Ansible execution reported
zero changes.

Milestone 4.6 — Final documentation and security/integration review
remains pending.
