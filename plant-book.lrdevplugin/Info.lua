return {
  VERSION = { major=0, minor=1, revision=0, },

  LrSdkVersion = 9.0,
  LrSdkMinimumVersion = 4.0,

  LrToolkitIdentifier = "org.krefting.plant-book",
  LrPluginName = "Plant Book",
  LrPluginInfoUrl="http://krefting.org/",

  LrMetadataProvider = 'MetadataDefinition.lua',
  LrMetadataTagsetFactory = 'Tagset.lua',

  LrExportServiceProvider = {
    title = "Plant Book",
    file = "PublishServiceProvider.lua",
  },
}
