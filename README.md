# Delibird

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