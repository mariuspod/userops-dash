# userops-dash

This is a simple python based tool using the framework [ApeWorx ape](https://docs.apeworx.io/ape/stable/index.html) for exporting `UserOperationEvent` logs from the biconomy entrypoint contract [deployed on base](https://basescan.org/address/0x5ff137d4b0fdcd49dca30c7cf57e578a026d2789).

The indexed data is persisted to a local [victoria-metrics](https://docs.victoriametrics.com) db. The db is added as the default datasource for a provisioned grafana dashboard. The script is built in a way so that it's easy to extend to other chains.

## Usage
Clone the repo and run this command to start all processing:

`docker-compose up -d`

Then open your browser at: http://localhost:3000


## Historical backfills
By default, the data is only processed starting from the time when the script is first invoked.

For historical backfills, you can set the env variable
`BACKFILL_START_BLOCK` to a block in the past which is after the inception block of the entrypoint contract.

When querying historical state, make sure to use an archive node by changing the rpc `uri` inside ape-config.yaml and rebuild the docker image: `docker-compose build`
