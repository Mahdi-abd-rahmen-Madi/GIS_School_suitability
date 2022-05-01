# imports
import arcpy
import arcpy.da
from arcpy.sa import *
from arcpy.conversion import *
from arcpy import env
from arcpy.ia import *
import os
from statistics import mean
# initializing the workspace
ws = os.path.abspath("os.getcwd()")
arcpy.env.workspace="ws"
# reset any python environement overrides to remove specific python settings
arcpy.ResetEnvironments()
# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")
# Preview the current Coordinate system used (for our case all vector and raster layers are under the same coordinate system   PCS = NAD_1983_StatePlane_Vermont_FIPS_4400 and projection = Transverse_Mercator
Coord_sys = env.outputCoordinateSystem.name

# Store elevation and land use in a raster variable 
elevation = Raster('elevation1')
land_Use = Raster('land_use1')

# Convert the land_use1 cellsize to conform with the elevation1 30m cellsize 
arcpy.Managment.Resample('land_use1','land_use2',30,"MAJORITY")
land = Raster('land_use2')

# Convert vector layers (Rec_sites = points ; Schools = points ; Roads = polyline )  to rasters 
arcpy.conversion.PointToRaster('Rec_sites',"MAP","MAXIMUM_COMBINED_AREA","#",env.cellsize)
arcpy.conversion.PointToRaster('Schools',"FID","MAXIMUM_COMBINED_AREA","#",env.cellsize)
arcpy.conversion.PolylineToRaster('Roads',"LENGTH","MAXIMUM_COMBINED_AREA","#",env.cellsize)

# Save these conversions to actual rasters for later use 
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

# Create a distance map using the euclidian distance tool : 
RoadsPath = os.path.abspath("Roads.shp")
Roads_Output_Path = os.path.abspath("Roads.tif")
Roads = "RoadsPath"
Roads_output = "Roads_Output_Path"
Rmax = Roads.maximum # Rmax = Roads maximum euclidian distance
Rmin = Roads.minimum # Rmin = Roads minimum euclidian distance
Range = mean(Rmax,Rmin) # R would be the avearge of theses min-max distances
R = Range//10
EDRoads = arcpy.sa.EucDistance(Roads,Range, 30, Roads_output)  
EDRoads.save(Roads_output)
reclassRoadsRange= arcpy.sa.RemapRange([0,R,10],[R,2*R,9],[2*R,3*R,8],[3*R,4*R,7],[4*R,5*R,6],[5*R,6*R,5],[6*R,7*R,4],[7*R,8*R,3],[8*R,9*R,2],[9*R,Range,1])
reclassRoads=arcpy.sa.Reclassify(Roads,'Roads.tif',reclassRoadsRange,"NODATA")
reclassRoads.save("Roads_Suitability")
Roads_S = arcpy.Raster("Roads_Suitability")

# far away from other schools : 
Schools_Path = os.path.abspath("Schools.shp")
Schools_Output_Path = os.path.abspath("Schools.tif")
schools = "Schools_Path"
School_output = "School_Output_Path"
EDSchools = arcpy.sa.EucDistance(schools,Range,30,School_output)
EDSchools.save(School_output)
reclassSchoolRange = arcpy.sa.RemapRange([0,R,1],[R,2*R,2],[2*R,3*R,3],[3*R,4*R,4],[4*R,5*R,5],[5*R,6*R,6],[6*R,7*R,7],[7*R,8*R,8],[8*R,9*R,9],[9*R,Range,10])
reclass_Schools = arcpy.sa.Reclassify(schools,'schools.tif',reclassSchoolRange,"NODATA")
reclass_Schools.save("School_Proximity_Suitability")
School_S = arcpy.Raster('School_Proximity_Suitability')

# recreational sites suitability 
Rec_Path = os.path.abspath("Rec_sites.shp")
Rec_Output_Path = os.path.abspath("Rec_sites.tif")
Rec_sites = "Rec_Path"
Rec_output = "Rec_Output_Path"
Rec_max = Rec_sites.maximum
Rec_min = Rec_sites.minimum
Rec = mean(Rec_min,Rec_max)
RE = Rec//10
EDRec = arcpy.sa.EucDistance(Rec_sites, Rec, 30, Rec_output)
EDRec.save(Rec_output)
reclassRecRange= arcpy.sa.RemapRange([0,RE,10],[RE,2*RE,9],[2*RE,3*RE,8],[3*RE,4*RE,7],[4*RE,5*RE,6],[5*RE,6*RE,5],[6*RE,7*RE,4],[7*RE,8*RE,3],[8*RE,9*RE,2],[9*RE,Rec,1])
reclassRec=arcpy.sa.Reclassify(Rec_sites,'Rec.tif',reclassRecRange,"NODATA")
reclassRec.save("Rec_Suitability")
Rec_S = arcpy.Raster("Rec_Suitability")

# suitability formula : 
suitability =( 0.125 * Slope_S + 0.125 * School_S + 0.25* Rec_S + 0.5 * Land_S ) 

# Displaying the results : 
arcpy.CheckOutExtension('ImageAnalyst')
arcpy.ia.Render(suitability, rendering_rule = {'min' : 0 ,'max' : 100 },colormap = 'Red to Green')
