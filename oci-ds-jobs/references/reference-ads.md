# Data Science Job

> **Source:** [ADS Documentation - Data Science Job](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/jobs/data_science_job.html)

---

## Overview

Oracle Cloud Infrastructure (OCI) Data Science Jobs (Jobs) enables you to define and run repeatable machine learning tasks on a fully managed infrastructure. You can create a compute resource on demand and run applications that perform tasks such as data preparation, model training, hyperparameter tuning, and batch inference.

Running workloads with Data Science Jobs involves two types of resources:

- **Job** — A template that describes the training task. It contains configurations about the infrastructure (Compute Shape, Block Storage, Logging) and information about the runtime (source code, environment variables, CLI arguments).
- **Job Run** — An instantiation of a job. In each job run, you can override some of the job configurations, such as environment variables and CLI arguments. You can use the same job as a template and launch multiple simultaneous job runs to parallelize a large task.

For example, you may want to experiment with how different model classes perform on the same training data by using the `ADSTuner` to perform hyperparameter tuning on each model class. You could do this in parallel by having a different job run for each class of models. For a given job run, you could pass an environment variable that identifies the model class that you want to use. Each model can write its results to the Logging service or Object Storage. Then you can run a final sequential job that uses the best model class, and trains the final model on the entire dataset.

---

## Quick Start

In ADS, a job is defined by **Infrastructure** and **Runtime**. The Data Science Job infrastructure is configured through a `DataScienceJob` instance. The runtime can be an instance of:

- **PythonRuntime** — For Python code stored locally, OCI Object Storage, or other remote location supported by `fsspec`. See [Run a Python Workload](#pythonruntime).
- **GitPythonRuntime** — For Python code from a Git repository. See [Run Code from Git Repo](#gitpythonruntime).
- **NotebookRuntime** — For a single Jupyter notebook stored locally, OCI Object Storage, or other remote location supported by `fsspec`. See [Run a Notebook](#notebookruntime).
- **ScriptRuntime** — For bash or shell scripts stored locally, OCI Object Storage, or other remote location supported by `fsspec`. See [Run a Script](#scriptruntime).
- **ContainerRuntime** — For container images.

A job can be defined either using Python APIs or YAML.

### Python

```python
from ads.jobs import Job, DataScienceJob, PythonRuntime

job = (
    Job(name="My Job")
    .with_infrastructure(
        DataScienceJob()
        # Configure logging for getting the job run outputs.
        .with_log_group_id("<log_group_ocid>")
        # Log resource will be auto-generated if log ID is not specified.
        .with_log_id("<log_ocid>")
        # If you are in an OCI data science notebook session,
        # the following configurations are not required.
        # Configurations from the notebook session will be used as defaults.
        .with_compartment_id("<compartment_ocid>")
        .with_project_id("<project_ocid>")
        .with_subnet_id("<subnet_ocid>")
        .with_shape_name("VM.Standard.E3.Flex")
        # Shape config details are applicable only for the flexible shapes.
        .with_shape_config_details(memory_in_gbs=16, ocpus=1)
        # Minimum/Default block storage size is 50 (GB).
        .with_block_storage_size(50)
        # A maximum number of 5 file systems are allowed to be mounted for a job.
        .with_storage_mount(
            {
                "src": "<mount_target_ip_address>@<export_path>",
                "dest": "<destination_path>/<destination_directory_name>"
            },
            {
                "src": "oci://<bucket_name>@<namespace>/<prefix>",
                "dest": "<destination_directory_name>"
            }
        )
    )
    .with_runtime(
        PythonRuntime()
        # Specify the service conda environment by slug name.
        .with_service_conda("pytorch110_p38_cpu_v1")
        # Source code of the job, can be local or remote.
        .with_source("path/to/script.py")
        # Environment variable
        .with_environment_variable(NAME="Welcome to OCI Data Science.")
        # Command line argument
        .with_argument(greeting="Good morning")
    )
)
```

### YAML

```yaml
kind: job
spec:
  name: "My Job"
  infrastructure:
    kind: infrastructure
    type: dataScienceJob
    spec:
      blockStorageSize: 50
      compartmentId: <compartment_ocid>
      jobInfrastructureType: STANDALONE
      logGroupId: <log_group_ocid>
      logId: <log_ocid>
      projectId: <project_ocid>
      shapeConfigDetails:
        memoryInGBs: 16
        ocpus: 1
      shapeName: VM.Standard.E3.Flex
      subnetId: <subnet_ocid>
      storageMount:
        - src: <mount_target_ip_address>@<export_path>
          dest: <destination_path>/<destination_directory_name>
        - src: oci://<bucket_name>@<namespace>/<prefix>
          dest: <destination_directory_name>
  runtime:
    kind: runtime
    type: python
    spec:
      args:
        - --greeting
        - Good morning
      conda:
        slug: pytorch110_p38_cpu_v1
        type: service
      env:
        - name: NAME
          value: Welcome to OCI Data Science.
      scriptPathURI: path/to/script.py
```

---

## Creating and Running a Job

Once the job is defined or loaded from YAML, you can call the `create()` method to create the job on OCI. To start a job run, you can call the `run()` method, which returns a `DataScienceJobRun` instance.

Once the job or job run is created, the job OCID can be accessed through `job.id` or `run.id`.

> **Note:** Once a job is created, if you change the configuration, you will need to re-create a job for the new configuration.

```python
# Create the job on OCI Data Science
job.create()

# Start a job run
run = job.run()

# Stream the job run outputs
run.watch()
```

The `watch()` method is useful to monitor the progress of the job run. It will stream the logs to terminal and return once the job is finished. Logging configurations are required for this method to show logs.

### Example Log Output

```
Job OCID: <job_ocid>
Job Run OCID: <job_run_ocid>
2023-02-27 15:58:01 - Job Run ACCEPTED
2023-02-27 15:58:11 - Job Run ACCEPTED, Infrastructure provisioning.
2023-02-27 15:59:06 - Job Run ACCEPTED, Infrastructure provisioned.
2023-02-27 15:59:29 - Job Run ACCEPTED, Job run bootstrap starting.
2023-02-27 16:01:08 - Job Run ACCEPTED, Job run bootstrap complete. Artifact execution starting.
2023-02-27 16:01:18 - Job Run IN_PROGRESS, Job run artifact execution in progress.
2023-02-27 16:01:11 - Good morning, your environment variable has value of (Welcome to OCI Data Science.)
```

---

## Infrastructure

The Data Science Job infrastructure is defined by a `DataScienceJob` instance. When creating a job, you specify the compartment ID, project ID, subnet ID, Compute shape, Block Storage size, log group ID, and log ID.

### Full Infrastructure Configuration

```python
from ads.jobs import DataScienceJob

infrastructure = (
    DataScienceJob()
    .with_compartment_id("<compartment_ocid>")
    .with_project_id("<project_ocid>")
    .with_subnet_id("<subnet_ocid>")
    .with_shape_name("VM.Standard.E3.Flex")
    .with_shape_config_details(memory_in_gbs=16, ocpus=1)  # Applicable only for the flexible shapes
    .with_block_storage_size(50)
    .with_log_group_id("<log_group_ocid>")
    .with_log_id("<log_ocid>")
)
```

### Using Notebook Session Defaults

If you are using these API calls in a Data Science Notebook Session, and you want to use the same infrastructure configurations as the notebook session, you can initialize the `DataScienceJob` with only the logging configurations:

```python
from ads.jobs import DataScienceJob

infrastructure = (
    DataScienceJob()
    .with_log_group_id("<log_group_ocid>")
    .with_log_id("<log_ocid>")
)
```

### Overriding Shape for GPU

In some cases, you may want to override the shape and block storage size. For example, if you are testing your code in a CPU notebook session, but want to run the job in a GPU VM:

```python
from ads.jobs import DataScienceJob

infrastructure = (
    DataScienceJob()
    .with_shape_name("VM.GPU2.1")
    .with_log_group_id("<log_group_ocid>")
    .with_log_id("<log_ocid>")
)
```

### Listing Available Shapes

You can get a list of currently supported shapes by calling:

```python
DataScienceJob.instance_shapes()
```

### Logging Configuration Notes

- If both the log OCID and corresponding log group OCID are specified, both are used.
- If your administrator configured the permission for you to search for logging resources, you can skip specifying the log group OCID because ADS automatically retrieves it.
- If you specify only the log group OCID and no log OCID, a new Log resource is automatically created within the log group to store the logs.

### Storage Mount

A maximum number of 5 file systems are allowed to be mounted for a job. You can pass `<mount_target_ip_address>@<export_path>` as the value for `src` to mount OCI File Storage. You can also pass `oci://<bucket_name>@<namespace>/<prefix>` to mount OCI Object Storage.

The value of `dest` indicates the path and directory to which you want to mount the file system and must be in the format `<destination_path>/<destination_directory_name>`. The `<destination_directory_name>` is required while the `<destination_path>` is optional. The `<destination_path>` must start with `/` if provided. If not, the file systems will be mounted to `/mnt/<destination_directory_name>` by default.

```python
from ads.jobs import DataScienceJob

infrastructure = (
    DataScienceJob()
    .with_log_group_id("<log_group_ocid>")
    .with_log_id("<log_ocid>")
    .with_storage_mount(
        {
            "src": "<mount_target_ip_address>@<export_path>",
            "dest": "<destination_path>/<destination_directory_name>"
        },
        {
            "src": "oci://<bucket_name>@<namespace>/<prefix>",
            "dest": "<destination_directory_name>"
        }
    )
)
```

### Infrastructure YAML Schema

```yaml
kind:
  allowed:
    - "infrastructure"
  required: true
  type: "string"
spec:
  required: true
  schema:
    blockStorageSize:
      default: 50
      min: 50
      required: false
      type: "float"
    compartmentId:
      required: false
      type: "string"
    displayName:
      required: false
      type: "string"
    id:
      required: false
      type: "string"
    jobInfrastructureType:
      default: "STANDALONE"
      required: false
      type: "string"
    jobType:
      allowed:
        - "DEFAULT"
      required: false
      type: "string"
    logGroupId:
      required: false
      type: "string"
    logId:
      required: false
      type: "string"
    projectId:
      required: false
      type: "string"
    shapeName:
      required: false
      type: "string"
    subnetId:
      required: false
      type: "string"
  type: "dict"
type:
  allowed:
    - "dataScienceJob"
  required: true
  type: "string"
```

---

## Runtime Types

A job can have different types of runtime depending on the source code you want to run. All runtime options allow you to configure a Data Science Conda Environment.

### ScriptRuntime

Allows you to run Python, Bash, and Java scripts from a single source file (`.zip` or `.tar.gz`) or code directory.

```python
from ads.jobs import ScriptRuntime

runtime = (
    ScriptRuntime()
    .with_source("oci://bucket_name@namespace/path/to/script.py")
    .with_service_conda("tensorflow28_p38_cpu_v1")
)
```

With environment variables, arguments, and tags:

```python
runtime = (
    ScriptRuntime()
    .with_source("oci://bucket_name@namespace/path/to/script.py")
    .with_service_conda("tensorflow28_p38_cpu_v1")
    .with_environment_variable(ENV="value")
    .with_argument("argument", key="value")
    .with_freeform_tag(tag_name="tag_value")
)
```

With the preceding arguments, the script is started as: `python script.py argument --key value`.

You can store your source code in a local file path or location supported by `fsspec`.

#### Using Custom Conda Environment

```python
from ads.jobs import ScriptRuntime

runtime = (
    ScriptRuntime()
    .with_source("oci://bucket_name@namespace/path/to/script.py")
    .with_custom_conda("oci://bucket@namespace/conda_pack/pack_name")
)
```

By default, ADS will try to determine the region based on the authenticated API key or resource principal. If your custom conda environment is stored in a different region, you can specify the region when calling `with_custom_conda()`.

### PythonRuntime

Allows you to run Python code with additional options, including setting a working directory, adding Python paths, and copying output files.

```python
from ads.jobs import PythonRuntime

runtime = (
    PythonRuntime()
    .with_service_conda("pytorch110_p38_cpu_v1")
    .with_source("path/to/script.py")
    .with_environment_variable(NAME="Welcome to OCI Data Science.")
    .with_argument(greeting="Good morning")
)
```

With custom conda:

```python
from ads.jobs import PythonRuntime

runtime = (
    PythonRuntime()
    .with_source("oci://bucket_name@namespace/path/to/script.py")
    .with_custom_conda("oci://bucket@namespace/conda_pack/pack_name")
)
```

#### YAML

```yaml
kind: runtime
type: python
spec:
  conda:
    type: published
    uri: oci://bucket@namespace/conda_pack/pack_name
  scriptPathURI: oci://bucket_name@namespace/path/to/script.py
```

#### Output Files

You can copy output files from the job run to Object Storage:

```python
from ads.jobs import PythonRuntime

runtime = (
    PythonRuntime()
    .with_service_conda("pytorch110_p38_gpu_v1")
    .with_environment_variable(DATASET_NAME="MyData")
    .with_source("local/path/to/training_script.py")
    .with_output("output", "oci://bucket_name@namespace/prefix/${JOB_RUN_OCID}")
)
```

### NotebookRuntime

Allows you to run a single Jupyter notebook as a job.

```python
from ads.jobs import Job, DataScienceJob, NotebookRuntime

job = (
    Job(name="My Job")
    .with_infrastructure(
        DataScienceJob()
        .with_log_group_id("<log_group_ocid>")
        .with_log_id("<log_ocid>")
        .with_compartment_id("<compartment_ocid>")
        .with_project_id("<project_ocid>")
        .with_subnet_id("<subnet_ocid>")
        .with_shape_name("VM.Standard.E3.Flex")
        .with_shape_config_details(memory_in_gbs=16, ocpus=1)
        .with_block_storage_size(50)
    )
    .with_runtime(
        NotebookRuntime()
        .with_notebook(
            path="https://raw.githubusercontent.com/tensorflow/docs/master/site/en/tutorials/customization/basics.ipynb",
            encoding='utf-8'
        )
        .with_service_conda("tensorflow28_p38_cpu_v1")
        .with_environment_variable(GREETINGS="Welcome to OCI Data Science")
        .with_exclude_tag(["ignore", "remove"])
        .with_output("oci://bucket_name@namespace/path/to/dir")
    )
)
```

The `NotebookRuntime` also allows you to specify tags to exclude cells from being processed in a job run using `with_exclude_tag()` method. Cells with any matching tags are excluded from the job run.

#### YAML

```yaml
kind: job
spec:
  name: "My Job"
  infrastructure:
    kind: infrastructure
    type: dataScienceJob
    spec:
      blockStorageSize: 50
      compartmentId: <compartment_ocid>
      jobInfrastructureType: STANDALONE
      logGroupId: <log_group_ocid>
      logId: <log_ocid>
      projectId: <project_ocid>
      shapeConfigDetails:
        memoryInGBs: 16
        ocpus: 1
      shapeName: VM.Standard.E3.Flex
      subnetId: <subnet_ocid>
  runtime:
    kind: runtime
    type: notebook
    spec:
      conda:
        slug: tensorflow28_p38_cpu_v1
        type: service
      env:
        - name: GREETINGS
          value: Welcome to OCI Data Science
      excludeTags:
        - ignore
        - remove
      notebookEncoding: utf-8
      notebookPathURI: https://raw.githubusercontent.com/tensorflow/docs/master/site/en/tutorials/customization/basics.ipynb
      outputUri: oci://bucket_name@namespace/path/to/dir
```

### GitPythonRuntime

Allows you to run source code from a Git repository as a Data Science job.

```python
from ads.jobs import Job, DataScienceJob, GitPythonRuntime

job = (
    Job()
    .with_infrastructure(
        DataScienceJob()
        .with_log_group_id("<log_group_ocid>")
        .with_log_id("<log_ocid>")
        .with_compartment_id("<compartment_ocid>")
        .with_project_id("<project_ocid>")
        .with_subnet_id("<subnet_ocid>")
        .with_shape_name("VM.Standard.E3.Flex")
        .with_shape_config_details(memory_in_gbs=16, ocpus=1)
        .with_block_storage_size(50)
    )
    .with_runtime(
        GitPythonRuntime()
        .with_environment_variable(GREETINGS="Welcome to OCI Data Science")
        .with_service_conda("pytorch19_p37_gpu_v1")
        .with_source("https://github.com/pytorch/tutorials.git")
        .with_entrypoint("beginner_source/examples_nn/polynomial_nn.py")
        .with_output(
            output_dir="~/Code/tutorials/beginner_source/examples_nn",
            output_uri="oci://BUCKET_NAME@BUCKET_NAMESPACE/PREFIX"
        )
    )
)

# Create the job with OCI
job.create()

# Run the job and stream the outputs
job_run = job.run().watch()
```

The default branch from the Git repository is used unless you specify a different branch or commit in the `.with_source()` method.

The `GitPythonRuntime` method updates metadata in the free form tags of the job run after the job run finishes.

By default, the source code is cloned to the `~/Code` directory. The `.with_python_path()` method allows you to add additional Python paths to the runtime. The `.with_argument()` method allows you to pass arguments to invoke the script or function.

#### Running a Notebook from Git

```python
from ads.jobs import Job, DataScienceJob, GitPythonRuntime

job = (
    Job(name="My Job")
    .with_infrastructure(
        DataScienceJob()
        .with_log_group_id("<log_group_ocid>")
        .with_log_id("<log_ocid>")
        .with_compartment_id("<compartment_ocid>")
        .with_project_id("<project_ocid>")
        .with_subnet_id("<subnet_ocid>")
        .with_shape_name("VM.Standard.E3.Flex")
        .with_shape_config_details(memory_in_gbs=16, ocpus=1)
        .with_block_storage_size(50)
    )
    .with_runtime(
        GitPythonRuntime()
        .with_service_conda("pytorch110_p38_gpu_v1")
        .with_source(url="https://github.com/karpathy/minGPT.git")
        .with_entrypoint("demo.ipynb")
    )
)
```

#### YAML

```yaml
kind: job
spec:
  name: "My Job"
  infrastructure:
    kind: infrastructure
    type: dataScienceJob
    spec:
      blockStorageSize: 50
      compartmentId: <compartment_ocid>
      jobInfrastructureType: STANDALONE
      logGroupId: <log_group_ocid>
      logId: <log_ocid>
      projectId: <project_ocid>
      shapeConfigDetails:
        memoryInGBs: 16
        ocpus: 1
      shapeName: VM.Standard.E3.Flex
      subnetId: <subnet_ocid>
  runtime:
    kind: runtime
    type: gitPython
    spec:
      conda:
        slug: pytorch19_p37_gpu_v1
        type: service
      entrypoint: demo.ipynb
      url: https://github.com/karpathy/minGPT.git
```

---

## Defining a Job

With runtime and infrastructure, you can define a job and give it a name:

```python
from ads.jobs import Job

job = (
    Job(name="<job_display_name>")
    .with_infrastructure(infrastructure)
    .with_runtime(runtime)
)
```

If the job name is not specified, a name is generated automatically based on the name of the job artifact and a time stamp.

Alternatively, a job can also be defined with keyword arguments:

```python
job = Job(
    name="<job_display_name>",
    infrastructure=infrastructure,
    runtime=runtime
)
```

---

## YAML Serialization

The job infrastructure, runtime and job run support YAML serialization/deserialization.

### Full Job YAML Example

```yaml
kind: job
spec:
  name: <job_display_name>
  infrastructure:
    kind: infrastructure
    type: dataScienceJob
    spec:
      logGroupId: <log_group_ocid>
      logId: <log_ocid>
      compartmentId: <compartment_ocid>
      projectId: <project_ocid>
      subnetId: <subnet_ocid>
      shapeName: VM.Standard.E3.Flex
      shapeConfigDetails:
        memoryInGBs: 16
        ocpus: 1
      blockStorageSize: 50
  runtime:
    kind: runtime
    type: script
    spec:
      conda:
        slug: tensorflow28_p38_cpu_v1
        type: service
      scriptPathURI: oci://bucket_name@namespace/path/to/script.py
```

### Job YAML Schema

```yaml
kind:
  required: true
  type: string
  allowed:
    - job
spec:
  required: true
  type: dict
  schema:
    id:
      required: false
    infrastructure:
      required: false
    runtime:
      required: false
    name:
      required: false
      type: string
```

---

## Environment Variable Substitution

When defining a job or starting a job run, you can use environment variable substitution for the names and `output_uri` argument of the `with_output()` method.

```python
from ads.jobs import Job, DataScienceJob, PythonRuntime

job = (
    Job(name="Training on ${DATASET_NAME}")
    .with_infrastructure(
        DataScienceJob()
        .with_log_group_id("<log_group_ocid>")
        .with_log_id("<log_ocid>")
        .with_compartment_id("<compartment_ocid>")
        .with_project_id("<project_ocid>")
        .with_shape_name("VM.Standard.E3.Flex")
        .with_shape_config_details(memory_in_gbs=16, ocpus=1)
    )
    .with_runtime(
        PythonRuntime()
        .with_service_conda("pytorch110_p38_gpu_v1")
        .with_environment_variable(DATASET_NAME="MyData")
        .with_source("local/path/to/training_script.py")
        .with_output("output", "oci://bucket_name@namespace/prefix/${JOB_RUN_OCID}")
    )
)
```

Environment variables enclosed by `${...}` will be substituted.

---

## Managing Jobs

### Listing Jobs

```python
from ads.jobs import Job

# Get a list of jobs in a specific compartment.
jobs = Job.datascience_job("<compartment_ocid>")
```

### Listing Job Runs

```python
# Gets a list of job runs for a specific job.
runs = job.run_list()
```

### Deleting Jobs and Job Runs

```python
# Delete a job and the corresponding job runs.
job.delete()

# Delete a job run
run.delete()
```

### Running a Job with Overrides

When you call `job.run()`, a new job run will be started with the configuration defined in the job. You can override certain configurations:

```python
job_run = job.run(
    name="custom-run-name",
    args="--custom-arg value",
    env_var={"KEY": "value"},
    freeform_tags={"tag_name": "tag_value"},
    wait=False
)
```

Parameters:

- **name** (`str`, optional) — Name of the job run. If not provided, a default name will be generated.
- **args** (`str`, optional) — Command line arguments for the job run. This will override the configurations on the job.
- **env_var** (`dict`, optional) — Environment variables for the job run.
- **freeform_tags** (`dict`, optional) — Freeform tags for the job run.
- **wait** (`bool`, optional) — Whether to wait for the job run to complete before returning.

---

## Prerequisites

Before creating a job, ensure that you have policies configured for Data Science resources. See [About Data Science Policies](https://docs.oracle.com/en-us/iaas/data-science/using/policies.htm).

---

## Authentication

```python
import ads
import oci

ads.set_auth(
    auth="api_key",
    oci_config_location=oci.config.DEFAULT_LOCATION,
    profile="DEFAULT"
)
```

---

## Related Topics

- [Run a Script](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/jobs/run_script.html)
- [Run a Notebook](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/jobs/run_notebook.html)
- [Run Code from Git Repo](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/jobs/run_git.html)
- [Infrastructure and Runtime](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/jobs/infra_and_runtime.html)
- [ADS Logging](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/logging/logging.html)
- [Publishing a Conda Environment](https://docs.oracle.com/en-us/iaas/data-science/using/conda_publishs_object.htm)