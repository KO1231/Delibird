# Delibird
Delibird is a URL shortening system with various features such as measurement, password protection, and redirects with digital signatures, in addition to simple redirection.

This application supports custom domains, enabling domain-specific management pages and user management, and can be implemented with a fully serverless architecture using AWS Lambda.

It allows you to deploy your own shortened link service with full access to all features, delivering far superior cost performance compared to existing cloud-based shortening services.

<img width="1512" height="753" alt="Delibird" src="https://github.com/user-attachments/assets/acbc692e-908d-42c7-b69a-53a24ea75231" />


## Requirements

- Python 3.13.9
    - pyenv (recommended)
    - pipenv
- Terraform v1.14.0
    - tfenv (recommended)

## Installation

1. (If you use pyenv, and did not install Python 3.13.5 yet)
   ```bash
   pyenv install 3.13.5
   ```

2. (If you use tfenv, and did not install Terraform v1.14.0 yet)
   ```bash
   tfenv install 1.14.0
   ```

2. Clone this repository
   ```bash
    git clone https://github.com/KO1231/Delibird.git
    cd Delibird
    ```

3. Install dependencies using pipenv
   ```bash
   pip3 install pipenv
   pipenv install
   ```

4. Create environment
    - Create a environments file in environments directory based on sample environment.

5. Initialize Terraform
    - If you create `dev` environment (create `environments/dev`), run following command with `dev` environment name.
      <br>

   ```bash
   make init-{environment name}
   ```

## Deployment

```bash
make plan-{environment name}
```

```bash
make apply-{environment name}
```
