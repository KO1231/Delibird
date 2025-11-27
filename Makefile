MAKEFILE_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

init-%:
	ENV_NAME=$* && \
	if [ ! -d "$(MAKEFILE_DIR)/environments/$$ENV_NAME" ]; then \
		echo "Error: Environment '$$ENV_NAME' does not exist."; \
		exit 1; \
	fi; \
	if [ -f "$(MAKEFILE_DIR)/environments/$$ENV_NAME/config.yml" ]; then \
		if [ ! -d "$(MAKEFILE_DIR)/environments/$$ENV_NAME/.terraform" ]; then \
			cd $(MAKEFILE_DIR)/environments/$$ENV_NAME && terraform init; \
		else \
			echo "Terraform is already initialized for environment '$$ENV_NAME'."; \
		fi; \
	else \
		echo "Error: Configuration file not found for environment '$$ENV_NAME'."; \
		exit 1; \
	fi


plan-%:
	ENV_NAME=$* && \
	if [ ! -d "$(MAKEFILE_DIR)/environments/$$ENV_NAME" ]; then \
		echo "Error: Environment '$$ENV_NAME' does not exist."; \
		exit 1; \
	fi && \
	if [ -d "$(MAKEFILE_DIR)/environments/$$ENV_NAME/.terraform" ]; then \
	  	rm -f $(MAKEFILE_DIR)/environments/$$ENV_NAME/.plan && \
		cd $(MAKEFILE_DIR)/environments/$$ENV_NAME && \
		terraform plan -out .plan && \
		APPLYABLE=$$(terraform show -json .plan | jq '.applyable') && \
		if [ "$$APPLYABLE" = "false" ]; then \
			rm -f .plan; \
		fi; \
	else \
		echo "Error: Terraform is not initialized for environment '$$ENV_NAME'. Please run 'make init-$$ENV_NAME' first."; \
		exit 1; \
	fi

plan:
	@make plan-dev
	@make plan-prod

apply-%:
	ENV_NAME=$* && \
	cd $(MAKEFILE_DIR)/environments/$$ENV_NAME && terraform show .plan && terraform apply .plan && \
	rm -f .plan