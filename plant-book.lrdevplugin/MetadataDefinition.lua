return {
  schemaVersion = 1,

  metadataFieldsForPhotos = {
    {dataType="string", searchable=true, browsable=true, id="scientificName", title="Scientific Name", version=1},
    {dataType="string", searchable=true, browsable=true, id="commonName",     title="Common Name",     version=1},
    {dataType="enum",   searchable=true, browsable=true, id="location",       title="Location",        version=1, values = {
      {value=nil,            title="-"},
      {value='backyard',     title="Back Yard"},
      {value='frontyard',    title="Front Yard"},
      {value='meadow',       title="Meadow"},
      {value='meadowgarden', title="Meadow Garden"},
      {value='pondarea',     title="Pond Area"},
      {value='slopegarden',  title="Slope Garden"},
      {value='other',        title="Other"},
    },},
    {dataType="enum",   searchable=true, browsable=true, id="plantType",      title="Plant Type",      version=1, values = {
      {value=nil,            title="-"},
      {value='tree',         title="Trees"},
      {value='shrub',        title="Shrubs"},
      {value='forb',         title="Forbs"},
      {value='fern',         title="Ferns"},
      {value='fungus',       title="Fungi"},
      {value='grass',        title="Grasses, Sedges and Rushes"},
      {value='vine',         title="Vines"},
    },},
    {dataType="enum",   searchable=true, browsable=true, id="invasive",       title="Invasive",        version=1, values = {
      {value=nil,            title="-"},
      {value='no',           title="No"},
      {value='yes',          title="Yes"},
    },},
  },
}
