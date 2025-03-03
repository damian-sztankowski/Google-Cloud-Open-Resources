This script helps you **identify Google Cloud projects that still use Container Registry (GCR)** and determine whether they should be migrated to **Artifact Registry**.
## **📌 Features**

✅ **Scans all projects** in an organization or folder  
✅ **Checks if GCR API and Artifact Registry API are enabled**  
✅ **Detects GCR repositories using both Storage Buckets and Container Registry APIs**  
✅ **Displays structured results in a table format**  
✅ **Supports single-project checks**  
✅ **Progress bar support for large org-wide scans**

## **📦 Requirements**

1. **Python 3.x**
2. **Google Cloud SDK (`gcloud`) installed and authenticated**
3. **Dependencies:** Install required Python modules with:

```bash
pip install tabulate tqdm

or 

pip install -r requirements.txt
```

## **🚀 Usage**

Run the script using the following options:

### **1️⃣ Check a single project**

```bash
python main.py -p PROJECT_ID
```

✔️ **Checks if the project is using GCR**  
✔️ **Lists GCR repositories**  
✔️ **Determines if migration is required**

2️⃣ Scan all projects in an organization

```bash
`python main.py -o ORGANIZATION_ID`
```

✔️ **Scans all projects under the given Organization**  
✔️ **Displays GCR usage status for each project**  
✔️ **Progress bar for large organizations**

3️⃣ Scan all projects in a specific folder
```bash
`python main.py -d FOLDER_ID`
```

✔️ **Scans only the projects within a specific folder**
# **💡 How It Works**

1. **Lists all projects** in the provided Org, Folder, or for a single project.
2. **Checks if the GCR API (`containerregistry.googleapis.com`) is enabled.**
3. **Checks if Artifact Registry API (`artifactregistry.googleapis.com`) is enabled.**
4. **Detects GCR repositories using both:**
    - `gcloud container images list`
    - `gcloud storage buckets list`
5. **Displays results in a readable table format.**
![output.png](https://github.com/damian-sztankowski/Google-Cloud-Open-Resources/blob/main/migrate-to-artifact-registry/output.png?raw=true)

## **🔧 Troubleshooting**

If the script is not detecting GCR repositories correctly:
1. **Manually check for GCR images**:
```bash
gcloud container images list --project PROJECT_ID
```
2. **Check if the storage bucket exists**:
```bash
- `gcloud storage buckets list --project PROJECT_ID`
```
3.  **Ensure your `gcloud` CLI is authenticated**:
```bash
gcloud auth application-default login
```
## **📜 License**

This script is open-source and licensed under **Apache 2.0**.
