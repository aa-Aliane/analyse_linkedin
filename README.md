# 🧊 Projet : Analyse des Offres d'Emploi LinkedIn avec Snowflake & Streamlit

## 👥 Équipe de Projet (Groupe MBA ESG)
* **ALIANE Ahamed Amine**
* **TSOPBENG Joyce Terrence**
* **IDIRI Anis**
* **VAILLAUD Sixtine**
* **ALAIN Kelako**

---

## 🎯 Présentation du Projet
Ce projet consiste à concevoir une solution de Business Intelligence de bout en bout. L'objectif est d'extraire, transformer et visualiser des données massives provenant de LinkedIn (offres d'emploi, entreprises, secteurs, salaires). 

Le flux de données suit le parcours suivant :
1.  **Extraction** depuis un bucket Amazon S3 public.
2.  **Ingestion & Stockage** dans le Data Warehouse Snowflake.
3.  **Transformation** SQL pour structurer les données JSON et CSV.
4.  **Visualisation** via un dashboard interactif développé avec Streamlit.

---

## 🛠️ Architecture Technique

### 1. Ingestion des Données (SQL)
Nous avons configuré l'infrastructure Snowflake pour automatiser l'importation :
* **Stage Externe :** Création d'un lien direct vers `s3://snowflake-lab-bucket/`.
* **Formats de Fichiers :** * Un format **CSV** spécifique (gestion des en-têtes et des guillemets optionnels).
    * Un format **JSON** pour les données semi-structurées des entreprises et industries.
* **Chargement :** Utilisation de la commande `COPY INTO` pour peupler les tables. Pour les fichiers JSON, nous avons utilisé des tables temporaires avec le type `VARIANT` avant d'extraire les clés dans des tables relationnelles propres.

### 2. Développement du Dashboard (Python / Streamlit)
Le dashboard intégré à Snowflake permet de filtrer les données en temps réel :
* **Requêtes Dynamiques :** Utilisation de `session.sql()` pour lier les widgets Streamlit aux données Snowflake.
* **Sécurité :** Nettoyage des entrées utilisateurs (gestion des apostrophes dans les noms de secteurs).

---

## 📊 Analyses Réalisées

Le dashboard se décompose en 5 axes d'analyse :

1.  **Top 10 des titres de postes par industrie :** Identification des métiers les plus demandés selon le secteur choisi.
   <img width="790" height="507" alt="image" src="https://github.com/user-attachments/assets/67b5b078-eca4-41c6-a061-ba182734c92a" />

2.  **Top 10 des salaires par industrie :** Calcul du salaire maximum moyen par intitulé de poste pour comprendre les tendances de rémunération.
   <img width="781" height="524" alt="image" src="https://github.com/user-attachments/assets/8377dcd4-36d5-4083-9ae6-2c1cc184fc29" />

3.  **Répartition par taille d'entreprise :** Analyse du volume d'offres selon la structure.
   <img width="786" height="622" alt="image" src="https://github.com/user-attachments/assets/63e39601-012d-4cd1-ac56-c51f76e4d6fb" />

4.  **Répartition par secteur d'activité :** Identification des secteurs les plus dynamiques sur le marché.
   <img width="794" height="546" alt="image" src="https://github.com/user-attachments/assets/f97dffb9-c27b-4d12-8d73-69df426be5af" />

5.  **Répartition par type d'emploi :** Vue d'ensemble sur la nature des contrats
   <img width="782" height="361" alt="image" src="https://github.com/user-attachments/assets/86bad3c5-9ac1-4ef0-98aa-bf6b0eb9c0dd" />

   

---

## 🚀 Problèmes Rencontrés & Solutions
* **Valeurs NULL dans les clés primaires :** 12,8% des entreprises (21 993 sur 172 291) avaient des company_id NULL. Solution : Génération automatique d'IDs négatifs via ROW_NUMBER() avec un flag is_generated_id pour la traçabilité.
* **Complexité JSON :** Les fichiers entreprises étaient au format JSON. Nous avons dû utiliser la fonction `FLATTEN` ou l'extraction directe `data:key::type` pour les transformer en colonnes exploitables.
* **Performance :** Pour optimiser les calculs, nous avons configuré le warehouse `COMPUTE_WH` en taille 'SMALL'.
* **Visualisation :** Adaptation des graphiques Streamlit (`st.bar_chart`) pour s'assurer que les axes X et Y soient correctement mappés sur les colonnes SQL.

---




---

