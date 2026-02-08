from azure.identity import ClientSecretCredential
from azure.mgmt.datafactory import DataFactoryManagementClient

from dotenv import load_dotenv
from pathlib import Path

import os
import time

def check_pipeline_status(adf_client: DataFactoryManagementClient, pline_kwargs: dict):
    # --- Monitor Pipeline Status ---
    while True:
        pipeline_run = adf_client.pipeline_runs.get(**pline_kwargs)

        # check status of pipeline
        status = pipeline_run.status
        print(f"Current pipeline status: {status}")

        if status in ["Succeeded", "Failed", "Canceled"]:
            print(f"Pipeline run finished with status: {status}")
            break
        
        time.sleep(30) # Wait for 30 seconds before checking again

    # --- Further Actions based on Status (Example) ---
    if status == "Failed":
        raise Exception("Pipeline `sgppipeline_extract` failed.")
        # You can query activity runs for more details here
        # query_response = adf_client.activity_runs.query_by_pipeline_run(...)
        # print_activity_run_details(query_response.value[0])


if __name__ == "__main__":
    # # Retrieve credentials from environment variables
    # # this is strictly used only in development
    # # load env variables
    # env_dir = Path('../../').resolve()
    # load_dotenv(os.path.join(env_dir, '.env'))

    # Retrieve credentials from environment variables
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    client_id = os.environ.get("AZURE_CLIENT_ID")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET")
    sub_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    res_grp_name = os.environ.get("RESOURCE_GROUP_NAME")
    # print(f"running subpipeline with {sub_id}")
    print(res_grp_name)

    # location and data factory name
    location = "eastus"
    adf_name = "sgppipelineadf"

    # Specify your Active Directory client ID, client secret, and tenant ID
    credential = ClientSecretCredential(
        client_id=client_id, 
        client_secret=client_secret, 
        tenant_id=tenant_id
    )

    adf_client = DataFactoryManagementClient(credential, sub_id)

    # run the azrue data factory pipeline
    run_response = adf_client.pipelines.create_run(
        resource_group_name=res_grp_name,
        factory_name=adf_name,
        pipeline_name="sgppipeline_extractor"
    )
    run_id = run_response.run_id

    print(f"pipeline run with id: {run_id}")

    # check the status fo the pipeline and if it is finished
    # only then can the airflow pipeline proceed. If it fails
    # then raise an exception
    check_pipeline_status(adf_client, pline_kwargs={
        "resource_group_name": res_grp_name,
        "factory_name": adf_name,
        "run_id": run_id,
    })

