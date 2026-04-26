# Argo CD deployment plan for polymarket-autopilot

## Recommended repo split

### 1. App code repo
Example:
- `git@github.com:LaurynasJurys/polymarket-autopilot.git`

This repo should contain:
- Node app code
- Dockerfile
- Kubernetes manifests or Helm chart
- optional GitHub Actions for image build/push

### 2. GitOps repo
Keep only the Argo CD Application object in:
- `K3s/apps/polymarket-autopilot/application.yaml`

If you want stronger separation, keep raw manifests in the app repo too, and Argo CD points directly there.

## Best v1 Kubernetes shape

- one `CronJob` every 15 minutes for scanning
- one `CronJob` every day for reporting
- one `PersistentVolumeClaim` for SQLite
- one `ConfigMap` for non-secret config
- one `Secret` for future message/webhook credentials if needed

## Important caveat

SQLite on Kubernetes is acceptable only for hobby-scale v1 on a single-node k3s cluster. If this grows, move to Postgres.
