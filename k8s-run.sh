#!/bin/sh

# k8s-run.sh - Shell wrapper script for dynamic Kubernetes pod names
# Usage: k8s-run.sh <image> <namespace> [env_var1=value1] [env_var2=value2] ...
#
# This script generates a unique pod name using timestamp and runs a temporary
# Kubernetes pod with the specified image, namespace, and environment variables.

set -e

# Check if minimum required arguments are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <image> <namespace> [env_var1=value1] [env_var2=value2] ..." >&2
    echo "Example: $0 stickerdaniel/linkedin-mcp-server:latest librechat LINKEDIN_COOKIE=abc123" >&2
    exit 1
fi

# Parse arguments
IMAGE="$1"
NAMESPACE="$2"
shift 2

# Generate unique pod name using timestamp and random suffix for extra uniqueness
TIMESTAMP=$(date +%s)
# Use a more portable method for random suffix generation
RANDOM_SUFFIX=$(od -An -N2 -tx1 /dev/urandom | tr -d ' ' | head -c 4)
POD_NAME="mcp-pod-${TIMESTAMP}-${RANDOM_SUFFIX}"

# Build kubectl command
KUBECTL_CMD="kubectl run ${POD_NAME}"
KUBECTL_CMD="${KUBECTL_CMD} --image=${IMAGE}"
KUBECTL_CMD="${KUBECTL_CMD} --rm"
KUBECTL_CMD="${KUBECTL_CMD} -i"
KUBECTL_CMD="${KUBECTL_CMD} --restart=Never"
KUBECTL_CMD="${KUBECTL_CMD} -n ${NAMESPACE}"

# Add environment variables if provided
for env_var in "$@"; do
    if echo "$env_var" | grep -q "="; then
        KUBECTL_CMD="${KUBECTL_CMD} --env=${env_var}"
    else
        echo "Warning: Ignoring invalid environment variable format: $env_var" >&2
    fi
done

# Log the command being executed (for debugging)
echo "[DEBUG] Executing: $KUBECTL_CMD" >&2

# Execute the kubectl command
# Use exec to replace the shell process and properly handle stdin/stdout
exec sh -c "$KUBECTL_CMD"