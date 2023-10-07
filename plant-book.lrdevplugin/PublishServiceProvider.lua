local LrFileUtils = import 'LrFileUtils'
local LrTasks = import 'LrTasks'
local LrView = import 'LrView'
local LrLogger = import 'LrLogger'
local LrPathUtils = import 'LrPathUtils'
local LrExportSession = import 'LrExportSession'

local logger = LrLogger('PlantBookPlugin')
logger:enable("logfile")

local bind = LrView.bind

local json = require "JSON"

local exportServiceProvider = {}

-- All the action is here!
function exportServiceProvider.processRenderedPhotos(functionContext, exportContext)
  local exportSettings = assert(exportContext.propertyTable)

  logger:info('------------------------------------------')
  logger:info('Starting processRenderedPhotos from Provider: ' .. exportSettings.LR_exportServiceProviderTitle)
  logger:info('Description: ' .. exportSettings.LR_publish_connectionName)

  --for k, v in pairs(exportContext) do
  --  logger:trace(k, v)
  --end

  --for k, v in exportSettings:pairs() do
  --  logger:trace(k, v)
  --end

  local localPath = exportSettings.local_path
  assert(not(localPath == nil or localPath == '') , "Local path is required")
  if LrFileUtils.exists(localPath) == nil then
    error("Local path does not exist")
  end

  snippetPath = LrPathUtils.child(localPath, "snippets")
  jsonPath = LrPathUtils.child(localPath, "json")
  publicHtml = LrPathUtils.child(localPath, "public_html")
  imagePath = LrPathUtils.child(publicHtml, "images")
  thumbPath = LrPathUtils.child(publicHtml, "thumbs")
  mainShPath = LrPathUtils.child(LrPathUtils.parent(_PLUGIN.path), 'book_formatter/main.sh')

  LrFileUtils.createAllDirectories(snippetPath)
  LrFileUtils.createAllDirectories(jsonPath)
  LrFileUtils.createAllDirectories(thumbPath)
  LrFileUtils.createAllDirectories(imagePath)

  local remoteHost = exportSettings.remote_host
  assert(not(remoteHost == nil or remoteHost == '') , "Remote host is required")
  
  local remotePath = exportSettings.remote_path
  assert(not(remotePath == nil or remotePath == '') , "Remote path is required")
  
  local thumbsToCreate = {}
  -- loop through all photos that have been modified since last publish,
  -- copying them to the local path
  logger:info('Exporting photos')
  local count = 0
  for i, rendition in exportContext:renditions { stopIfCanceled = true } do
    local success, tempFilePathOrMessage = rendition:waitForRender()
    if success then
      photoFileName = LrPathUtils.leafName(tempFilePathOrMessage)
      destinationPath = LrPathUtils.child(imagePath, photoFileName)

      if LrFileUtils.exists(destinationPath) then
        LrFileUtils.delete(destinationPath)
      end
      LrFileUtils.copy(tempFilePathOrMessage, destinationPath)

      rendition:recordPublishedPhotoId(photoFileName)
      thumbsToCreate[#thumbsToCreate+1] = rendition.photo
    else
      error(tempFilePathOrMessage)
    end
    count = count + 1
  end
  logger:info('Exported ' .. count)

  -- now do the thumbs
  logger:info('Exporting thumbs')
  local params = {}
  params.LR_format = "JPEG"
  params.LR_jpeg_quality = 1
  params.LR_export_destinationType = "specificFolder"
  params.LR_export_destinationPathPrefix = thumbPath
  params.LR_export_useSubfolder = false
  params.LR_size_doConstrain = true
  params.LR_size_doNotEnlarge = true
  params.LR_size_maxHeight = 150
  params.LR_size_maxWidth  = 150
  params.LR_collisionHandling  = "overwrite"

  exportSession = LrExportSession {
    photosToExport = thumbsToCreate,
    exportSettings = params,
  }
  exportSession:doExportOnCurrentTask()
  logger:info('Exported ' .. #thumbsToCreate)

  -- do the control file
  LrTasks.startAsyncTask(function ()
    local found = false
    for _, collection in ipairs(exportContext.publishService:getChildCollections()) do
      if "Plant Photos" == collection:getName() then
        found = true
        logger:info('Exporting control file')
        ExportBookData(collection, jsonPath)
      end
    end
    if not found then
      error("No top level collection named 'Plant Book'")
    end
    cmd = "sh " .. mainShPath .. " " .. localPath .. " " .. remoteHost .. " " .. remotePath
    logger:trace('Calling main.sh: ' .. cmd)
    res = LrTasks.execute(cmd)
    logger:trace('Done calling main.sh: ' .. res)
  end)

end

-- We don't let the user pick any of the photo export settings
exportServiceProvider.showSections = {}
exportServiceProvider.canExportVideo = false
exportServiceProvider.supportsIncrementalPublish = 'only'

function exportServiceProvider.updateExportSettings(exportSettings)
  exportSettings.LR_format = "JPEG"
  exportSettings.LR_jpeg_quality = 1
  exportSettings.LR_size_maxWidth = 2500
  exportSettings.LR_size_maxHeight = 2500
  exportSettings.LR_size_doConstrain = true
  exportSettings.LR_renamingTokensOn = false
  exportSettings.LR_collisionHandling  = "overwrite"
end

function exportServiceProvider.getCollectionBehaviorInfo(publishSettings)
  return {
    defaultCollectionName = "Plant Photos",
    defaultCollectionCanBeDeleted = true,
    canAddCollection = true,
    maxCollectionSetDepth = 0,
  }
end

-- The user tells us where the photos end up and where
-- the Photo Guide and the Photo Book are built
exportServiceProvider.exportPresetFields = {
  {key = 'local_path', default = ''},
  {key = 'remote_host', default = 'gkreftin@krefting.org'},
  {key = 'remote_path', default = ''},
}

function exportServiceProvider.sectionsForTopOfDialog(f, propertyTable)
  return {
    {
      title = "Configuration",
      f:row {
        f:static_text {
          title = 'Local path:',
        },
        f:edit_field {
          value = bind 'local_path',
          width_in_chars = 35,
          wraps = false,
        },
      },
      f:row {
        f:static_text {
          title = 'Remote User@Host:',
        },
        f:edit_field {
          value = bind 'remote_host',
        },
      },
      f:row {
        f:static_text {
          title = 'Remote path:',
        },
        f:edit_field {
          value = bind 'remote_path',
          width_in_chars = 35,
          wraps = false,
        },
      },
    }
  }
end

function ExportBookData(collection, jsonPath)
  logger:trace("Exporting data for " .. collection:getName())

  -- Create the data file
  photo_records = {}
  for _, photo in ipairs(collection:getPhotos()) do
    local photo_record = {}
    photo_record.scientificName = photo:getPropertyForPlugin("org.krefting.plant-book", "scientificName")
    photo_record.commonName = photo:getPropertyForPlugin("org.krefting.plant-book", "commonName")
    photo_record.plantType = photo:getPropertyForPlugin("org.krefting.plant-book", "plantType")
    photo_record.location = photo:getPropertyForPlugin("org.krefting.plant-book", "location")
    photo_record.locationDescription = photo:getPropertyForPlugin("org.krefting.plant-book", "locationDescription")
    photo_record.notes = photo:getPropertyForPlugin("org.krefting.plant-book", "notes")
    photo_record.rating = photo:getFormattedMetadata("rating")
    photo_record.fileName = photo:getFormattedMetadata("fileName")
    photo_record.caption = photo:getFormattedMetadata("caption")
    photo_record.title = photo:getFormattedMetadata("title")
    photo_record.dateTime = photo:getRawMetadata("dateTimeOriginalISO8601")
    photo_record.nativity = photo:getPropertyForPlugin("org.krefting.plant-book", "nativity")
    table.insert(photo_records, photo_record)
  end
  jsonFile = LrPathUtils.child(jsonPath, "PhotoBook.json")
  local file = assert(io.open(jsonFile, "w"))
  file:write(json:encode_pretty(photo_records))
  file:close()
end

return exportServiceProvider
