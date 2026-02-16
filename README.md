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
* **Complexité JSON :** Les fichiers entreprises étaient au format JSON. Nous avons dû utiliser la fonction `FLATTEN` ou l'extraction directe `data:key::type` pour les transformer en colonnes exploitables.
* **Performance :** Pour optimiser les calculs, nous avons configuré le warehouse `COMPUTE_WH` en taille 'SMALL'.
* **Visualisation :** Adaptation des graphiques Streamlit (`st.bar_chart`) pour s'assurer que les axes X et Y soient correctement mappés sur les colonnes SQL.

---

## 📸 Captures d'écran du Dashboard

### 1 & 2. Analyses des Titres et Salaires par Industrie
*(Espace pour insérer la capture d'écran du menu déroulant et des graphiques de barres)*


### 3. Répartition par Taille d'Entreprise
*(Espace pour insérer la capture d'écran de l'analyse 3)*


### 4 & 5. Secteurs et Types de Contrats
*(Espace pour insérer la capture d'écran des répartitions globales)*


---

## 📬 Soumission
**Intitulé :** MBAESG_EVALUATION_ARCHITECTURE_BIGDATA  
**Destinataire :** axel@logbrain.fr  
**Dépôt GitHub :** [Lien vers votre dépôt]
