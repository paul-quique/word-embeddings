"""
TP N°5 - Othman DRICI - Paul QUIQUE
------Matrice de co-occurences-----
"""

import re
import numpy as np
import pickle5 as pickle

# Chemins de tous les textes du corpus, réduire à 3 textes car pas assez de mémoire vive pour la matrice.
chemins_corpus = ["tiny"]#, "soap_text", "movies_text", "wiki_text", "tv_text"]

def fichierVersMots(chemin):
    """
    Retourne le contenu d'un fichier texte sous forme d'une liste de mots.
    Paramètres: Nom      |    Type
                chemin   |    str
    """
    # On ouvre le fichier en mode lecture et on lit son contenu.
    fichier = open(chemin, "r")
    texte = ""
    
    for ligne in fichier.readlines():
        texte += ligne
    
    #Libérer l'accès au fichier et renvoyer la liste de mots.
    fichier.close()
    
    return texteVersMots(
            epurerTexte(texte)
        )

def epurerTexte(texte):
    """
    Retourne le texte en minuscules, sans la ponctuation.
    Paramètres: Nom      |    Type
                texte    |    str
    """
    #Mettre le texte en minuscules.
    texte = texte.lower()
    #Filtrer les caractères pour ne garder que les lettres et les chiffres avec une expression régulière.
    texte = re.sub('[^a-z0-9]', ' ', texte)
    return texte

def texteVersMots(texte):
    """
    Retourne les mots contenus dans le texte sous forme de liste.
    Paramètres: Nom      |    Type
                texte    |    str
    """
    #L'expression régulière match les suites d'un ou plusieurs espaces et les utilise
    #pour séparer les mots.
    return re.split('[ ]+', texte)

def occurencesMots(mots):
    """
    Retourne les mots contenus dans le texte de dictionnaire avec comme
    clé le mot et comme valeur le nombre de fois ou il apparait.
    Paramètres: Nom      |    Type
                mots     |    str list
    """
    #On va parcourir la liste et incrémenter la valeur correspondante au
    #mot courant dans le dictionnaire.
    occurences = {}
    
    for mot in mots:
        if mot in occurences:
            occurences[mot] += 1
        else:
            occurences[mot] = 1
        
    return occurences

def occurencesMots_v2(mots):
    """
    Retourne les mots contenus dans le dictionnaire sous forme de liste
    ((clé, valeur)) avec clé le mot et comme valeur le nombre de fois ou il apparait.
    Elimine les 100 mots les plus fréquents et les mots qui n'apparaissent
    qu'une seule fois.
    Paramètres: Nom      |    Type
                mots     |    dict
    """
    # On trie le dictionnaire :
    trie = sorted(mots.items(), key=lambda occurence: occurence[1], reverse=True)
    #On élimine les 100 mots les plus fréquents:
    index_sup = 100
    index_min = 0
    
    for couple in trie:
        if couple[1] == 1:
            break
        index_min += 1
        
    trie = trie[0:index_sup] + trie[index_min:len(mots)]
    
    for couple in trie:
        mots.pop(couple[0])
        
    return mots

def sauvegarder(chemin):
    """
    Fonction générale qui appelle dans l'ordre les fonctions précédente et enregistre la liste
    dans un fichier texte, avec un mot par ligne, et la liste de tous les mots dans un autre
    fichier texte.
    
    Paramètres: Nom      |    Type
                mots     |    dict
    """
    
    #On recopie les mots uns à uns dans le fichier texte en sautant des lignes.
    mots = fichierVersMots(chemin+".txt")
    occurences = occurencesMots_v2(occurencesMots(mots))
    
    f = open(chemin+"_sauvegarde"+".txt", "w")
    
    for mot in mots:
        if mot in occurences:
            f.write(mot + "\n")
    #Libérer le fichier
    f.close()
    
    f = open(chemin+"_mots"+".txt", "w")
    
    for cle in occurences.keys():
        f.write(cle + "\n")
    #Libérer le fichier
    f.close()

def traiterCorpus():
    """
    Effectue le traitement des textes du corpus et sauvegarde les résultats dans les fichiers texte.
    
    Paramètres: Aucun
    """
    
    for chemin in chemins_corpus:
        sauvegarder(chemin)

def chargerMots(chemin):
    """
    Retourne le contenu d'une sauvegarde sous forme d'une liste de mots.
    
    Paramètres: Nom      |    Type
                chemin   |    str
    """
    mots = []
    sauvegarde = open(chemin+"_sauvegarde.txt", "r")
    
    #Chaque ligne correspond en fait à un mot, puisque on lit le fichier de sauvegarde.
    for mot in sauvegarde.readlines():
        #On prend garde à enlever le retour à la ligne.
        mots.append(mot[:-1])
        
    sauvegarde.close()
    #Renvoyer la liste des mots lus dans le fichier.
    return mots

def chargerIndicesMots(chemin):
    """
    Retourne le contenu d'une sauvegarde d'un dictionnaire{mot:indice}.
    
    Paramètres: Nom      |    Type
                chemin   |    str
    """
    indices_mots = {}
    sauvegarde = open(chemin+"_mots.txt", "r")
    
    #Chaque ligne correspond en fait à un mot, puisque on lit le fichier de sauvegarde.
    indice = 0
    for mot in sauvegarde.readlines():
        #On prend garde à enlever le retour à la ligne.
        indices_mots[mot[:-1]] = indice
        indice += 1
        
    sauvegarde.close()
    #Renvoyer le dictionnaire{mot:indice}.
    return indices_mots

def compute_matrix(mots, k, indices_mots):
    """
    Calculer la matrice de co-occurrence. Cette fonction prend en paramètre
    plusieurs éléments : la liste des mots du corpus, la valeur de k pour le
    calcul des contextes, et un dictionnaire qui associe à chaque mot son index
    dans la matrice.
    
    Paramètres: Nom          |    Type
                mots         |    str list
                k            |    int
                indices_mots |    dict{str:int}
    """
    #On initialise les incréments pour le k-context, qui vont rester constants
    #pour un appel de fonction puisque k ne varie pas
    increments = list(range(-k, 0)) + list(range(1, k+1))
    
    #On initialise la matrice carrée de taille NxN en la remplissant de 0
    N = len(indices_mots)
    mat_occurences = np.zeros((N, N))
    
    #On parcourt la liste des mots, et on complète la matrice
    index = 0
    for mot in mots:
        #Récupérer l'indice (la ligne) du mot
        ligne = indices_mots[mot]
        
        #Pour chaque mot, évaluer son k-context en faisant attention aux bornes
        for inc in increments:
            if index + inc < 0 or index + inc > len(mots)-1:
                continue
            else:
                colonne = indices_mots[mots[index+inc]]
                mat_occurences[ligne][colonne] += 1
                
        #Incrémenter l'index du mot traité
        index += 1
    
    #Remplacer les effectifs par des fréquences et retourner la matrice
    return mat_occurences / len(mots)

def matriceCorpusComplet():
    """
    Renvoie la matrice de co-occurences du corpus de texte entier.
    Cette fonction est limitée par la taille maximum d'une matrice numpy.
    
    Paramètres: Aucun
    """
    corpus_complet = []
    
    #On va récupérer tous les mots du corpus et les traiter.
    for chem in chemins_corpus:
        corpus_complet += chargerMots(chem)
    
    #On va remplir le dictionnaire des indices.
    indices_mots = {}
    indice = 0
    
    for mot in corpus_complet:
        #Vérifier que le mot courant ne se trouve pas déjà dans le dictionnaire.
        if not(mot in indices_mots):
            #Lui assigner son indice propre.
            indices_mots[mot] = indice
            indice+=1
            
    return compute_matrix(corpus_complet, 8, indices_mots)
        
def sauvegarderMatrice(chemin, mat):
    """
    Enregistre la matrice passée en paramètre dans un fichier.
    
    Paramètres: Nom      |    Type
                chemin   |    str
                mat      |    numpy.array
    """
    fichier = open(chemin, "wb")
    #Sérialiser la matrice et la sauvegarder dans le fichier.
    pickle.dump(mat, fichier)
    #Libérer l'accès au fichier.
    fichier.close()
    
def fonctionPrincipale():
    """
    1) Créer la matrice d'occurence du corpus.
    2) La sauvegarder dans un fichier .dat (i.e data = données).
    
    Paramètres: Aucun
    """
    #/!\ La matrice pour un seul texte du corpus prend 1.7GiB de mémoire, donc on ne peut pas traiter
    #l'ensemble des textes. On se restreint au traitement de tiny.txt.
    #La matrice seule de tiny.txt a un poids de 200 Mb !
    
    #Créer la matrice du corpus complet.
    mat = matriceCorpusComplet()
    
    #Enregistrer la matrice dans un fichier .dat.
    sauvegarderMatrice("matrice_corpus.dat", mat)
    