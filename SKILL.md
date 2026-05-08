---
name: porkbun
description: Manage Porkbun domains and DNS through the Porkbun API. Use when Codex should connect to Porkbun, list domains, check expiration dates, inspect API access or auto-renew status, retrieve DNS records, add/update/delete DNS records, configure dynamic DNS, or automate Porkbun account/domain workflows using local API credentials.
---

# Porkbun

Use Porkbun's API through local credentials. Prefer bundled scripts for routine domain and DNS work.

## Credential Handling

Never ask the user to paste Porkbun secrets into chat. Use credentials in this order:

1. Existing `PORKBUN_API_KEY` and `PORKBUN_SECRET_API_KEY` environment variables.
2. `PORKBUN_ENV_FILE`, when set to a file containing those variables.
3. `.env.porkbun` in the current workspace or skill folder.

Use this file shape:

```zsh
PORKBUN_API_KEY="pk1_..."
PORKBUN_SECRET_API_KEY="sk1_..."
```

Ensure `.env.porkbun` is ignored by git before creating or editing it. Keep example/template files free of real keys.

## Workflow

For read-only tasks, run the relevant script and summarize the result in friendly prose or a compact table. For DNS-changing tasks, first retrieve the current records, state the exact planned change, then perform the change only when the user has clearly requested it. Confirm deletions unless the user already gave an unambiguous delete instruction.

Porkbun API access is per domain. If API calls fail for a domain with an access-related error, tell the user to enable API access for that domain in Porkbun Domain Management.

## Scripts

Run scripts from the user's active workspace when possible so `.env.porkbun` can be found there.

List domains:

```zsh
scripts/porkbun-domains.sh
```

List DNS records:

```zsh
scripts/porkbun-dns.py list example.com
```

Find records by type and optional subdomain:

```zsh
scripts/porkbun-dns.py find example.com A www
scripts/porkbun-dns.py find example.com MX
```

Create, update, or delete DNS records:

```zsh
scripts/porkbun-dns.py create example.com A app 1.2.3.4
scripts/porkbun-dns.py update example.com RECORD_ID A app 5.6.7.8
scripts/porkbun-dns.py delete example.com RECORD_ID --yes
```

Use empty quotes for root/apex record names:

```zsh
scripts/porkbun-dns.py create example.com TXT "" "v=spf1 include:_spf.example.com ~all"
```

## References

Read `references/porkbun-api.md` when adding new operations beyond domain listing and DNS record management.

