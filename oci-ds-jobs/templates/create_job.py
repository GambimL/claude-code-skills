import os
import ads

from ads.jobs import Job, DataScienceJob, ScriptRuntime

compartment_id = os.environ['NB_SESSION_COMPARTMENT_OCID'] #compartment id
ads.set_auth(auth="resource_principal") # autenticação do ads


# Treino
job = (
    Job(name="job-name") #job name
    .with_infrastructure(
        DataScienceJob()
        .with_log_group_id("log-group-id")
        .with_log_id("log-id")
        .with_project_id("project-id")
        .with_shape_name("shape-name")
        .with_shape_config_details(ocpus=1, memory_in_gbs=16)
        .with_block_storage_size(50)
        .with_storage_mount(
          {
            "src" : "src",
            "dest" : "dest",
          },
        )
    )
    .with_runtime(
        ScriptRuntime()
        .with_custom_conda("custom-conda")
        .with_source("zip-file-path")
        .with_environment_variable(
            ENV_VAR_NAME="env-var-value", 
        )
        .with_entrypoint("entrypoint.py(in zip file)")
    )
)


job.create()