# Landscape features indicator for Wildlife economy potential
# Mélanie Weynants, Claudia Capitani, Philipp Schaegner
# August 2020

import qgis.utils
from qgis.gui import *

import processing
import numpy as np
import os
# set current directory
os.chdir("/Users/mela/Documents/JRC/BIOPAMA/ESS/wildlife_tourism/pyCode")

# Get the project instance
project = QgsProject.instance()
# set CRS to Mollweide to do the buffers
project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
# Draw layers with missing projection in project's CRS
settings = QSettings()
defaultProjValue = settings.value( "/Projections/defaultBehaviour", "prompt", type=str )
settings.setValue( "/Projections/defaultBehaviour", "useProject" )

# functions
def getFieldsNames(layer):
    fields = []
    for field in layer.fields():
      fields = fields + [field.name()]
    return(fields)

def editAttribute(layer, fieldName, expression):
    index = layer.dataProvider().fieldNameIndex(fieldName)
    context = QgsExpressionContext()
    context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
    layer.startEditing()
    for feature in layer.getFeatures():
        context.setFeature(feature)
        value = expression.evaluate(context)
        layer.changeAttributeValue(feature.id(), index, value)
        layer.updateFeature(feature)
    layer.commitChanges()
# !!! NOT WORKING!!!    


# load layers
# gaul_eez_dissolved
countries = iface.addVectorLayer("/Users/mela/JRCbox/gaul_eez_dissolved.gpkg|layername=gaul_eez_dissolved", "countries","ogr")
# GMBA: mountain ranges
gmba = iface.addVectorLayer("../../data/GMBA mountain inventory V1.2(by mega-region)/GMBA Mountain Inventory_v1.2-Africa.shp", "", "ogr")
# GLWD_l1
glwd1 = iface.addVectorLayer("../../data/GLWD-level1/glwd_1.shp", "", "ogr")

# make a copy of countries
countryCodes = np.loadtxt("../../data/country_codes.txt", 
    dtype=np.dtype([('CC', 'U2'),('a2', 'U2'),('a3', 'U3'), ('n', 'U3'), ('Name', 'U50')]), 
    delimiter='\t', 
    skiprows=1)

countriesList = []
for c in countryCodes:
    if c['CC'] == 'AF':
        countriesList = countriesList + [c['a3']]

countries.selectByExpression(" OR ".join(['"iso3" LIKE\'%{:s}%\''.format(i) for i in countriesList]), QgsVectorLayer.SetSelection)

clone_countries = processing.run("native:saveselectedfeatures", {
    'INPUT': countries, 
    'OUTPUT': 'memory:'
    })['OUTPUT']

# select glwd1 for Africa
# extract by location
glwd1_af = processing.run("native:extractbylocation", { 
    'INPUT' : glwd1, 
    'INTERSECT' : clone_countries,
    'OUTPUT' : 'memory:', 
    'PREDICATE' : [0] })['OUTPUT']

project.addMapLayer(glwd1_af)
project.addMapLayer(clone_countries)    
# edit attributes
# delete geom mollweide
res = clone_countries.dataProvider().deleteAttributes([len(getFieldsNames(clone_countries))-1])
# add attributes
res = clone_countries.dataProvider().addAttributes([QgsField("gmba", QVariant.Int), QgsField("glwd_1", QVariant.Int), QgsField("glwd_2_1", QVariant.Int)])
clone_countries.updateFields()

# set countries that intersect GMBA to 1
s0 = " ) ) ) OR intersects(  $geometry , geometry ( get_feature_by_id ( '" + gmba.id() + "' , "
s1 = "intersects( $geometry , geometry ( get_feature_by_id ( '" + gmba.id() + "' , \
" + s0.join(str(i + 1) for i in range(gmba.featureCount() )) + " ) ) )"
# set countries that intersect GLWD_1 to sum of big lakes
s2 = " ) ) ) + intersects(  $geometry , geometry ( get_feature_by_id ( '" + glwd1_af.id() + "' , "
s3 = "intersects( $geometry , geometry ( get_feature_by_id ( '" + glwd1_af.id() + "' , \
" + s2.join(str(i + 1) for i in range(glwd1_af.featureCount() )) + " ) ) )"

context = QgsExpressionContext()
with edit(clone_countries):
    for feat in clone_countries.getFeatures():
        feat[clone_countries.fields().indexFromName("gmba")] = QgsExpression(s1).evaluate(context)
        feat[clone_countries.fields().indexFromName("glwd_1")] = QgsExpression(s3).evaluate(context)
        clone_countries.updateFeature(feat)

clone_countries.updateFields()

# the editAtribute function doesn't work. Manually paste s2 in the field expression
    

# save to file
clone_countries.selectAll()
output = processing.run("native:saveselectedfeatures", {
    'INPUT': clone_countries, 
    'OUTPUT': '../temp/countries_gmba_glwd.gpkg'
    })['OUTPUT']

# save to csv
QgsVectorFileWriter.writeAsVectorFormat(
    layer = clone_countries, 
    fileName = '../temp/countries_gmba_glwd.csv', 
    fileEncoding = 'utf-8', 
    #destCRS: QgsCoordinateReferenceSystem = QgsCoordinateReferenceSystem(), 
    driverName = 'CSV', # by default, no geometries exported with csv
    #onlySelected: bool = False, 
    #datasourceOptions: Iterable[str] = [], 
    #layerOptions: Iterable[str] = [], 
    #skipAttributeCreation: bool = False, 
    #newFilename: str = '', 
    #symbologyExport: QgsVectorFileWriter.SymbologyExport = QgsVectorFileWriter.NoSymbology, 
    #symbologyScale: float = 1, 
    #filterExtent: QgsRectangle = None, 
    #overrideGeometryType: QgsWkbTypes.Type = QgsWkbTypes.Unknown, 
    #forceMulti: bool = False, 
    #includeZ: bool = False, 
    attributes = [3,4,5,7,9,10] # : Iterable[int]
    #fieldValueConverter: QgsVectorFileWriter.FieldValueConverter = None
    ) 

