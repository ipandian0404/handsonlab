targetScope = 'resourceGroup'

@minLength(1)
@maxLength(40)
@description('Name of the azd environment used to identify deployed resources.')
param environmentName string

@description('Azure region for all resources.')
param location string = 'southafricanorth'

@allowed([
  'B1'
  'S1'
  'P0v3'
])
@description('App Service plan SKU. B1 is suitable for this low-traffic training site.')
param appServicePlanSku string = 'B1'

var resourceToken = toLower(uniqueString(subscription().id, resourceGroup().id, environmentName))
var tags = {
  'azd-env-name': environmentName
  application: 'momentum-copilot-race'
}
var webAppTags = union(tags, {
  'azd-service-name': 'web'
})
var planName = 'asp-${environmentName}-${resourceToken}'
var webAppName = 'app-momentum-race-${resourceToken}'
var logAnalyticsName = 'log-${environmentName}-${resourceToken}'
var applicationInsightsName = 'appi-${environmentName}-${resourceToken}'

module logAnalytics 'br/public:avm/res/operational-insights/workspace:0.16.1' = {
  params: {
    name: logAnalyticsName
    location: location
    dataRetention: 30
    tags: tags
  }
}

module applicationInsights 'br/public:avm/res/insights/component:0.8.0' = {
  params: {
    name: applicationInsightsName
    location: location
    workspaceResourceId: logAnalytics.outputs.resourceId
    applicationType: 'web'
    tags: tags
  }
}

module appServicePlan 'br/public:avm/res/web/serverfarm:0.7.0' = {
  params: {
    name: planName
    location: location
    kind: 'linux'
    reserved: true
    skuName: appServicePlanSku
    skuCapacity: 1
    tags: tags
  }
}

module webApp 'br/public:avm/res/web/site:0.24.0' = {
  params: {
    name: webAppName
    location: location
    kind: 'app,linux'
    serverFarmResourceId: appServicePlan.outputs.resourceId
    httpsOnly: true
    clientAffinityEnabled: false
    publicNetworkAccess: 'Enabled'
    configs: [
      {
        name: 'appsettings'
        properties: {
          APPLICATIONINSIGHTS_CONNECTION_STRING: applicationInsights.outputs.connectionString
          ENABLE_ORYX_BUILD: 'false'
          SCM_DO_BUILD_DURING_DEPLOYMENT: 'false'
        }
      }
    ]
    siteConfig: {
      alwaysOn: true
      appCommandLine: 'python app.py'
      ftpsState: 'Disabled'
      healthCheckPath: '/health'
      http20Enabled: true
      linuxFxVersion: 'PYTHON|3.12'
      minTlsVersion: '1.2'
      remoteDebuggingEnabled: false
    }
    tags: webAppTags
  }
}

output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP_NAME string = resourceGroup().name
output AZURE_SUBSCRIPTION_ID string = subscription().subscriptionId
output SERVICE_WEB_NAME string = webApp.outputs.name
output SERVICE_WEB_URI string = 'https://${webApp.outputs.defaultHostname}'