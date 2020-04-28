# Data Science Activator

## Installation and set up
### Step 1: Install Terraform
Get download and install terraform in your local machine.

Download terraform from https://www.terraform.io/downloads.html.

Move terraform to your directory of interest and set up you path for it

Example: 
```shell script
export PATH=$PATH:/Users/dir_to_terraform/
```

You can add it to your ```.bash_profile```.

### Step 2: Set up your GCP project
 
#### Step 2.1: Create GCP project
Create you project or use an existing project. There are number of ways for GCP
 project creation, but most trivial way is to use GCP consul.

#### Step 2.2: Create GCP Service Account Permissions

* Go to created GCP project 
* Go to the Create Service Account Key page
* From the Service account list, select New service account.
* In the Service account name field, enter a name.
* From the Role list, select Project > Owner.
* Click Create. A JSON file that contains your key downloads to your computer. 
Name the file YOUR_PROJECT.json as an example. Then Download the service account 
json key to somewhere local.

cli equivalents of above steps:
```shell script
    gcloud config set project mssb-sandbox
    gcloud iam service-accounts create data-science-activator
    gcloud projects add-iam-policy-binding mssb-sandbox --member "serviceAccount:data-science-activator@mssb-sandbox.iam.gserviceaccount.com" --role "roles/owner"
    gcloud iam service-accounts keys create data-science-activator.json --iam-account data-science-activator@mssb-sandbox.iam.gserviceaccount.com

```
 
### Step 3: Initiate your project
* Clone data-science-activator
* Follow the instruction to install shared-components first within the package.
* Then you can follow the instruction to install data-landing-zone and data-science-environment