---
name: oci-ds-jobs
description: This skill provides the ability to manage Oracle Data Science jobs, including creating, updating, and deleting jobs, as well as retrieving job details and monitoring job status.
disable-model-invocation: true
---


# OCI Data Science Job Deployment Skill

## When to use this skill
Use this skill when you want to automate the deployment of Oracle Data Science jobs. This skill allows you to create, update, and delete jobs, as well as retrieve job details and monitor job status, all through a simple interface. This skill should always be questioned before being performed.


## Prerequisites
- OCI CLI configured (~/.oci/config), search for oci config in folder $ARGUMENTS[0] if not found in default location
- ADS SDK should be installed (`pip install oracle-ads`)
- User should have the necessary permissions to create and manage Data Science jobs in OCI


## Configurações padrão
the user The user may want to use their own configuration file; look for $ARGUMENTS[1] json file in the project for the compartment_id, project_id and shape. If not found, use the default configuration file at `config/defaults.json`.


## Fluxo
1. compact the folder $ARGUMENTS[2] containing the job scripts
1. Ler o script/notebook que o usuário quer subir
2. Usar `templates/create_job.py` como base para criar o job
5. Retornar o OCID do job e o status do job run


