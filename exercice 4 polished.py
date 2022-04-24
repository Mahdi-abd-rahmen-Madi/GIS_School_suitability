#
# city rec sites schools roads are all vector files 
# land_use1  : cellsize = 25*25 
# elevation1 : cellsize = 30*30 

# imports
import arcpy
import arcpy.da
from arcpy.sa import *
from arcpy.management import * # to import project raster (not needed here)
from arcpy.conversion import * # needed when converting polygone to raster
from arcpy import env
# initializing the workspace
arcpy.env.workspace="C:\Users\Mahdi\Desktop\Rasters"
# reset any python environement overrides to remove specific python settings
arcpy.ResetEnvironments()
# to preview the current Coordinate system used 
Coord_sys = env.outputCoordinateSystem.name
# Store elevation in raster variable 
elevation = Raster('elevation1')
land_Use = Raster('land_use1')
# Convert the land_use1 cellsize to conform with the elevation1 30m cellsize 
arcpy.Managment.Resample('land_use1','land_use2',30,"MAJORITY")
land = Raster('land_use2')
#c convert vector layers to rasters 
arcpy.conversion.PolygoneToRaster('Rec_sites',"SOIL_CODE","MAXIMUM_COMBINED_AREA","#",env.cellsize)
arcpy.conversion.PolygoneToRaster('Schools',"SOIL_CODE","MAXIMUM_COMBINED_AREA","#",env.cellsize)
arcpy.conversion.PolygoneToRaster('Roads',"LENGTH","MAXIMUM_COMBINED_AREA","#",env.cellsize)
# save these conversions to actual rasters to use later 
Roads = arcpy.Raster('Roads')
Rec_sites = arcpy.Raster('Rec_sites')
schools = arcpy.Raster('schools')

# create the slope raster layer with the "Slope" spatial analyst tool 
slope = Slope(elevation) 
# reclassify the slopes values following the given table 
slope = arcpy.Raster('slope')
reclassListRanges=arcpy.sa.RemapRange([[0,7,10],[7,14,9],[14,21,8],[21,28,7],[28,35,6],[35,42,5],[42,49,4],[49,56,3],[56,63,2],[63,70,1]])
reclassified_Slope=arcpy.sa.Reclassify(slope,"Value",reclassListRanges,"NODATA")
reclassified_Slope.save('slope_suitability')
# save the slope suitability into a variable for later use 
Slope_S = arcpy.Raster('slope_suitavility')

# relcassify the land values following the given table 
reclassListValues=arcpy.sa.RemapValue([["Agriculture",10],["Barren Land",6],["Brush/traditional",5],["Builtup",3]["Forest",4],["Water",0],["Wetlands",0]])
reclassified_Land=arcpy.sa.Reclassify(land,"Land_Use1",reclassListValues,"NODATA")
reclassified_Land.save("Land_Suitability")
# save the land suitability into a variable for later use 
Land_S = arcpy.Raster('Land_Suitability')

# roads distance (optional as stated in exercise text)
Roads = "C:\Users\Mahdi\Desktop\Rasters\Roads.shp"
Roads_output = "C:\Users\Mahdi\Desktop\Rasters\Roads.tiff"
# INPUT /MAX DISTANCE / CELLSIZE / OUTPUT / DISTANCE METHOD / IN BARRIER DATA / OUTBACK DIRECTION RASTER 
# https://desktop.arcgis.com/en/arcmap/latest/tools/spatial-analyst-toolbox/euclidean-distance.htm
EDRoads = arcpy.sa.EucDistance(Roads, 3100, 30, Roads_output) # as in 3.1 km 
EDRoads.save(Roads_output)
reclassRoadsRange= arcpy.sa.RemapRange([0,300,10],[301,600,9],[601,900,8],[901,1200,7],[1201,1500,6],[1501,1800,5],[1801,2100,4],[2101,2500,3],[2501,2801,2],[2801,3100,1])
reclassRoads=arcpy.sa.Reclassify(Roads,'Roads.tiff',reclassRoadsRange,"NODATA")
reclassRoads.save("Roads_Suitability")
Roads_S = arcpy.Raster("Roads_Suitability")
# far away from other schools : 
schools = "C:\Users\Mahdi\Desktop\Rasters\Schools.shp"
School_output = "C:\Users\Mahdi\Desktop\Rasters\Schools.tiff"
EDSchools = arcpy.sa.EucDistance(schools,3100,30,School_output)
EDSchools.save(School_output)
reclassSchoolRange = arcpy.sa.RemapRange([0,300,1],[301,600,2],[601,900,3],[901,1200,4],[1201,1500,5],[1501,1800,6],[1801,2100,7],[2101,2500,8],[2501,2801,9],[2801,3100,10])
reclass_Schools = arcpy.sa.Reclassify(schools,'schools.tiff',reclassSchoolRange,"NODATA")
reclass_Schools.save("School_Proximity_Suitability")
School_S = arcpy.Raster('School_Proximity_Suitability')
# recreational sites suitability 
Rec_sites = "C:\Users\Mahdi\Desktop\Rasters\Rec_sites.shp"
Rec_output = "C:\Users\Mahdi\Desktop\Rasters\Rec_sites.tiff"
EDRec = arcpy.sa.EucDistance(Rec_sites, 1000, 30, Rec_output) # as in 1 km Recreational sites need to be real close compared to regular distance to school
EDRec.save(Rec_output)
reclassRecRange= arcpy.sa.RemapRange([0,100,10],[101,200,9],[201,300,8],[301,400,7],[401,500,6],[501,600,5],[601,700,4],[701,800,3],[801,900,2],[901,1000,1])
reclassRec=arcpy.sa.Reclassify(Rec_sites,'Rec.tiff',reclassRecRange,"NODATA")
reclassRec.save("Rec_Suitability")
Rec_S = arcpy.Raster("Rec_Suitability")

suitability =( 0.125 * Slope_S + 0.125 * School_S + 0.25* Rec_S + 0.5 * Land_S ) 