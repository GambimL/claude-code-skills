# oci-ds-jobs — Claude Code Skill

A Claude Code skill for automating the deployment of Oracle Cloud Infrastructure (OCI) Data Science Jobs using the [ADS SDK](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/jobs/data_science_job.html).

## What it does

When invoked, this skill:

1. Compresses the provided job scripts folder into a zip artifact
2. Reads the target script/notebook the user wants to deploy
3. Uses `templates/create_job.py` as a base to configure and create the OCI Data Science Job
4. Returns the job OCID and the status of the job run

## Prerequisites

- **OCI CLI configured** — `~/.oci/config` with a valid profile
- **ADS SDK installed** — `pip install oracle-ads`
- **OCI permissions** — IAM policies granting access to create and manage Data Science Jobs in the target compartment

## Directory structure

```
oci-ds-jobs/
├── SKILL.md                    # Skill definition and instructions for Claude
├── README.md                   # This file
├── config/
│   └── defaults.json           # Default infrastructure configuration (fill in your values)
├── templates/
│   └── create_job.py           # Base template for creating OCI DS Jobs
└── references/
    └── reference-ads.md        # ADS SDK documentation reference
```

## Configuration

Copy `config/defaults.json` and fill in your OCI resource IDs:

```json
{
    "log_group_id": "ocid1.loggroup.oc1.<region>...",
    "log_id": "ocid1.log.oc1.<region>...",
    "project_id": "ocid1.project.oc1.<region>...",
    "compartment_id": "ocid1.compartment.oc1...",
    "shape": "VM.Standard.E3.Flex",
    "storange_mount": {
        "src": "oci://<bucket>@<namespace>",
        "dest": "/home/datascience/<mount-dir>"
    },
    "custom_conda": "oci://<bucket>@<namespace>/conda_environments/...",
    "environment_variables": {
        "MY_VAR": "my-value"
    }
}
```

The skill looks for a project-level config JSON first (passed as an argument), falling back to `config/defaults.json`.

## Usage

Invoke the skill from Claude Code by describing the job you want to deploy. Example prompts:

```
Deploy the scripts in ./my_pipeline as an OCI Data Science job
```

```
Create an OCI DS job from ./train.py using my project config at ./job_config.json
```

### Arguments

| Position | Description |
|----------|-------------|
| `$ARGUMENTS[0]` | Path to search for the OCI config file (if not in default `~/.oci/config` location) |
| `$ARGUMENTS[1]` | Path to a project-level JSON config file (overrides `config/defaults.json`) |
| `$ARGUMENTS[2]` | Path to the folder containing the job scripts to compress and upload |

## Runtime types supported

The template supports all ADS runtime types:

- **ScriptRuntime** — Python, Bash, or Java scripts
- **PythonRuntime** — Python code with extended options (output copy, Python path)
- **NotebookRuntime** — Single Jupyter notebook
- **GitPythonRuntime** — Source code from a Git repository
- **ContainerRuntime** — Container images

## References

- [ADS Data Science Job docs](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/jobs/data_science_job.html)
- [OCI Data Science Policies](https://docs.oracle.com/en-us/iaas/data-science/using/policies.html)
- [Publishing a Conda Environment](https://docs.oracle.com/en-us/iaas/data-science/using/conda_publishs_object.html)
