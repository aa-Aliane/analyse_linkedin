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
2.  **Top 10 des salaires par industrie :** Calcul du salaire maximum moyen par intitulé de poste pour comprendre les tendances de rémunération.
3.  **Répartition par taille d'entreprise :** Analyse du volume d'offres selon la structure (de la TPE à la multinationale).
4.  **Répartition par secteur d'activité :** Identification des secteurs les plus dynamiques sur le marché.
5.  **Répartition par type d'emploi :** Vue d'ensemble sur la nature des contrats (Temps plein, Freelance, Stage).

---

## 🚀 Problèmes Rencontrés & Solutions
* **Valeurs NULL dans les clés primaires :** 12,8% des entreprises (21 993 sur 172 291) avaient des company_id NULL. Solution : Génération automatique d'IDs négatifs via ROW_NUMBER() avec un flag is_generated_id pour la traçabilité.
* **Complexité JSON :** Les fichiers entreprises étaient au format JSON. Nous avons dû utiliser la fonction `FLATTEN` ou l'extraction directe `data:key::type` pour les transformer en colonnes exploitables.
* **Performance :** Pour optimiser les calculs, nous avons configuré le warehouse `COMPUTE_WH` en taille 'SMALL'.
* **Visualisation :** Adaptation des graphiques Streamlit (`st.bar_chart`) pour s'assurer que les axes X et Y soient correctement mappés sur les colonnes SQL.

---

## 📸 Captures d'écran du Dashboard

### 1 & 2. Analyses des Titres et Salaires par Industrie
<img width="1507" height="734" alt="image" src="https://github.com/user-attachments/assets/21b9c47c-02dc-4afa-ba92-72ca0684884a" />
<img width="1487" height="655" alt="image" src="https://github.com/user-attachments/assets/7d7574d1-f2f1-4b8a-9013-8d5df098173c" />



### 3. Répartition par Taille d'Entreprise
<img width="1499" height="556" alt="image" src="https://github.com/user-attachments/assets/ce243602-a720-401b-8426-8a5e9f2db0ed" />



### 4 & 5. Secteurs et Types de Contrats
<img width="1505" height="515" alt="image" src="https://github.com/user-attachments/assets/61e87f16-113d-4ca4-9718-57bad37b85f9" />
<img width="1468" height="544" alt="image" src="https://github.com/user-attachments/assets/702f4914-87a0-48c4-b091-c41be6d455d4" />



---

