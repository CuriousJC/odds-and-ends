# Read the environment data from env.yaml based on the selected environment
environment_data=$(yq eval '.environment[] | select(.name == "'"$selected_environment"'")' "env.yaml")

# Check if the environment exists in the YAML
if [ -z "$environment_data" ]; then
    echo "Environment '$selected_environment' not found in env.yaml."
    exit 1
fi

# Iterate through the tokens within the selected environment
for token_data in $(echo "$environment_data" | yq eval '.tokens[]'); do
    token=$(echo "$token_data" | yq eval '.token')
    value=$(echo "$token_data" | yq eval '.value')

    # Iterate through the YAML files in the directory
    for yaml_file in "$yaml_directory"/*.yaml; do
        # Replace the token with the value in the YAML file
        sed -i "s/||$token||/$value/g" "$yaml_file"
    done

    echo "Replaced tokens for token '$token' with value '$value'."
done

echo "Token replacement for environment '$selected_environment' complete."