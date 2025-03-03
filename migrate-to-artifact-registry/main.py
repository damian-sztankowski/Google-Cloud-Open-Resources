import subprocess
import json
import argparse
from tabulate import tabulate
from tqdm import tqdm  # Progress bar

def get_projects(org_id=None, folder_id=None):
    """Get projects in an organization or folder."""
    if folder_id:
        cmd = f"gcloud projects list --filter='parent.id={folder_id}' --format=json"
    elif org_id:
        cmd = f"gcloud projects list --filter='parent.type=organization AND parent.id={org_id}' --format=json"
    else:
        print("Error: You must specify either an organization (-o) or folder (-d).")
        exit(1)

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print("Error fetching projects:", result.stderr)
        return []

    return json.loads(result.stdout) if result.stdout else []

def is_api_enabled(project_id, api_name):
    """Check if a specific API is enabled for the project."""
    cmd = f"gcloud services list --project {project_id} --enabled --format='value(config.name)'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error checking APIs for {project_id}: {result.stderr}")
        return False

    return api_name in result.stdout

def check_gcr_repositories(project_id):
    """Check if GCR repositories exist using storage buckets (fallback method)."""
    cmd_storage = f"gcloud storage buckets list --project {project_id} --format='value(name)'"
    result_storage = subprocess.run(cmd_storage, shell=True, capture_output=True, text=True)

    if result_storage.returncode != 0:
        print(f"Error checking GCR storage buckets for {project_id}: {result_storage.stderr}")
        return False

    gcr_buckets = [b for b in result_storage.stdout.split() if b.startswith(("gcr.io", "eu.artifacts", "us.artifacts", "asia.artifacts"))]
    
    if gcr_buckets:
        return True  # GCR is in use

    # If no storage bucket is found, try the container images list (fallback)
    cmd_gcr = f"gcloud container images list --project {project_id} --format='value(name)'"
    result_gcr = subprocess.run(cmd_gcr, shell=True, capture_output=True, text=True)

    if result_gcr.returncode != 0:
        error_message = result_gcr.stderr.strip()
        if "NAME_UNKNOWN" in error_message:
            return False
        else:
            print(f"Unexpected error checking GCR repositories for {project_id}: {error_message}")
            return False

    return bool(result_gcr.stdout.strip())

def check_project(project_id):
    """Check a single project for GCR and Artifact Registry usage."""
    gcr_enabled = is_api_enabled(project_id, "containerregistry.googleapis.com")
    ar_enabled = is_api_enabled(project_id, "artifactregistry.googleapis.com")
    
    gcr_repos_found = check_gcr_repositories(project_id) if gcr_enabled else False
    
    notes = "Potential migration needed" if gcr_repos_found and not ar_enabled else "Already using Artifact Registry" if ar_enabled else "-"
    
    return [
        project_id,
        "✅ Yes" if gcr_enabled else "❌ No",
        "✅ Yes" if gcr_repos_found else "❌ No",
        "✅ Yes" if ar_enabled else "❌ No",
        notes
    ]

# Argument parsing
parser = argparse.ArgumentParser(description="Check GCR migration readiness for Google Cloud projects.")
parser.add_argument("-o", "--organization", help="Organization ID to scan all projects in the org")
parser.add_argument("-p", "--project", help="Check a single project by Project ID")
parser.add_argument("-d", "--directory", help="Folder ID to scan all projects in a specific folder")

args = parser.parse_args()

data = []

if args.project:
    # Single project mode
    data.append(check_project(args.project))

elif args.organization or args.directory:
    # Scan projects in org or folder
    projects = get_projects(org_id=args.organization, folder_id=args.directory)
    
    if not projects:
        print("No projects found. Check your permissions and IDs.")
        exit()

    use_progress_bar = len(projects) > 1
    for project in (tqdm(projects, desc="Checking projects", unit="project") if use_progress_bar else projects):
        data.append(check_project(project["projectId"]))

else:
    print("Error: You must specify either an organization (-o), a folder (-d), or a project (-p). Use -h for help.")
    exit(1)

# Print the final table
print("\n")
print(tabulate(data, headers=["Project ID", "GCR API Enabled", "GCR Repo Exists", "Artifact Registry API Enabled", "Notes"], tablefmt="grid"))
