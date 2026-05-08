# Codex Porkbun Skill

A public-safe Codex skill for managing Porkbun domains and DNS while keeping each user's API keys local.

Created by **Ray Brown / [rayproducer](https://github.com/rayproducer)**.

## What It Does

- Lists Porkbun domains, expiration dates, API access, and auto-renew status.
- Retrieves DNS records for a domain.
- Finds DNS records by type and name.
- Creates, updates, and deletes DNS records through Porkbun's API.
- Keeps credentials out of the skill and out of git.

## Install

Copy this skill into your Codex skills folder:

```zsh
mkdir -p ~/.codex/skills
git clone https://github.com/rayproducer/codex-porkbun-skill.git ~/.codex/skills/porkbun
```

Restart Codex if the skill does not appear immediately.

## Set Up Credentials

Create a local `.env.porkbun` file in the workspace where you want to run Porkbun commands:

```zsh
cp .env.porkbun.example .env.porkbun
```

Then fill in your own Porkbun API keys:

```zsh
PORKBUN_API_KEY="pk1_your_api_key_here"
PORKBUN_SECRET_API_KEY="sk1_your_secret_key_here"
```

Do not commit `.env.porkbun`. It is ignored by this repository.

You can also use environment variables directly, or set `PORKBUN_ENV_FILE` to the path of your credential file.

## Usage

In Codex, invoke the skill with:

```text
$porkbun list my domains by expiration date
$porkbun show DNS for example.com
```

You can also run the scripts directly:

```zsh
scripts/porkbun-domains.sh
scripts/porkbun-dns.py list example.com
scripts/porkbun-dns.py find example.com A www
```

Create, update, and delete DNS records:

```zsh
scripts/porkbun-dns.py create example.com A app 1.2.3.4
scripts/porkbun-dns.py update example.com RECORD_ID A app 5.6.7.8
scripts/porkbun-dns.py delete example.com RECORD_ID --yes
```

For root/apex records, use empty quotes for the name:

```zsh
scripts/porkbun-dns.py create example.com TXT "" "v=spf1 include:_spf.example.com ~all"
```

## Safety Notes

- Never paste API secrets into chat or commit them to git.
- Enable Porkbun API access per domain in Porkbun Domain Management.
- Review DNS changes before applying them.
- Prefer deleting DNS records by ID to avoid deleting multiple matching records.

## License

MIT

