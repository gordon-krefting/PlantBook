local LrApplication = import 'LrApplication'
local LrDialogs = import 'LrDialogs'
local LrTasks = import 'LrTasks'
local LrExportSession = import 'LrExportSession'

local LrLogger = import 'LrLogger'
local logger = LrLogger('PlantBookPlugin')
logger:enable("logfile")

local json = require "JSON"

LrTasks.startAsyncTask(function ()
  local found = false
  for _, collection in ipairs(LrApplication.activeCatalog():getChildCollections()) do
    if "Plant Book" == collection:getName() then
      found = true
      ExportBookData(collection)
    end
  end
  if not found then
    LrDialogs.message("Plant Book Error", "No top level collection named 'Plant Book'")
  end
end)

function ExportBookData(collection)
  logger:trace("Exporting data for " .. collection:getName())
  photo_records = {}
  for _, photo in ipairs(collection:getPhotos()) do
    local photo_record = {}
    photo_record.scientificName = photo:getPropertyForPlugin("org.krefting.plant-book", "scientificName")
    photo_record.commonName = photo:getPropertyForPlugin("org.krefting.plant-book", "commonName")
    photo_record.plantType = photo:getPropertyForPlugin("org.krefting.plant-book", "plantType")
    photo_record.location = photo:getPropertyForPlugin("org.krefting.plant-book", "location")
    photo_record.invasive = photo:getPropertyForPlugin("org.krefting.plant-book", "invasive")
    photo_record.rating = photo:getFormattedMetadata("rating")
    photo_record.fileName = photo:getFormattedMetadata("fileName")
    table.insert(photo_records, photo_record)
    logger:trace(json:encode_pretty(photo_record))
  end
  logger:trace(json:encode_pretty(photo_records))
  local file = assert(io.open("/Users/gkreftin/temp/PhotoBook.json", "w"))
  file:write(json:encode_pretty(photo_records))
  file:close()

  -- Do the export
  local params = {}
  params.LR_format = "JPEG"
  params.LR_export_destinationType = "specificFolder"
  params.LR_export_destinationPathPrefix = "/Users/gkreftin/temp/test"
  params.LR_export_useSubfolder = false

  local exportSession = LrExportSession {
    photosToExport = collection:getPhotos(),
    exportSettings = params,
  }
  exportSession:doExportOnCurrentTask()

end
