# -*- coding: utf-8 -*-

# Importation du module arcpy
import arcpy
from arcpy.sa import *

arcpy.overwriteoutput = 1

# Workspace
Workspace = arcpy.GetParameterAsText(0)
# Couche à analyser
layerSelected = arcpy.GetParameterAsText(1)
# Nom du champ contenant la catégorie
champCategorie = arcpy.GetParameterAsText(2)
# Nom du champ contenant la date de plantation
champDatePlant = arcpy.GetParameterAsText(3)
# Nom du champ contenant la date d'observation
champDateObs = arcpy.GetParameterAsText(4)
# Nom du champ contenant la hauteur de l'arbre
champHauteurTotale = arcpy.GetParameterAsText(5)
# Nom du champ contenant la hauteur du tronc
champHauteurTronc = arcpy.GetParameterAsText(6)
# Nom du champ contenant le diametre couronne
champDiametre = arcpy.GetParameterAsText(7)
# ROI name
ROIname = arcpy.GetParameterAsText(8)


# Set the current workspace
arcpy.env.workspace = Workspace

# Build SQL expression
# Sélection sur critères :
# 1) Catégorie connue
# 2) Date de plantation connue
# 3) Situation connue
# 4) Rayon couronne connue
# 5) Date d'observation connue
# 6) Date d'observation postérieure au 01.01.2010 
Expression = str(champCategorie) + " <> '' And " + str(champDatePlant) + " IS NOT NULL And " + str(champHauteurTotale) + " <> 0 And " + str(champHauteurTronc) + " <> 0 And " + str(champDiametre) + " <> 0 And " + str(champDateObs) + " IS NOT NULL And " + str(champDateObs) + " > timestamp '2010-01-01 00:00:00'"
arcpy.AddMessage(Expression)

# Clear Selection
Selection = arcpy.SelectLayerByAttribute_management(layerSelected, "CLEAR_SELECTION")

# Select the points
Selection = arcpy.SelectLayerByAttribute_management(layerSelected, "NEW_SELECTION", Expression)

# Generate the name of the output shapefile
NameSelection = "CalibrationData"

# Copy the selection into a new shapefile
arcpy.CopyFeatures_management(Selection, Workspace + "\\" + NameSelection)


CalibrationSHPlayer = Workspace + "\\" + NameSelection + ".shp"

line = ""

columns = [str(champCategorie), str(champDatePlant), str(champDateObs), str(champHauteurTotale), str(champHauteurTronc), str(champDiametre)]
path = "D:\Documents\Flann\STDL\CanopyGrowthABM\DATA\CalibrationCSVdata_" + str(ROIname) + ".csv"

with open(path, "w") as newFile:
    with arcpy.da.SearchCursor(CalibrationSHPlayer, columns) as rows:
        for row in rows:
            line = str(row[0]) + ";" + str(row[1]) + ";" + str(row[2]) + ";" + str(row[3]) + ";" + str(row[4]) + ";" + str(row[5]) + "\n"
            newFile.write(line)


    