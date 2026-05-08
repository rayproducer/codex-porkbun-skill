# Porkbun API Notes

Base URL:

```text
https://api.porkbun.com/api/json/v3
```

Credential fields for JSON requests:

```json
{
  "apikey": "pk1_...",
  "secretapikey": "sk1_..."
}
```

Common endpoints:

- `POST /ping`: test credentials and return caller IP.
- `POST /domain/listAll`: list domains, expiration dates, auto-renew, and API access state.
- `POST /dns/retrieve/{domain}`: list DNS records for a domain.
- `POST /dns/retrieve/{domain}/{id}`: retrieve one DNS record by ID.
- `POST /dns/retrieveByNameType/{domain}/{type}/{subdomain}`: retrieve DNS records by type and subdomain. Omit subdomain for root records.
- `POST /dns/create/{domain}`: create a DNS record.
- `POST /dns/edit/{domain}/{id}`: edit a DNS record by ID.
- `POST /dns/delete/{domain}/{id}`: delete a DNS record by ID.

DNS create/edit fields:

- `type`: record type, such as `A`, `AAAA`, `CNAME`, `MX`, `TXT`, `ALIAS`.
- `name`: subdomain portion only; empty string for root/apex.
- `content`: target/value.
- `ttl`: default to `600` unless the user asks otherwise.
- `prio`: required for MX/SRV-style priority; use `0` otherwise.

Safety:

- Do read-only operations directly.
- For create/update/delete, show the exact domain, record name, type, content, TTL, and record ID when relevant before changing DNS unless the user has already specified all details.
- Do not delete by broad name/type unless the user explicitly understands it may delete multiple records; prefer delete by ID.
- Treat API keys and DNS records as operationally sensitive.

Official docs: https://porkbun.com/api/json/v3/documentation

