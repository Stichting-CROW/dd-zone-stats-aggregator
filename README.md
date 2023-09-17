# README

dd-zone-stats-aggregator is an application that counts the number of vehicles in every zone.

# How to deploy?

Build api with:

1. `docker build -t ghcr.io/stichting-crow/dd-zone-stats-aggregator:<version_number> .`.

2. `docker push ghcr.io/stichting-crow/dd-zone-stats-aggregator:<version_number>` (make sure you are logged in to gitlab registry)


# ssh tunnels
```bash
ssh -L 5433:10.133.75.95:5432 root@auth.deelfietsdashboard.nl
ssh -L 5434:10.133.137.239:5432 timescaledb
``````