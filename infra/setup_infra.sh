# run setup_infra.sh

# terrraform apply with argument -auto-approve just auto yes's the
# prompt apply changes
terraform init
terraform fmt
terraform apply -auto-approve