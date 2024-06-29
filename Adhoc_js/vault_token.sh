#!/bin/sh
set -e
export VAULT_TOKEN=$(aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:eu-west-1:483013340174:secret:campaign/provisioning/vault_token-zsAW8Q  --query SecretString --output text  --region eu-west-1 |  tr { '\n' | tr , '\n' | tr } '\n' | grep 'VAULT_TOKEN' | awk  -F'"' '{print $4}')
