Workflows
----------
This document explains our GitHub workflows and team strategies for managing them.

1) For making commits
    - Work happens on a branch, never directly on `main`.
    - Name branches after what they do, e.g. `documentation` or `workflow`.
    - Write commit messages that describe what changed and why, not just "fix" or "update".
    - Open a pull request into `main` when the branch is ready. At least one other team member must review and approve it before it can merge.
    - A PR can't merge unless it passes both CI checks (below): pytest and ruff. If either fails, fix it on the branch and push again. 

2) Continuous integration (CI)
   We have two GitHub Actions workflows that run automatically on every push and every pull request targeting `main`.
   **Tests (`runPythonTests.yml`)**
   Runs our pytest suite on every push and PR, so a broken test can't merge into `main` unnoticed. It also spins up a real, throwaway Postgres database container for the duration of the run. 
   **Lint (`RunRuff`)**
   Runs Ruff against the codebase on every push and PR, checking both for lint issues (unused imports, style problems, etc.) and that code is formatted consistently.

3) Deploying

   - We have a third workflow, `Deploy on AWS`, that SSH into our EC2 instance and runs `scripts/redeploy.sh` to pull the latest code and restart the app. Unlike the two CI workflows above, it only runs when manually triggered from the Actions tab.
   It never runs automatically on push or merge, since we don't want every merge to `main` to immediately redeploy the live app.

   **Setting up the GitHub secrets this workflow needs:**

   The workflow connects to EC2 using two repository secrets: the instance's public IP, and the private key used to SSH into it. These are stored encrypted by GitHub and are only ever exposed to workflow runs, never visible in logs or to anyone browsing the repo.

   To add them:
    1. Go to the repository on GitHub.
    2. Open **Settings** → **Secrets and variables** → **Actions**.
    3. Click **New repository secret**.
    4. Add `PUBLICIP`, with the value set to the EC2 instance's public IP address.
    5. Add `LABSUSERPEM`, with the value set to the full contents of the `.pem` private key file used to SSH into the instance.

