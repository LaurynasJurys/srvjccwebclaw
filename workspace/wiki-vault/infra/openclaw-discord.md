---
title: OpenClaw Discord setup
---

# OpenClaw Discord setup

## Current direction

Main communication is being moved from WhatsApp toward Discord.

## Current state

- OpenClaw is exposed through Tailscale.
- WhatsApp is still active.
- Discord has been enabled as a new channel.
- Owner Discord user id: `147099563864358913`
- Guild id: `1485021229638226125`
- Channel `general` is enabled for slash command access.

## Secrets policy

- Secrets must never be shared in chat.
- Secrets should only be stored and retrieved through Vault.
- Discord bot credentials are stored in Vault under `secret/Discord`.
- Vault root credentials live under `/root/.vault` and should only be used when explicitly authorized.

## Known issue

The current Discord Vault secret shape is slightly wrong because `ChannelId` is being used as a guild id. This should be cleaned up later into:

- `GuildId`
- `ChannelId`
- `UserId`
- `Token`

## Next direction

The longer-term goal is to talk to OpenClaw by voice, likely starting on Discord before a more advanced voice flow is introduced later.
