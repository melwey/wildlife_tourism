# map
# remove all layers
QgsProject.instance().removeMapLayer(regionLayer)
QgsProject.instance().removeMapLayer(regionPaLayer)

## Background: mapbox
#uri = "crs=EPSG:3857&format&type=xyz&url=https://api.mapbox.com/styles/v1/mboni/cj978emxv180k2rmtgsz6i1b4/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWJvbmkiLCJhIjoiY2lzOHNzcWJtMDA0ODJ6czQ2eXQxOXNqeCJ9.geDRSQxeQQQkKDN9bZWeuw"
#mapboxLayer = QgsRasterLayer(uri, "mapbox", 'wms')
#if not mapboxLayer.isValid():
#    print("Mapbox failed to load!")
#mapbox = project.addMapLayer(mapboxLayer)

# Background: Esri light
#uri = "url=http://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D&zmax=19&zmin=0&type=xyz"
#mts_layer=QgsRasterLayer(uri,'Background: ESRI World Light Gray','wms')
#if not mts_layer.isValid():
#    print ("Layer failed to load!")

uri = "url=http://basemaps.cartocdn.com/light_all/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&type=xyz"
mts_layer=QgsRasterLayer(uri,'Background: CartoDb Positron','wms')

esri = project.addMapLayer(mts_layer)

colours = {
    'glwd': '#36aa49',
    'coral': '#e65025',
    'gmba': '#720f11''
    }
layers = dict()
extent = NULL
for name in colours.keys():
    try:
        layer = iface.addVectorLayer('./' + region + '/' + name + 'I_' + region + '.geojson', name, 'ogr')
        layers[name] = layer
        layer.setName(name + " distribution")
        renderer = layer.renderer() #singleSymbol renderer
        symLayer = QgsSimpleFillSymbolLayer.create({'color':colours[name], 'outline_style': 'no'})
        renderer.symbols(QgsRenderContext())[0].changeSymbolLayer(0,symLayer)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        iface.layerTreeView().refreshLayerSymbology(layer.id())
        # get extent and combine
        if extent.isNull():
            extent = layer.extent()
        else:
            extent.combineExtentWith(layer.extent())
    except:
        pass

# show PA
regionPaLayer = iface.addVectorLayer("./" + region + "/" + region+"wdpa_o25_coastORmarine.geojson", 
    "pa", "ogr")
regionPaLayer.setName("Marine and coastal protected areas _n\n(WDPA Jul 2018/JRC)")
renderer = regionPaLayer.renderer() #singleSymbol renderer
symLayer = QgsSimpleFillSymbolLayer.create({'color':'255,255,255,100', 'outline_color': '#70b6d1'})
renderer.symbols(QgsRenderContext())[0].changeSymbolLayer(0,symLayer)
regionPaLayer.setRenderer(renderer)
regionPaLayer.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(regionPaLayer.id())

# region layer
regionLayer = iface.addVectorLayer('./' + region + '/' + region + ".geojson", 
    "region", "ogr")
regionLayer.setName("East and Southern Africa _n\n(GAUL and EEZ)")
renderer = regionLayer.renderer() #singleSymbol renderer
symLayer = QgsSimpleFillSymbolLayer.create({'color':'250,250,250,10', 'outline_color': '#91af90'})
renderer.symbols(QgsRenderContext())[0].changeSymbolLayer(0,symLayer)
regionLayer.setRenderer(renderer)
regionLayer.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(regionLayer.id())

# Set canvas extent
canvas = iface.mapCanvas()
# zoom to coral, mangrove and seeagrass combined extent
# set CRS to WGS84
project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
# zoom to extent
canvas.setExtent(extent.buffered(0.08))
# # or zoom to single country
# eez.selectByExpression('"ISO_Ter1" = \'KEN\'', QgsVectorLayer.SetSelection)
# # zoom to selected features
# canvas.setExtent(eez.boundingBoxOfSelected().buffered(0.08))
# # deselect features
# eez.removeSelection()
# set CRS to native Mapbox (pseudo Mecator)
project.setCrs(QgsCoordinateReferenceSystem("EPSG:3857"))


# print layout
# get a reference to the layout manager
manager = project.layoutManager()
#make a new print layout object
layout = QgsPrintLayout(project)
#needs to call this according to API documentaiton
layout.initializeDefaults()
#cosmetic
layout.setName('map_coral_seagrass_mangrove_pa')
#add layout to manager
manager.addLayout(layout)

#create a map item to add
itemMap = QgsLayoutItemMap.create(layout)
# lock layers
itemMap.setLayers([regionPaLayer, layers['mangrove'], layers['coral'], layers['seagrass'], regionLayer, esri])
itemMap.setKeepLayerSet(True)

# add to layout
layout.addLayoutItem(itemMap)
# set size
itemMap.attemptResize(QgsLayoutSize(257, 170, QgsUnitTypes.LayoutMillimeters))
itemMap.attemptMove(QgsLayoutPoint(20,15,QgsUnitTypes.LayoutMillimeters))
itemMap.setExtent(canvas.extent())

# add grid linked to map
itemMap.grid().setName("graticule")
itemMap.grid().setEnabled(True)
itemMap.grid().setStyle(QgsLayoutItemMapGrid.FrameAnnotationsOnly)
itemMap.grid().setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
itemMap.grid().setIntervalX(5)
itemMap.grid().setIntervalY(2)
itemMap.grid().setAnnotationEnabled(True)
itemMap.grid().setFrameStyle(QgsLayoutItemMapGrid.InteriorTicks)
itemMap.grid().setFramePenSize(0.5)
itemMap.grid().setAnnotationFormat(1) # DegreeMinuteSuffix
itemMap.grid().setAnnotationPrecision(0) # integer
#itemMap.grid().setBlendMode(QPainter.CompositionMode_SourceOver) # ?

# Legend
itemLegend = QgsLayoutItemLegend.create(layout)
itemLegend.setAutoUpdateModel(False)
itemLegend.setLinkedMap(itemMap)
itemLegend.setLegendFilterByMapEnabled(True)
itemLegend.setTitle(region)
itemLegend.setWrapString('_n')
itemLegend.setResizeToContents(False)
itemLegend.attemptResize(QgsLayoutSize(85, 65, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemLegend)
itemLegend.attemptMove(QgsLayoutPoint(205,10,QgsUnitTypes.LayoutMillimeters))

# text box
itemLabel = QgsLayoutItemLabel.create(layout)
itemLabel.setText("Coordinate Reference System: [% @project_crs %] \nData sources: \nhttp://data.unep-wcmc.org/datasets/ \nhttps://www.protectedplanet.net/")
#itemLabel.adjustSizeToText()
itemLabel.setFixedSize(QgsLayoutSize(100,25,QgsUnitTypes.LayoutMillimeters))
itemLabel.attemptMove(QgsLayoutPoint(15,185,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemLabel)

# North arrow
itemNorth = QgsLayoutItemPicture.create(layout)
itemNorth.setPicturePath("C:/PROGRA~1/QGIS3~1.2/apps/qgis/svg/arrows/NorthArrow_04.svg")
itemNorth.setFixedSize(QgsLayoutSize(10,10,QgsUnitTypes.LayoutMillimeters))
itemNorth.attemptMove(QgsLayoutPoint(250,160,QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(itemNorth)

# BIOPAMA logo
itemLogo = QgsLayoutItemPicture.create(layout)
itemLogo.setPicturePath("../../DOC/pen_biopama_logo_1.png")
layout.addLayoutItem(itemLogo)
itemLogo.setFixedSize(QgsLayoutSize(50,10,QgsUnitTypes.LayoutMillimeters))
itemLogo.attemptMove(QgsLayoutPoint(230,190,QgsUnitTypes.LayoutMillimeters))

# print to png
export = QgsLayoutExporter(layout)
expSett = QgsLayoutExporter.ImageExportSettings()
expSett.dpi = 150
export.exportToImage("./" + region + "/" + layout.name() + "_" + region + ".png", expSett)

#'modSeagrass': '#36aa49'
# add modSeagrass to map
layers['modSeagrass'].setName("Modelled seagrass suitability")

# new print layout
layout1 = manager.duplicateLayout(layout, 'map_modelled_seagrass_pa')
# get mapItem and edit italic
# mapItem type = 65639
for item in layout1.items():
    # Map
    if item.type() == 65639:
        item.setKeepLayerSet(False)
        item.setLayers([regionLayer, regionPaLayer, layers['modSeagrass'], esri])
        item.setKeepLayerSet(True)
        item.refresh()
    # Legend    
    if item.type() == 65642:
        item.attemptResize(QgsLayoutSize(85, 55, QgsUnitTypes.LayoutMillimeters))

# Export print layout
export = QgsLayoutExporter(layout1)
export.exportToImage("./" + region + "/" + layout1.name() + "_" + region + ".png", expSett)

# 
layout2 = manager.duplicateLayout(layout, 'map_pa')
for item in layout2.items():
    # Map
    if item.type() == 65639:
        item.setKeepLayerSet(False)
        item.setLayers([regionPaLayer, regionLayer, esri])
        item.setKeepLayerSet(True)
        item.refresh()
    # Legend    
    if item.type() == 65642:
        item.attemptResize(QgsLayoutSize(85, 45, QgsUnitTypes.LayoutMillimeters))

# Export print layout
export = QgsLayoutExporter(layout2)
export.exportToImage("./" + region + "/" + layout2.name() + "_" + region + ".png", expSett)

