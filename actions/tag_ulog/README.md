# tag_ulog

This Action adds tags to a dataset by scanning ULog files (.ulg) for any ERROR messages. 

Under the hood, it uses the [pyulog](https://github.com/PX4/pyulog) library.

## Getting started

1. Setup a virtual environment specific to this project and install development dependencies, including the `roboto` CLI: `./scripts/setup.sh`
2. Build Docker image: `./scripts/build.sh`
3. Run Action image locally: `./scripts/run.sh <path-to-input-data-directory>`
4. Deploy to Roboto Platform: `./scripts/deploy.sh`

## Action configuration file

This Roboto Action is configured in `action.json`. Refer to Roboto's latest documentation for the expected structure.
