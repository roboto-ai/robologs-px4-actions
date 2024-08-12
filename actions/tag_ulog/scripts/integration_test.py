import subprocess
from pathlib import Path
# Run the build script
subprocess.run(["./scripts/deploy.sh", "roboto-public"], check=True)

import logging
import pathlib
from roboto.domain import datasets, actions, topics
from roboto.waiters import wait_for
from roboto.association import Association, AssociationType

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def wait_for_terminal_status(invocation: actions.Invocation) -> None:
    def _invocation_has_terminal_status(invoc: actions.Invocation) -> bool:
        invoc.refresh()
        return invoc.reached_terminal_status

    wait_for(
        _invocation_has_terminal_status,
        args=[invocation],
        interval=10,
        timeout_msg=f"Invocation {invocation.id} has not run to completion in allowed time",
    )

caller_org_id = "roboto-public"

# Create dataset
log.info("Creating dataset")
dataset = datasets.Dataset.create(caller_org_id=caller_org_id)
dataset.put_tags(tags=["integration_test", "ros_ingestion"])
log.info(f"Dataset created: {dataset.dataset_id}")

# Upload PX4 file
test_file_path_ulg = pathlib.Path("./test/input/test.ulg")
log.info(f"Uploading file {test_file_path_ulg}")
dataset.upload_file(test_file_path_ulg, file_destination_path="test.ulg")

# Invoke action
action = actions.Action.from_name(name="tag_ulog", owner_org_id=caller_org_id)
log.info("Invoking action")
invocation = action.invoke(
        input_data=["**.ulg"],
        data_source_id=dataset.dataset_id,
        data_source_type=actions.InvocationDataSourceType.Dataset,
        invocation_source=actions.InvocationSource.Manual,
        caller_org_id=caller_org_id,
)
wait_for_terminal_status(invocation)

try:
    assert invocation.current_status == actions.InvocationStatus.Completed
except AssertionError as e:
    for entry in invocation.get_logs():
        print(entry.log)
    raise e

file_id = dataset.get_file_by_path("test.ulg")

assert "ERROR_commander" in file_id.tags
log.info("Test completed successfully")
