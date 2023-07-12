# UIUCTF-2023-Public

> **Note**  
> This is the repository for all UIUCTF 2023 challenges and infrastructure. This 
is an exact copy of our development repository, minus some deployment secrets 
and git history.

Flag format: `uiuctf{...}`

## For Challenge Devs: Adding a Challenge
- Do you need a container?
  - YES: 
    - cd into `/challenges/<category>`
    - `kctf chal create --template <templatename> <chalname> --challenge-dir ./<chalname>`
    - Available templates: `pwn`, `web`, `xss-bot`
    - Note: the kCTF config is `challenge.yaml` and the CTFd config is `challenge.yml`. Confusing? Yes.
  - NO
    - `mkdir /challenges/<category>/<chalname>`

- Your challenge folder **MUST** have a `challenge.yml` file for CTFd, following the specification [here](https://github.com/CTFd/ctfcli/blob/master/ctfcli/spec/challenge-example.yml)
- Your challenge must have a healthcheck script if it is deployable - attempt to make it solve the challenge
- Your challenge should have a `SOLUTION.md` writeup (it's ok if it's simple/concise or a TL;DR version)

## For Challenge Devs: Local Development for Containerized Challenges

### Initial setup
- Follow kCTF setup instructions [here](https://google.github.io/kctf/local-testing.html)
  - `umask a+x`
  - Install dependencies (CLI tools, Docker)
  - Enable user namespaces:
    - `echo 'kernel.unprivileged_userns_clone=1' | sudo tee -a /etc/sysctl.d/00-local-userns.conf
    - `sudo service procps restart`
- Helpful: `export DOCKER_SCAN_SUGGEST=false` - disables annoying Snyk messages from newer Docker versions which break kCTF parsing

### After initial setup
Every time you open a new shell, you will need to do the following:
- `cd` to root of this repository
- `source kctf/activate`

### Testing locally
- Switch to and start local cluster:
  - `kctf cluster load local-cluster`
  - `kctf cluster start`
- Start challenge and port forward to access it:
  - `kctf chal start`
  - `kctf chal debug port-forward`
- When done testing:
  - `kctf cluster stop` to shutdown local k8s cluster
    - **Do NOT run this command on remote-cluster or you will delete the Google Cloud cluster**
  - `deactivate` to exit ctfcli

### Testing deployed challenge on remote cluster
- Push to repo, and run the kCTF GitHub action
- Switch to remote cluster:
  - `kctf cluster load remote-cluster`
- Port forward to access it:
  - `kctf chal debug port-forward`
- When done testing:
  - `deactivate` to exit ctfcli

## For Infrastructure Admins: Setting Up Google Cloud
These instructions only need to be done once before the CTF.

### Prerequisites
- Install `gcloud`: https://cloud.google.com/sdk/docs/install-sdk
- Authenticate with Google Cloud: `gcloud auth login`
- Follow kCTF setup instructions [here](https://google.github.io/kctf/local-testing.html)

### Set up Kubernetes
Create cluster:
```sh
kctf cluster create --project dotted-forest-314903 --domain-name chal.uiuc.tf --start --email-address sigpwny@gmail.com --zone us-central1-a --registry us.gcr.io remote-cluster --disable-src-ranges
```
Note: `--disable-src-ranges` disables Cloud Armor. To remove, you need the SECURITY_POLICIES quota.

Resize cluster (to reduce costs before CTF starts):
```sh
kctf cluster resize --min-nodes 1 --max-nodes 1 --num-nodes 1 --machine-type e2-standard-4 --pool-name default-pool --spot
```

#### Test challenge deployment

`cd` to a challenge folder with a deployment `challenge.yaml` file and run the following:
``` sh
kctf chal start
```

### Set up CTFd

#### Enable services
You may need to enable SQL and Redis services. Run the following commands. If you see a prompt like `API [sqladmin.googleapis.com] not enabled on project [648434879266]. Would you like to enable and retry (this will take a few minutes)? (y/N)?`, press `y`.
```sh
gcloud sql instances list
gcloud redis instances list --region us-central1
```

#### Setup script
Run from the root directory:
``` sh
./ctfd/chal setup
```

#### Setting up CI/CD

GitHub Actions needs some secrets to automatically sync with the CTFd instance. After creating a CTFd admin account, go to http://<ctfd-ip>/settings#tokens to obtain a token.

From the root of the repository, create the `.ctf/config` file with the new IP and token. Note that you need `git-crypt` to unlock and edit the file. These credentials will be automatically used by the GitHub Actions workflow to connect to CTFd and sync/install challenges.
