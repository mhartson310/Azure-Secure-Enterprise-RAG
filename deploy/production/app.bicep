targetScope = 'resourceGroup'

@description('Container App name.')
param appName string = 'secure-rag-api'

@description('Azure region. Use the same region as the Container Apps environment.')
param location string = resourceGroup().location

@description('Existing Container Apps environment resource ID from the production platform deployment.')
param managedEnvironmentId string

@description('Existing application user-assigned managed identity resource ID.')
param appIdentityResourceId string

@description('Existing application user-assigned managed identity client ID.')
param appIdentityClientId string

@description('Azure Container Registry login server, for example myregistry.azurecr.io.')
param registryServer string

@description('Full container image reference, for example myregistry.azurecr.io/secure-rag-api:v1.')
param appImage string

@description('Azure AI Search endpoint.')
param searchEndpoint string

@description('Azure AI Search index name.')
param searchIndex string = 'enterprise-rag-demo'

@description('Azure OpenAI-compatible endpoint for the deployed model.')
param openaiEndpoint string

@description('Azure OpenAI / Foundry model deployment name.')
param openaiDeployment string

@description('Azure OpenAI API version used by the reference app.')
param openaiApiVersion string = '2024-10-21'

@description('Identity mode used by the application. easy_auth expects a trusted platform-injected client principal.')
@allowed([
  'easy_auth'
  'debug'
])
param identityMode string = 'easy_auth'

@description('Minimum number of running replicas.')
@minValue(1)
param minReplicas int = 1

@description('Maximum number of running replicas.')
@minValue(1)
param maxReplicas int = 3

@description('Optional tags.')
param tags object = {
  workload: 'secure-enterprise-rag'
  component: 'api'
  environment: 'production'
  managedBy: 'bicep'
}

resource app 'Microsoft.App/containerApps@2025-07-01' = {
  name: appName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${appIdentityResourceId}': {}
    }
  }
  properties: {
    managedEnvironmentId: managedEnvironmentId
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        allowInsecure: false
        targetPort: 8000
        transport: 'auto'
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      registries: [
        {
          server: registryServer
          identity: appIdentityResourceId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: appImage
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: appIdentityClientId
            }
            {
              name: 'AZURE_SEARCH_ENDPOINT'
              value: searchEndpoint
            }
            {
              name: 'AZURE_SEARCH_INDEX'
              value: searchIndex
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: openaiEndpoint
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT'
              value: openaiDeployment
            }
            {
              name: 'AZURE_OPENAI_API_VERSION'
              value: openaiApiVersion
            }
            {
              name: 'IDENTITY_MODE'
              value: identityMode
            }
            {
              name: 'ALLOW_DEBUG_IDENTITY'
              value: 'false'
            }
            {
              name: 'SEARCH_TOP_K'
              value: '5'
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/healthz'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 10
              periodSeconds: 30
              timeoutSeconds: 5
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/healthz'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 5
              periodSeconds: 10
              timeoutSeconds: 5
              failureThreshold: 3
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
  tags: tags
}

output containerAppName string = app.name
output containerAppFqdn string = app.properties.configuration.ingress.fqdn
output containerAppUrl string = 'https://${app.properties.configuration.ingress.fqdn}'
