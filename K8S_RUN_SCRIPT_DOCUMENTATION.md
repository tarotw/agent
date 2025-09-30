# K8s Run Script Documentation

## Overview

This document describes the implementation of the `k8s-run.sh` shell wrapper script for dynamic Kubernetes pod names in the LibreChat application. This script solves the issue of generating unique pod names for MCP (Model Context Protocol) servers running in Kubernetes environments.

## Problem Statement

The original MCP configuration attempted to use shell command substitution (`$(date +%s)`) directly in YAML configuration, which doesn't work as expected:

```yaml
# This doesn't work - shell commands aren't evaluated in YAML
k8s_linkedin:
  command: kubectl
  args:
    - run
    - --  # Missing pod name
    - --image=stickerdaniel/linkedin-mcp-server:latest
    # ... other args
  env:
    podname: cshtest$(date +%s)  # This isn't used in the kubectl command
```

## Solution

The `k8s-run.sh` script provides a clean wrapper that:
1. Generates unique pod names using timestamp + random suffix
2. Properly constructs kubectl commands with correct syntax
3. Handles multiple environment variables
4. Provides proper error handling and validation
5. Works with Alpine Linux (the base Docker image)

## Files Modified/Created

### 1. `k8s-run.sh` (New File)
A shell script that generates dynamic pod names and executes kubectl commands.

**Key Features:**
- **Unique Pod Names**: Format `mcp-pod-<timestamp>-<random-hex>`
- **Parameter Validation**: Ensures minimum required arguments
- **Environment Variables**: Supports multiple env vars in `KEY=value` format
- **Error Handling**: Validates input and provides helpful error messages
- **Debug Logging**: Shows the generated kubectl command for troubleshooting
- **Portable**: Uses standard Unix tools available in Alpine Linux

**Usage:**
```bash
k8s-run.sh <image> <namespace> [env_var1=value1] [env_var2=value2] ...
```

**Example:**
```bash
k8s-run.sh stickerdaniel/linkedin-mcp-server:latest librechat LINKEDIN_COOKIE=abc123
```

### 2. `Dockerfile` (Modified)
Added installation of the k8s-run.sh script:

```dockerfile
# Copy and install the k8s-run.sh script for dynamic pod name generation
COPY k8s-run.sh /usr/local/bin/k8s-run.sh
RUN chmod +x /usr/local/bin/k8s-run.sh
```

### 3. `.values.yaml` (Modified)
Updated the MCP configuration to use the new script:

**Before:**
```yaml
k8s_linkedin:
  command: kubectl
  args:
    - run
    - --
    - --image=stickerdaniel/linkedin-mcp-server:latest
    # ... complex args
  env:
    podname: cshtest$(date +%s)  # Doesn't work
```

**After:**
```yaml
k8s_linkedin:
  command: k8s-run.sh
  args:
    - stickerdaniel/linkedin-mcp-server:latest
    - librechat
    - LINKEDIN_COOKIE=${LINKEDIN_COOKIE}
  env:
    LINKEDIN_COOKIE: "${LINKEDIN_COOKIE}"
    KUBERNETES_SERVICE_HOST: '10.97.0.1'
    KUBERNETES_SERVICE_PORT: '443'
    KUBERNETES_SERVICE_PORT_HTTPS: '443'
```

## Generated kubectl Commands

The script generates kubectl commands with this structure:

```bash
kubectl run mcp-pod-<timestamp>-<random> \
  --image=<image> \
  --rm \
  -i \
  --restart=Never \
  -n <namespace> \
  --env=<key1>=<value1> \
  --env=<key2>=<value2>
```

**Example Output:**
```bash
kubectl run mcp-pod-1753274161-183a \
  --image=stickerdaniel/linkedin-mcp-server:latest \
  --rm \
  -i \
  --restart=Never \
  -n librechat \
  --env=LINKEDIN_COOKIE=test123
```

## Testing

A test script `test-k8s-run.sh` was created to validate functionality:

```bash
chmod +x test-k8s-run.sh
./test-k8s-run.sh
```

**Test Results:**
- ✅ Basic functionality with required parameters
- ✅ Multiple environment variables handling
- ✅ Error handling for insufficient arguments
- ✅ Warning for invalid environment variable formats
- ✅ Unique pod name generation

## Integration Instructions

### For New Deployments

1. **Build the Docker Image:**
   ```bash
   docker build -t your-registry/librechat:latest .
   ```

2. **Update Helm Values:**
   Configure your MCP servers in `values.yaml`:
   ```yaml
   mcpServers:
     your_mcp_server:
       command: k8s-run.sh
       args:
         - your-image:latest
         - your-namespace
         - ENV_VAR=${YOUR_ENV_VAR}
       env:
         YOUR_ENV_VAR: "${YOUR_VALUE}"
   ```

3. **Deploy with Helm:**
   ```bash
   helm upgrade --install librechat ./helm/librechat -f your-values.yaml
   ```

### For Existing Deployments

1. **Update the codebase** with the new files
2. **Rebuild and push** the Docker image
3. **Update your Helm values** to use `k8s-run.sh` instead of direct kubectl
4. **Upgrade the deployment:**
   ```bash
   helm upgrade librechat ./helm/librechat -f your-values.yaml
   ```

## Usage Examples

### LinkedIn MCP Server
```yaml
k8s_linkedin:
  command: k8s-run.sh
  args:
    - stickerdaniel/linkedin-mcp-server:latest
    - librechat
    - LINKEDIN_COOKIE=${LINKEDIN_COOKIE}
  env:
    LINKEDIN_COOKIE: "${LINKEDIN_COOKIE}"
```

### Custom MCP Server with Multiple Environment Variables
```yaml
custom_mcp:
  command: k8s-run.sh
  args:
    - your-registry/custom-mcp:v1.0
    - production
    - API_KEY=${API_KEY}
    - DEBUG_MODE=${DEBUG_MODE}
    - TIMEOUT=${TIMEOUT}
  env:
    API_KEY: "${YOUR_API_KEY}"
    DEBUG_MODE: "true"
    TIMEOUT: "30"
```

## Troubleshooting

### Debug Information
The script outputs debug information to stderr:
```
[DEBUG] Executing: kubectl run mcp-pod-1753274161-183a --image=...
```

### Common Issues

1. **Script not found**: Ensure the Docker image was rebuilt after adding the script
2. **Permission denied**: The Dockerfile should make the script executable
3. **Invalid environment variables**: Use `KEY=value` format, warnings will be shown for invalid formats
4. **Pod name conflicts**: The timestamp + random suffix should prevent this, but check for clock synchronization issues

### Validation
You can test the script locally:
```bash
# This will show the generated command (kubectl will fail if not in cluster)
./k8s-run.sh nginx:latest default TEST=value
```

## Security Considerations

- The script validates input parameters to prevent command injection
- Environment variables are properly escaped in kubectl commands
- Pod names are generated deterministically but uniquely
- The script runs with the same permissions as the LibreChat container

## Future Enhancements

Potential improvements for future versions:
- Support for additional kubectl flags (resource limits, labels, etc.)
- Configuration file support for complex setups
- Integration with Kubernetes RBAC for fine-grained permissions
- Monitoring and logging integration
- Support for pod templates or custom resource definitions

## Conclusion

The `k8s-run.sh` script successfully resolves the dynamic pod naming issue while providing a clean, reusable solution for MCP server deployments in Kubernetes. The implementation is portable, well-tested, and integrates seamlessly with the existing LibreChat Helm chart structure.