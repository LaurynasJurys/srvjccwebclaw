# MEMORY.md

## Laurynas
- Name: Laurynas
- Timezone: Europe/Vilnius
- Prefers clear correction over agreement

## OpenClaw setup
- Uses Tailscale to expose the OpenClaw web UI
- WhatsApp is currently active, but Discord is being set up as the main communication surface
- Secrets should never be shared in chat, only stored and retrieved via Vault
- Vault root credentials are stored under /root/.vault and can be used when explicitly authorized
- Discord bot credentials are stored in Vault under `secret/Discord`
- Discord owner user id: `147099563864358913`
- Discord guild `1485021229638226125` has `general` enabled for slash command access
- The current Discord Vault secret shape is slightly wrong because `ChannelId` is being used as a guild id and should later be split into proper `GuildId` and `ChannelId`
- Long-term goal is voice access to OpenClaw, likely starting on Discord
- Heartbeat disabled for now
