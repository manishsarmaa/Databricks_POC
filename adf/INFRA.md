# ADF POC — Provisioned Infrastructure

Created with Azure CLI on 2026-06-25. **No secrets in this file** — storage keys are
retrieved on demand (see below) and must only ever live under `adf/.secrets/` (gitignored).

## Subscription / context

| Field | Value |
|---|---|
| Subscription name | Azure subscription 1 |
| Subscription ID | `d5f98fab-893f-45ce-9fdc-c3399ba9f46f` |
| Tenant ID | `7fe6f6b6-e7fe-4f44-911d-35598e6526d0` |
| Signed-in user | sharmamanish242114@gmail.com |
| Region | centralindia |

## Resources

| Resource | Name |
|---|---|
| Resource group | `rg-adf-poc` |
| Storage account (ADLS Gen2, HNS enabled) | `stadfpoc78cqho` |
| Filesystem / container 1 | `source` |
| Filesystem / container 2 | `sink` |
| Data Factory | `adf-poc-78cqho` |

Unique suffix used across names: `78cqho`

## Useful endpoints

- ADLS Gen2 (dfs): `https://stadfpoc78cqho.dfs.core.windows.net/`
- Blob endpoint:   `https://stadfpoc78cqho.blob.core.windows.net/`
- `source` filesystem: `abfss://source@stadfpoc78cqho.dfs.core.windows.net/`
- `sink` filesystem:   `abfss://sink@stadfpoc78cqho.dfs.core.windows.net/`
- ADF Studio: https://adf.azure.com/?factory=/subscriptions/d5f98fab-893f-45ce-9fdc-c3399ba9f46f/resourceGroups/rg-adf-poc/providers/Microsoft.DataFactory/factories/adf-poc-78cqho

## Retrieving the storage key (do NOT commit the output)

```powershell
$az = "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
& $az storage account keys list --account-name stadfpoc78cqho --resource-group rg-adf-poc --query "[0].value" -o tsv
```

Save it only under `adf/.secrets/` if you need it on disk, e.g.:
```powershell
& $az storage account keys list --account-name stadfpoc78cqho --resource-group rg-adf-poc --query "[0].value" -o tsv > adf\.secrets\storage-key.txt
```

## Tear down (when the POC is finished)

```powershell
$az = "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
& $az group delete --name rg-adf-poc --yes --no-wait
```
