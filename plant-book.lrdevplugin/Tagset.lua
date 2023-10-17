return {
  id = 'plant-book-tagset',
  title = 'Plant Book',
  items = {
    {'com.adobe.label', label = "Species Information"},
    'org.krefting.plant-book.scientificName',
    'org.krefting.plant-book.commonName',
    'org.krefting.plant-book.idConfidence',
    'org.krefting.plant-book.plantType',
    'org.krefting.plant-book.nativity',
    {'org.krefting.plant-book.notes', height_in_lines = 3},
    'com.adobe.separator',
    {'com.adobe.label', label = "Specimen Information"},
    'org.krefting.plant-book.location',
    {'org.krefting.plant-book.locationDescription', height_in_lines = 3},
    'org.krefting.plant-book.introduced',
    'org.krefting.plant-book.introductionYear',
    'com.adobe.separator',
    {'com.adobe.label', label = "Photo Data"},
    {'com.adobe.caption', height_in_lines = 3},
    'com.adobe.dateTimeOriginal',
    'com.adobe.GPS',
  }
}
