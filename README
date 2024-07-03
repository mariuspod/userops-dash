# userops-dash

This is a simple python script based on ApeWorx ape for exporting `UserOperationEvent` logs from the biconomy entrypoint contract deployed on base to a local victoria-metrics db. The db is added as the default datasource for a provisioned grafana dashboard. The script is built in a way so that it's easy to extend to other chains.

## Usage
Clone the repo and run this command to start all processing:

`docker-compose up -d`

Then open your browser at: http://localhost:3000


## Historical backfills
By default, the data is only processed starting from the time when the script is first invoked.

For historical backfills, you can set the env variable
`BACKFILL_START_BLOCK` to a block in the past which is after the inception block of the entrypoint contract.

When querying historical state, make sure to use an archive node by changing the value inside ape-config.yaml
