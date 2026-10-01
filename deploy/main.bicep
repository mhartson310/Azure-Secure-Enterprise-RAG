targetScope = 'resourceGroup'

@description('Base name used to generate globally unique resource names.')
@minLength(3)
@maxLength(20)
param baseName string = 'securerag'

@description('Azure region. Confirm Microsoft Foundry/model availability in your selected region before deploying a model.')
param location string = resourceGroup().location

@description('Azure AI Search SKU. Use free for the cheapest learning path; use basic or higher for capabilities not available on Free, including Private Link.')
@allowed([
  'free'
  'basic'
  'standard'
])
param searchSku string = 'free'

@description('Enable semantic ranker on the search service. Free is appropriate for a small lab.')
param semanticSearch string = 'free'

@description('Create a Microsoft Foundry / Azure AI Services resource. No model deployment is created by this template.')
param deployFoundry bool = true

@description('Keep public access enabled for the low-friction lab. Production deployments should evaluate Private Link and network isolation.')
param publicNetworkAccess string = 'Enabled'

@description('Allow API-key authentication to Search in addition to Microsoft Entra ID. Set true only after your RBAC path is tested.')
param disableSearchLocalAuth bool = false

@description('Optional tags applied to resources.')
param tags object = {
  workload: 'secure-enterprise-rag'
  environment: 'lab'
  managedBy: 'bicep'
}

var suffix = uniqueString(resourceGroup().id, baseName)
var searchName = toLower('srch-${baseName}-${suffix}')
var foundryName = toLower('ai-${baseName}-${suffix}')

resource search 'Microsoft.Search/searchServices@2025-05-01' = {
  name: searchName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: searchSku
  }
  properties: {
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
    disableLocalAuth: disableSearchLocalAuth
    encryptionWithCmk: {
      enforcement: 'Disabled'
    }
    hostingMode: 'default'
    networkRuleSet: {
      bypass: 'None'
      ipRules: []
    }
    partitionCount: 1
    publicNetworkAccess: publicNetworkAccess
    replicaCount: 1
    semanticSearch: semanticSearch
  }
  tags: tags
}

resource foundry 'Microsoft.CognitiveServices/accounts@2026-07-01' = if (deployFoundry) {
  name: foundryName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: foundryName
    publicNetworkAccess: publicNetworkAccess
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
  tags: tags
}

output searchServiceName string = search.name
output searchEndpoint string = 'https://${search.name}.search.windows.net'
output searchPrincipalId string = search.identity.principalId
output foundryResourceName string = deployFoundry ? foundry.name : ''
output foundryEndpoint string = deployFoundry ? 'https://${foundry.name}.cognitiveservices.azure.com/' : ''
output foundryPrincipalId string = deployFoundry ? foundry.identity.principalId : ''
