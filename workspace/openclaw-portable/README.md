# OpenClaw portability bundle

This directory makes the current OpenClaw setup reproducible on another host.

## Files
- `openclaw.template.json` - versioned config template with host-specific placeholders
- `openclaw.env.example` - example env contract, do not commit live secrets
- `bootstrap-openclaw.sh` - renders config, installs env for systemd, restarts the gateway

## Required secret inputs
Provide these from Vault or another central secret source:
- `OPENCLAW_GATEWAY_PASSWORD`
- `OPENAI_API_KEY`
- `OPENCLAW_ALLOWED_ORIGIN`

## Suggested migration flow
1. Restore the workspace on the new host.
2. Install OpenClaw and system dependencies.
3. Create `/home/jccadmin/.openclaw/.env` from the example and fill it from Vault.
4. Run `bootstrap-openclaw.sh`.
5. Verify `openclaw health` and `openclaw status`.
6. Confirm the Tailscale URL matches `OPENCLAW_ALLOWED_ORIGIN`.

## Notes
- The allowed origin is host-specific and must be changed for each new Tailscale hostname.
- Keep secrets out of git and out of wiki page bodies.
- Wiki.js remains the durable operational memory and should be updated when the deployment model changes.
