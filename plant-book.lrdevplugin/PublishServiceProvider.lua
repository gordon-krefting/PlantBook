local LrFileUtils = import 'LrFileUtils'
local LrTasks = import 'LrTasks'
local LrView = import 'LrView'
local LrLogger = import 'LrLogger'
local LrPathUtils = import 'LrPathUtils'
local LrExportSession = import 'LrExportSession'

local logger = LrLogger('PlantBookPlugin')
logger:enable("logfile")

local bind = LrView.bind

local exportServiceProvider = {}

-- All the action is here!
function exportServiceProvider.processRenderedPhotos(functionContext, exportContext)

  local exportSettings = assert(exportContext.propertyTable)

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

  LrFileUtils.createAllDirectories(snippetPath)
  LrFileUtils.createAllDirectories(jsonPath)
  LrFileUtils.createAllDirectories(thumbPath)
  LrFileUtils.createAllDirectories(imagePath)

  local remoteHost = exportSettings.remote_host
  assert(not(remoteHost == nil or remoteHost == '') , "Remote host is required")
  
  local remotePath = exportSettings.remote_path
  assert(not(remotePath == nil or remotePath == '') , "Remote path is required")
  
  local password = exportSettings.password
  assert(not(password == nil or password == '') , "Password is required")

  local thumbsToCreate = {}
  -- loop through all photos that have been modified since last publish,
  -- copying them to the local path
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
  end

  -- now do the thumbs
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

  -- do the control file

  -- call main.py

  logger:trace("\n\n\n")

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
    defaultCollectionCanBeDeleted = false,
    canAddCollection = false,
  }
end

-- The user tells us where the photos end up and where
-- the Photo Guide and the Photo Book are built
exportServiceProvider.exportPresetFields = {
  { key = 'local_path', default = "" },
  { key = 'remote_host', default = "" },
  { key = 'password', default = "" },
  { key = 'remote_path', default = "" },
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
        },
      },
      f:row {
        f:static_text {
          title = 'Remote Host:',
        },
        f:edit_field {
          value = bind 'remote_host',
        },
      },
      f:row {
        f:static_text {
          title = 'Password:',
        },
        f:password_field {
          value = bind 'password',
        },
      },
      f:row {
        f:static_text {
          title = 'Remote path:',
        },
        f:edit_field {
          value = bind 'remote_path',
        },
      },
    }
  }
end

return exportServiceProvider
