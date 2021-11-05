# -*- coding: utf-8 -*-

# Importation du module arcpy
import arcpy
from arcpy.sa import *

arcpy.overwriteoutput = 1

# Workspace
Workspace = arcpy.GetParameterAsText(0)
# Fichier stockant les correspondances arbre - Catégorie
CSVFile = arcpy.GetParameterAsText(1)
# Couche à modifier
layerSelected = arcpy.GetParameterAsText(2)
# Nom du champ contenant l'espèce
champEspece = arcpy.GetParameterAsText(3)

# Set the current workspace
arcpy.env.workspace = Workspace

arcpy.AddMessage("Ouverture du fichier Excel et stockage des valeurs...")

correspondancesArbreCategorie = dict()

# Ouverture du fichier de correspondances
with open(CSVFile, "r") as file1:
    # Pour chaque ligne
    for line in file1:
        # On sépare la ligne par rapport au ;
        line=line.split(";")
        # Categorie 1 représente les arbres grands, 2 = moyen, 3 = petit.
        if "1" in line[1]:
            correspondancesArbreCategorie[line[0]] = "Grand"
        elif "2" in line[1]:
            correspondancesArbreCategorie[line[0]] = "Moyen"
        elif "3" in line[1]:
            correspondancesArbreCategorie[line[0]] = "Petit"

arcpy.AddMessage("Lecture du fichier Excel terminee")

# Délétion du champ "Categorie" s'il existe deja.
existingFields = arcpy.ListFields(layerSelected)
lstNamesExistingFields = []
for field in existingFields:
    lstNamesExistingFields.append(field.name)
if "Categorie" in lstNamesExistingFields:
    arcpy.DeleteField_management(layerSelected, "Categorie")
    arcpy.AddMessage("Reinitialisation du champ \"Categorie\" en cours...")
else:
    arcpy.AddMessage("Creation du champ \"Categorie\" en cours...")

# Création du champ "Categorie"
arcpy.AddField_management(layerSelected, "Categorie", "TEXT")

arcpy.AddMessage("Creation du champ \"Categorie\" terminee.")

nRows = int(str(arcpy.GetCount_management(layerSelected)))
currentRow = 0
percentage = 0
nFailedAssociations = 0

arcpy.AddMessage("Debut de l'ecriture dans la table d'attributs. " + str(nRows) + " lignes dans le tableau.")

# On pré-sélectionne les colonnes (le champs contenant le nom de l'espèce et la catégorie)
columns = [str(champEspece), "Categorie"]

# On choisit la couche et les colonnes
with arcpy.da.UpdateCursor(layerSelected, columns) as rows:
    # Pour chaque ligne du tableau
    for row in rows:
        previousPercentage = percentage
        percentage = int(100*currentRow/nRows)
        if percentage != previousPercentage:
            arcpy.AddMessage("Ecriture dans la table d'attributs en cours... " + str(percentage) + "%")
        # On stocke le nom de l'espèce
        espece = row[0]
        # On itère sur toutes les espèces dans la table de correspondances.
        notHalted = True
        for keySpecies in correspondancesArbreCategorie.keys():

            # Si ce nom est dans la table de correspondances, ou fait partie d'un des noms de la table, et que c'est bien la première fois qu'on détecte une correspondance.
            if notHalted and (espece in keySpecies or keySpecies in espece):
                # On stocke la catégorie correspondante dans la table.
                row[1] = correspondancesArbreCategorie[keySpecies]
                notHalted = False
            # Il y a parfois des "x" bizarres dans la table d'attributs qui gênent la reconnaissance de l'espèce.
            elif notHalted and (espece.replace("×","") in keySpecies or keySpecies in espece.replace("×","")):
                # On stocke la catégorie correspondante dans la table.
                row[1] = correspondancesArbreCategorie[keySpecies]
                notHalted = False
        
        # Si on a pas trouvé de correspondance.
        if len(row[1]) == 0:
            nFailedAssociations += 1
        # Commit les changements
        rows.updateRow(row)
        currentRow += 1

# On a terminé.
arcpy.AddMessage("Ecriture dans la table d'attributs terminée. " + str(nFailedAssociations) + " erreurs de correspondance rencontrées, soit " + str(int(nFailedAssociations/nRows * 100)) + "% du total.")