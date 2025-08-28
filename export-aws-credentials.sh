#!/bin/bash

set -euo pipefail

aws_credentials=$(gds aws govuk-test-developer -e --art 8h)
relevant_credentials=$(echo "$aws_credentials" | grep '^export ' | sed -E 's/^export (.*);$/\1/')
printf "%s\n" "$relevant_credentials" > .env.aws

echo "Written credentials to .env.aws"
