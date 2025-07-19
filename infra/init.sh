# run setup_infra.sh

# terrraform apply with argument -auto-approve just auto yes's the
# prompt apply changes. Note the way to refer to bash arguments
# is like variables where the variable is preceded by a $ char
if [ $1 == "setup" ]; then
    echo "Initiating infrastructure build"
    terraform init
    terraform fmt
    terraform apply -auto-approve

elif [ $1 == "destroy" ]; then
    echo "Initiating infrastructure destruction"
    terraform destroy -auto-approve

else
    echo "No command executed. Please use 'setup' or 'destroy' as an argument."

fi