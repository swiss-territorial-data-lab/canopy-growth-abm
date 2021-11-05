import numpy as np
import statistics as st
import os

# tkinter module for importing a file via a dialog box (should be crossplatform)
from tkinter import Tk 
from tkinter.filedialog import askopenfilename
 
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing 
CalibrationData = askopenfilename() # show an "Open" dialog box and return the path to the selected file 

# Création d'un nouveau dossier "CalibrationOutput" s'il n'existe pas déjà.
dirName = "CalibrationOutput"
if not os.path.exists(dirName):
    os.makedirs(dirName)

# Calcul des coefficients.
def LinearWeighting (max_canopy, max_lifetime, r):
    return (8 * r * max_canopy - 4 * max_canopy) / max_lifetime

def QuadraticWeighting (max_canopy, max_lifetime, r):
    return (-16 * r * max_canopy + 11 * max_canopy) / max_lifetime**2

def CubicWeighting (max_canopy, max_lifetime, r):
    return (8 * r * max_canopy - 6 * max_canopy) / max_lifetime**3

# Calcul du diamètre de la canopée.
def calculateCanopyDiameter (max_canopy, max_lifetime, r, age, growth_stress_multiplier):
    return growth_stress_multiplier * (CubicWeighting(max_canopy, max_lifetime, r) * age**3 + QuadraticWeighting(max_canopy, max_lifetime, r) * age**2 + LinearWeighting(max_canopy, max_lifetime, r) * age)

# Initialisation de la liste qui va contenir les données de calibration.
data = []

# Ouverture du fichier de données de calibration
with open(CalibrationData, "r") as file1:
    for line in file1:
        line = line.split(";")
        date_plant = int(line[1][6:10])
        date_obs = int(line[2][6:10])
        # Importation des données du fichier csv vers la liste.
        # Catégorie
        # Nombre d'années entre la date d'observation et la date de plantation
        # Hauteur de l'arbre - Hauteur du tronc
        # Diamètre de la canopée
        data.append([line[0], date_obs - date_plant, float(line[3]) - float(line[4]), float(line[5])])

print(data)

# Nombre d'expériences à conserver.
nRegisteredExperiments = 20

# Catégorie : Petit arbre.
# Code : A

# Liste des expériences ayant la plus petite erreur.
# Elle sera de la forme : [exp1, exp2, exp3, ... expN]
# Initialisée à [[1], [2], .... , [N]]
# Chaque exp est elle-même une liste des paramètres qui lui sont propres.
# expn = [erreur moyenne, canopée_max, longévité, r, âge à la plantation, GSM = growth stress multiplier]
# Par conséquent expn[0] réfère à l'erreur moyenne de l'expérience n, et c'est ce critère qui va déterminer quelles expériences garder.

listOptimalExperimentsA = []
for n in range(nRegisteredExperiments):
    listOptimalExperimentsA.append([n+1, n+1])

# On filtre les données par catégorie.
data_A = [tree for tree in data if tree[0] == "Petit"]

print("Calibration pour les petits arbres en cours...")

with open("CalibrationOutput\outputA.csv", "w") as outputFileA:
    # Si les données ne sont pas vides.    
    if len(data_A) != 0:
        # On fait varier le diamètre de la canopée maximale entre 3 et 7 compris, par pas de 1.
        for yMaxA_D in range(3,10):
            # On fait varier la hauteur de la canopée maximale entre 3 et 7 compris, par pas de 1.
            for yMaxA_H in range(3,10):
                # On fait varier la longévité maximale entre 10 et 120 compris, par pas de 10.
                for tMaxA in range(20,90,10):
                    # On fait varier la valeur r entre 0.5 et 0.9 compris, par pas de 0.05.
                    for rA in np.linspace(0.8,0.9,6):
                        # On fait varier l'âge à la plantation entre 0 et 20 compris, par pas de 2.
                        for ageAtPlantation_A in range(0,11,2):
                            # On fait varier le facteur de stress entre 0.5 et 0.9 compris, par pas de 0.1.
                            for GSM_A in np.linspace(0.6,0.8,5):
                                # Initialisation de la liste des erreurs pour chaque arbre individuel
                                listErrors_H = []
                                listErrors_D = []
                                # Pour chaque arbre, sous la forme d'une liste [Catégorie, nb d'années dans le sol à l'observation, diamètre couronne, situation de l'arbre]
                                for treeA in data_A:
                                    canopy_H = calculateCanopyDiameter (yMaxA_H, tMaxA, rA, treeA[1] + ageAtPlantation_A, GSM_A)
                                    canopy_D = calculateCanopyDiameter (yMaxA_D, tMaxA, rA, treeA[1] + ageAtPlantation_A, GSM_A)
                                    # On calcule l'écart entre la canopée calculée et la canopée relevée dans les data.
                                    error_H = abs(canopy_H - treeA[2]) / treeA[2]
                                    error_D = abs(canopy_D - treeA[3]) / treeA[3]
                                    # On ajoute cette valeur d'erreur à la liste.
                                    listErrors_H.append(error_H)
                                    listErrors_D.append(error_D)
                                # On calcule l'erreur moyenne pour cette série de paramètres.
                                # Il est possible de calculer une autre quantité que la moyenne (par exemple, la moyenne des carrés).
                                averageError_H = st.mean(listErrors_H)
                                averageError_D = st.mean(listErrors_D)
                                # On cherche dans la liste des expériences optimales, celle qui présente l'erreur la plus élevée
                                # et on la stocke dans la variable currentMaxError.
                                listMinErrorsA_D = [listOptimalExperimentsA[i][0] for i in range(len(listOptimalExperimentsA))]
                                currentMaxError_D = max(listMinErrorsA_D)

                                HeightErrorIsMin = True
                                listAlreadyShortened = False
                                # If we have a perfect match in average error for diameter in the list of min diameter error
                                if averageError_D in listMinErrorsA_D:
                                    # Capture the index of that match in the list of min diameter error
                                    index = listMinErrorsA_D.index(averageError_D)
                                    # We only save the current experiment if the average error for height is lower than the current one registered
                                    # for the corresponding average error in diameter.
                                    if averageError_H >= listOptimalExperimentsA[index][1]:
                                        HeightErrorIsMin = False
                                    # If we do save the current experiment, we remove the previous one.
                                    else:
                                        del listOptimalExperimentsA[index]
                                        listAlreadyShortened = True
                                
                                # Si l'erreur qu'on a obtenue pour cette série de paramètres est inférieure à currentMaxError
                                if averageError_D <= currentMaxError_D and HeightErrorIsMin:                                    
                                    # On ajoute l'expérience en cours.
                                    listOptimalExperimentsA.append([averageError_D, averageError_H, yMaxA_D, yMaxA_H, tMaxA, rA, ageAtPlantation_A, GSM_A])
                                    # On trie selon le premier argument de chaque élément de la liste.
                                    listOptimalExperimentsA.sort()
                                    # On supprime le dernier élément de la liste
                                    if not listAlreadyShortened:
                                        listOptimalExperimentsA.pop()
        # Initialisation du fichier output, qui va contenir les N expériences les plus optimales.
        outputFileA.write("Erreur_D;Erreur_H;CanopeeMax_D;CanopeeMax_H;Longevite;r;AgePlantation;GSM\n")
        # On trie selon le premier argument de chaque élément de la liste.
        # Ca tombe bien, ici il s'agit de l'erreur moyenne.
        # C'est justement la raison pour laquelle cette donnée apparaît en premier dans les données de chaque expérience.
        # Rappel : expn = [erreur moyenne, canopée_max, longévité, r, âge à la plantation, GSM = growth stress multiplier]
        listOptimalExperimentsA.sort()
        # Pour chaque expérience optimale
        for experiment in listOptimalExperimentsA:
            # Pour chaque paramètre de l'expérience
            for parameter in experiment:
                # On écrit la valeur de ce paramètre dans le fichier. On n'oublie pas le ;
                outputFileA.write(str(parameter) + ";")
            # On saute une ligne à la fin de la ligne.
            outputFileA.write("\n")
    else:
        outputFileA.write("Aucune donnée n'a été détectée pour cette catégorie d'arbres.")
        print("Aucune donnée n'a été détectée pour cette catégorie d'arbres.")
    
# Le code fonctionne sur le même principe pour les autres catégories.
# Les seules choses qui changent sont le fichier de sortie, et la range de certains paramètres, comme la taille de la canopée max.

# Catégorie : Arbre de taille moyenne.
# Code : B

listOptimalExperimentsB = []
for n in range(nRegisteredExperiments):
    listOptimalExperimentsB.append([n+1, n+1])

data_B = [tree for tree in data if tree[0] == "Moyen"]

print("Calibration pour les arbres de taille moyenne en cours...")

with open("CalibrationOutput\outputB.csv", "w") as outputFileB:
    if len(data_B) != 0:
        for yMaxB_D in range(4,16):
            for yMaxB_H in range(5,11):
                for tMaxB in range(20,80,10):
                    for rB in np.linspace(0.8,0.9,6):
                        for ageAtPlantation_B in range(0,11,2):
                            for GSM_B in np.linspace(0.6,0.8,5):
                                listErrors_D = []
                                listErrors_H = []
                                for treeB in data_B:
                                    canopy_H = calculateCanopyDiameter (yMaxB_H, tMaxB, rB, treeB[1] + ageAtPlantation_B, GSM_B)
                                    canopy_D = calculateCanopyDiameter (yMaxB_D, tMaxB, rB, treeB[1] + ageAtPlantation_B, GSM_B)
                                    error_H = abs(canopy_H - treeB[2]) / treeB[2]
                                    error_D = abs(canopy_D - treeB[3]) / treeB[3]
                                    listErrors_H.append(error_H)
                                    listErrors_D.append(error_D)
                                averageError_H = st.mean(listErrors_H)
                                averageError_D = st.mean(listErrors_D)
                                listMinErrorsB_D = [listOptimalExperimentsB[i][0] for i in range(len(listOptimalExperimentsB))]
                                currentMaxError_D = max(listMinErrorsB_D)

                                HeightErrorIsMin = True
                                listAlreadyShortened = False
                                # If we have a perfect match in average error for diameter in the list of min diameter error
                                if averageError_D in listMinErrorsB_D:
                                    # Capture the index of that match in the list of min diameter error
                                    index = listMinErrorsB_D.index(averageError_D)
                                    # We only save the current experiment if the average error for height is lower than the current one registered
                                    # for the corresponding average error in diameter.
                                    if averageError_H >= listOptimalExperimentsB[index][1]:
                                        HeightErrorIsMin = False
                                    else:
                                        del listOptimalExperimentsB[index]
                                        listAlreadyShortened = True

                                
                                if averageError_D <= currentMaxError_D and HeightErrorIsMin:
                                    listOptimalExperimentsB.append([averageError_D, averageError_H, yMaxB_D, yMaxB_H, tMaxB, rB, ageAtPlantation_B, GSM_B])
                                    listOptimalExperimentsB.sort()
                                    if not listAlreadyShortened:
                                        listOptimalExperimentsB.pop()
        outputFileB.write("Erreur_D;Erreur_H;CanopeeMax_D;CanopeeMax_H;Longevite;r;AgePlantation;GSM\n")
        listOptimalExperimentsB.sort()
        for experiment in listOptimalExperimentsB:
            for parameter in experiment:
                outputFileB.write(str(parameter) + ";")
            outputFileB.write("\n")
    else:
        outputFileB.write("Aucune donnée n'a été détectée pour cette catégorie d'arbres.")
        print("Aucune donnée n'a été détectée pour cette catégorie d'arbres.")


# Catégorie : Grand arbre.
# Code : C

listOptimalExperimentsC = []
for n in range(nRegisteredExperiments):
    listOptimalExperimentsC.append([n+1, n+1])

data_C = [tree for tree in data if tree[0] == "Grand"]

print("Calibration pour les grands arbres en cours...")

with open("CalibrationOutput\outputC.csv", "w") as outputFileC:
    if len(data_C) != 0:
        for yMaxC_D in range(8,21):
            for yMaxC_H in range(7,14):
                for tMaxC in range(40,160,10):
                    for rC in np.linspace(0.8,0.9,6):
                        for ageAtPlantation_C in range(0,21,2):
                            for GSM_C in np.linspace(0.6,0.8,5):
                                listErrors_H = []
                                listErrors_D = []
                                for treeC in data_C:
                                    canopy_H = calculateCanopyDiameter (yMaxC_H, tMaxC, rC, treeC[1] + ageAtPlantation_C, GSM_C)
                                    canopy_D = calculateCanopyDiameter (yMaxC_D, tMaxC, rC, treeC[1] + ageAtPlantation_C, GSM_C)
                                    if treeC[2] != 0:
                                        error_H = abs(canopy_H - treeC[2]) / treeC[2]
                                    else:
                                        error_H = 1
                                    if treeC[3] != 0:
                                        error_D = abs(canopy_D - treeC[3]) / treeC[3]
                                    else:
                                        error_D = 1
                                    listErrors_H.append(error_H)
                                    listErrors_D.append(error_D)
                                averageError_H = st.mean(listErrors_H)
                                averageError_D = st.mean(listErrors_D)
                                listMinErrorsC_D = [listOptimalExperimentsC[i][0] for i in range(len(listOptimalExperimentsC))]
                                currentMaxError_D = max(listMinErrorsC_D)
                                
                                listAlreadyShortened = False
                                HeightErrorIsMin = True
                                # If we have a perfect match in average error for diameter in the list of min diameter error
                                if averageError_D in listMinErrorsC_D:
                                    # Capture the index of that match in the list of min diameter error
                                    index = listMinErrorsC_D.index(averageError_D)
                                    # We only save the current experiment if the average error for height is lower than the current one registered
                                    # for the corresponding average error in diameter.
                                    if averageError_H >= listOptimalExperimentsC[index][1]:
                                        HeightErrorIsMin = False  
                                    else:
                                        del listOptimalExperimentsC[index]
                                        listAlreadyShortened = True                             
                                
                                if averageError_D <= currentMaxError_D and HeightErrorIsMin:
                                    listOptimalExperimentsC.append([averageError_D, averageError_H, yMaxC_D, yMaxC_H, tMaxC, rC, ageAtPlantation_C, GSM_C])
                                    listOptimalExperimentsC.sort()
                                    if not listAlreadyShortened:
                                        listOptimalExperimentsC.pop()
        outputFileC.write("Erreur_D;Erreur_H;CanopeeMax_D;CanopeeMax_H;Longevite;r;AgePlantation;GSM\n")
        listOptimalExperimentsC.sort()
        for experiment in listOptimalExperimentsC:
            for parameter in experiment:
                outputFileC.write(str(parameter) + ";")
            outputFileC.write("\n")
    else:
        outputFileC.write("Aucune donnée n'a été détectée pour cette catégorie d'arbres.")
        print("Aucune donnée n'a été détectée pour cette catégorie d'arbres.")

print("Calibration terminee !")
                



