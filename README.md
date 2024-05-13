# What is robologs-px4-actions

`robologs-px4-actions` is an open-source collection of software modules to extract, process and analyze PX4 data. These modules, referred to as Actions, are essentially containerized Python scripts, and form part of the broader [robologs](https://github.com/roboto-ai/robologs) library.

Actions can range from simple data transformations to more complex algorithms, accommodating a wide spectrum of requirements and use cases.

The package currently includes the following Actions:

- `tag_ulog`: Scan .ulg files for any errors and emit tags.
- `ulog_to_csv`: Convert .ulg files to .csv files.
- `px4_flight_review`: Generate interactive plots to analyze PX4 flights.

# Prerequisites

## Install Docker
- [Install Docker on Linux](https://docs.docker.com/desktop/install/linux-install/)
- [Install Docker on Mac](https://docs.docker.com/desktop/install/mac-install/)
- [Install Docker on Windows](https://docs.docker.com/desktop/install/windows-install/)

## Install pyenv

- [Install pyenv](https://github.com/pyenv/pyenv)

# Quickstart

Try an Action called: `ulog_info`:

```bash

# 0. Clone this repository
git clone https://github.com/roboto-ai/robologs-px4-actions.git
cd robologs-px4-actions/actions/ulog_info/

# 1. Set up a virtual environment for this project and install dependencies, which includes the `roboto` CLI:
./scripts/setup.sh

# 2. Build the Docker image for the Action: 
./scripts/build.sh

# 3. Run the Action locally: 
./scripts/run.sh <path-to-input-data-directory>

# 4. Run the provided tests to ensure everything is set up correctly:
./scripts/test.sh

# 5. (Optional) Deploy the Action to the Roboto platform (see notes below):
./scripts/deploy.sh

```

Deployment to Roboto (Step 5.) enables you to run an Action at scale on multiple datasets in the cloud, or automatically when new data gets uploaded. You can sign up for a free account at [roboto.ai](https://app.roboto.ai), and find user guides at [docs.roboto.ai](https://docs.roboto.ai/user-guides/index.html).

# Community

We're constantly looking to expand the capabilities of `robologs-px4-actions` and welcome suggestions for new Actions. If you have ideas or need assistance, feel free to join our discussion on [Discord](https://discord.gg/rvXqP6EjwF).

Your contributions and suggestions are not only encouraged but also form an integral part of this open-source initiative. Let's collaborate to make `robologs-px4-actions` more versatile and beneficial for everyone in the PX4 community!
