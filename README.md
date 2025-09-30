# LibreChat Kubernetes

A comprehensive Kubernetes deployment solution for [LibreChat](https://www.librechat.ai) using Helm charts. This project provides an easy, lightweight template to deploy LibreChat on Kubernetes with all necessary dependencies and configurations.

## Overview

LibreChat is an open-source AI chat platform that supports multiple AI providers. This Kubernetes deployment includes:

- **LibreChat Application** (v0.7.9)
- **MongoDB** (optional, bitnami/mongodb v16.3.0)
- **Meilisearch** (optional, for search functionality)
- **LibreChat RAG API** (optional, for Retrieval-Augmented Generation)

## Prerequisites

### Required Tools

- [Kubernetes](https://kubernetes.io/) cluster (v1.19+)
- [Helm](https://helm.sh/) (v3.0+)
- [kubectl](https://kubernetes.io/docs/tasks/tools/) configured for your cluster

### Required Secrets

**⚠️ IMPORTANT**: LibreChat requires several environment variables to be configured as Kubernetes secrets before installation. These secrets contain sensitive information and must be generated securely. 

#### Core Authentication Secrets

Generate the following secrets using OpenSSL:

```bash
# Generate 32-byte hex values for core secrets
openssl rand -hex 32  # Use for CREDS_KEY
openssl rand -hex 32  # Use for JWT_SECRET  
openssl rand -hex 32  # Use for JWT_REFRESH_SECRET
openssl rand -hex 32  # Use for MEILI_MASTER_KEY

# Generate 16-byte hex value for credentials IV
openssl rand -hex 16  # Use for CREDS_IV
```

#### Automated Secret Creation (Recommended)

Use this bash snippet to automatically generate all required credentials and create the Kubernetes secret:

```bash
#!/bin/bash

# Set your namespace and API keys here
NAMESPACE="librechat"  # Change to your desired namespace

# Generate required credentials
CREDS_KEY=$(openssl rand -hex 32)
CREDS_IV=$(openssl rand -hex 16)
JWT_SECRET=$(openssl rand -hex 32)
JWT_REFRESH_SECRET=$(openssl rand -hex 32)
MEILI_MASTER_KEY=$(openssl rand -hex 32)

echo "Generated credentials:"
echo "CREDS_KEY: $CREDS_KEY"
echo "CREDS_IV: $CREDS_IV"
echo "JWT_SECRET: $JWT_SECRET"
echo "JWT_REFRESH_SECRET: $JWT_REFRESH_SECRET"
echo "MEILI_MASTER_KEY: $MEILI_MASTER_KEY"
echo ""

# Create the Kubernetes secret
kubectl create secret generic librechat-credentials-env \
  --namespace="$NAMESPACE" \
  --from-literal=CREDS_KEY="$CREDS_KEY" \
  --from-literal=CREDS_IV="$CREDS_IV" \
  --from-literal=JWT_SECRET="$JWT_SECRET" \
  --from-literal=JWT_REFRESH_SECRET="$JWT_REFRESH_SECRET" \
  --from-literal=MEILI_MASTER_KEY="$MEILI_MASTER_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Secret 'librechat-credentials-env' created successfully in namespace '$NAMESPACE'"
echo ""
echo "To add additional optional environment variables, you can patch the secret:"
echo "kubectl patch secret librechat-credentials-env -n $NAMESPACE --type='merge' -p='{\"stringData\":{\"EMAIL_SERVICE\":\"Gmail\",\"EMAIL_HOST\":\"smtp.gmail.com\"}}'"
```

**Usage:**
1. Save the script above as `create-librechat-secret.sh`
2. Make it executable: `chmod +x create-librechat-secret.sh`
3. Edit the script to set your namespace and API keys
4. Run the script: `./create-librechat-secret.sh`

#### Manual Secret Creation (Alternative)

If you prefer to create the secret manually, use the following template:

#### Complete Secret Template

Create a Kubernetes secret named `librechat-credentials-env` with the following structure:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: librechat-credentials-env
  namespace: <your-namespace>
type: Opaque
stringData:
  # Core LibreChat Authentication (REQUIRED)
  CREDS_KEY: "<generated-32-byte-hex>"
  CREDS_IV: "<generated-16-byte-hex>"
  JWT_SECRET: "<generated-32-byte-hex>"
  JWT_REFRESH_SECRET: "<generated-32-byte-hex>"
  
  # Search Engine (REQUIRED if using Meilisearch)
  MEILI_MASTER_KEY: "<generated-32-byte-hex>"
```

#### AI Provider Setup

You need at least one AI provider API key. Follow the [LibreChat AI Setup Guide](https://docs.librechat.ai/install/configuration/ai_setup.html) to obtain API keys from your preferred providers:

- **OpenAI**: Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Google**: Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Other providers**: See LibreChat documentation for additional providers

## Installation

### Step 1: Create the Secret

**Option A: Automated Secret Creation (Recommended)**

Use the bash snippet provided above in the "Automated Secret Creation" section:

1. Save the script as `create-librechat-secret.sh`
2. Edit the script to set your namespace and API keys
3. Make it executable: `chmod +x create-librechat-secret.sh`
4. Run the script: `./create-librechat-secret.sh`

**Option B: Manual Secret Creation**

1. Generate your secrets using the OpenSSL commands above
2. Obtain API keys from your chosen AI providers
3. Create the secret YAML file with your values using the template provided
4. Apply the secret to your cluster:

```bash
kubectl apply -f librechat-credentials-env.secret.yaml
```

### Step 2: Add Helm Repository Dependencies

```bash
# Add required Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add meilisearch https://meilisearch.github.io/meilisearch-kubernetes
helm repo update
```

### Step 3: Install Dependencies

```bash
# Update chart dependencies
cd helm/librechat
helm dependency update
```

### Step 4: Configure Values

Create a custom `values.yaml` file or modify the default one in `helm/librechat/values.yaml`. Key configurations include:

```yaml
# Example custom values
image:
  repository: iunera/librechat
  registry: docker.io
  tag: "v0.7.9"

service:
  type: ClusterIP
  port: 3080

ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: librechat.example.com
      paths:
        - path: /
          pathType: Prefix

# Enable/disable dependencies
mongodb:
  enabled: true
  
meilisearch:
  enabled: true
  
librechat-rag-api:
  enabled: false
```

### Step 5: Install the Chart

```bash
# Install with default values
helm install librechat ./helm/librechat

# Or install with custom values
helm install librechat ./helm/librechat -f custom-values.yaml

# Install in specific namespace
helm install librechat ./helm/librechat -n librechat --create-namespace
```

## Configuration

### Environment Variables

LibreChat uses environment variables for configuration. All sensitive variables should be stored in the Kubernetes secret created above. Non-sensitive configuration can be set in the Helm values.

### Dependencies

#### MongoDB
- **Purpose**: Primary database for LibreChat
- **Default**: Enabled with Bitnami MongoDB chart
- **Configuration**: Modify `mongodb` section in values.yaml

#### Meilisearch
- **Purpose**: Search functionality
- **Default**: Enabled
- **Configuration**: Modify `meilisearch` section in values.yaml

#### LibreChat RAG API
- **Purpose**: Retrieval-Augmented Generation capabilities
- **Default**: Disabled
- **Configuration**: Set `librechat-rag-api.enabled: true` in values.yaml

## Accessing LibreChat

After installation, LibreChat will be available at:

- **Service**: `http://<service-name>.<namespace>.svc.cluster.local:3080`
- **Ingress**: `http://<your-configured-hostname>` (if ingress is enabled)
- **Port Forward**: `kubectl port-forward svc/librechat 3080:3080`

## Testing

### Automated Testing

This project includes comprehensive testing using GitHub Actions:

- **Chart Linting**: Validates Helm chart syntax and best practices
- **Integration Testing**: Deploys chart in Kind cluster and runs connectivity tests
- **Multi-platform Testing**: Tests on both AMD64 and ARM64 architectures

### Local Testing

Run the test script to validate your installation:

```bash
# Run full test suite
./helm/librechat/test/test-chart.sh

# Cleanup test resources
./helm/librechat/test/test-chart.sh --cleanup
```

### Manual Testing

```bash
# Check pod status
kubectl get pods -n <namespace>

# Check service
kubectl get svc -n <namespace>

# View logs
kubectl logs -f deployment/librechat -n <namespace>

# Test connectivity
kubectl port-forward svc/librechat 3080:3080 -n <namespace>
# Then visit http://localhost:3080
```

## Troubleshooting

### Common Issues

#### 1. Secret Not Found
```
Error: secret "librechat-credentials-env" not found
```
**Solution**: Ensure the secret is created in the correct namespace before installing the chart.

#### 2. Invalid API Keys
```
Error: Authentication failed for AI provider
```
**Solution**: Verify your API keys are valid and have sufficient quota/permissions.

#### 3. Database Connection Issues
```
Error: Failed to connect to MongoDB
```
**Solution**: Check MongoDB pod status and ensure it's running. Verify connection strings in values.yaml.

#### 4. Missing Environment Variables
```
Error: Required environment variable not set
```
**Solution**: Ensure all required secrets are present in your Kubernetes secret.

### Debug Commands

```bash
# Check secret contents (be careful with sensitive data)
kubectl get secret librechat-credentials-env -o yaml

# Describe pod for events
kubectl describe pod <pod-name>

# Check resource usage
kubectl top pods

# View all resources
kubectl get all -n <namespace>
```

## Development

### Building Custom Images

The project includes a Dockerfile for building custom LibreChat images:

```bash
# Build multi-platform image
docker buildx build --platform linux/amd64,linux/arm64 -t your-registry/librechat:tag .

# Push to registry
docker push your-registry/librechat:tag
```

### Chart Development

When modifying the Helm chart:

1. **Lint the chart**: `helm lint helm/librechat/`
2. **Update version**: Increment version in `Chart.yaml`
3. **Test changes**: Run `./helm/librechat/test/test-chart.sh`
4. **Update dependencies**: `helm dependency update` if needed

## Security Considerations

- **Never commit secrets**: Keep all sensitive values in Kubernetes secrets
- **Use RBAC**: Configure appropriate role-based access controls
- **Network Policies**: Implement network policies to restrict pod communication
- **Image Security**: Regularly update base images and scan for vulnerabilities
- **Secret Rotation**: Regularly rotate API keys and generated secrets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `./helm/librechat/test/test-chart.sh`
5. Submit a pull request

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## Related Projects

Explore other enterprise-grade solutions and tools from iunera:

- **[Druid Cluster Config](https://github.com/iunera/druid-cluster-config)** - Apache Druid cluster configuration and deployment templates
- **[Druid MCP Server](https://github.com/iunera/druid-mcp-server)** - Model Context Protocol server for Apache Druid integration
- **[General Purpose Enterprise RAG](https://github.com/iunera/gerneral-purpose-enterprise-rag)** - Enterprise-ready Retrieval-Augmented Generation solutions
- **[NLWeb](https://github.com/iunera/NLWeb)** - Natural language web interface framework
- **[Apache Druid MCP Server for Conversational AI](https://www.iunera.com/kraken/projects/apache-druid-mcp-server-conversational-ai-for-time-series/)** - Conversational AI integration for time-series data analysis

## Support

- **LibreChat Documentation**: https://docs.librechat.ai
- **LibreChat GitHub**: https://github.com/danny-avila/LibreChat
- **Kubernetes Documentation**: https://kubernetes.io/docs/

## Version Information

- **Chart Version**: 1.8.10
- **LibreChat Version**: v0.7.9
- **Kubernetes**: 1.19+
- **Helm**: 3.0+