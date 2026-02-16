import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd

# Configuration de la page
st.set_page_config(layout="wide", page_title="ANALYSE DES OFFRES D'EMPLOIES SUR LINKDIN")


session = get_active_session()

st.title("ANALYSE DES OFFRES D'EMPLOIES SUR LINKDIN")
st.markdown("Analyses haute performance des offres d'emploi")
st.write("")

# ========================================
# STATISTIQUES GLOBALES (COULEURS INTENSES)
# ========================================
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

def get_metric(query):
    try:
        return session.sql(query).collect()[0][0]
    except:
        return 0

with col_m1:
    total = get_metric('SELECT COUNT(*) FROM LINKEDIN.PUBLIC.JOB_POSTINGS')
    st.metric("TOTAL OFFRES", f"{total:,}", delta="LIVE")
with col_m2:
    comp = get_metric('SELECT COUNT(*) FROM LINKEDIN.PUBLIC.COMPANIES')
    st.metric("ENTREPRISES", f"{comp:,}")
with col_m3:
    sal = get_metric("SELECT ROUND(AVG((max_salary + min_salary)/2),0) FROM LINKEDIN.PUBLIC.JOB_POSTINGS WHERE max_salary > 0")
    st.metric("SALAIRE MOYEN", f"${sal:,.0f}" if sal else "N/A", delta="USD")
with col_m4:
    indus = get_metric('SELECT COUNT(DISTINCT industry) FROM LINKEDIN.PUBLIC.COMPANY_INDUSTRIES')
    st.metric("SECTEURS", f"{indus}")

st.write("")
st.divider()

# Préchargement des industries
industries_df = session.sql("SELECT DISTINCT industry FROM LINKEDIN.PUBLIC.COMPANY_INDUSTRIES WHERE industry IS NOT NULL ORDER BY industry").to_pandas()
industry_list = industries_df["INDUSTRY"].tolist()

# ========================================
# ANALYSES 1 & 2 : LES TOP 10 (CONTRASTE ÉLEVÉ)
# ========================================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("1-Top 10 Titres les plus demandés")
    ind1 = st.selectbox("Secteur cible", industry_list, key="sel1")
    
    query1 = f"""
        SELECT jp.title as TITRE, COUNT(DISTINCT jp.job_id) AS OFFRES
        FROM LINKEDIN.PUBLIC.JOB_POSTINGS jp
        JOIN LINKEDIN.PUBLIC.COMPANY_INDUSTRIES ci ON jp.company_id = ci.company_id
        WHERE ci.industry = '{ind1.replace("'", "''")}'
        GROUP BY 1 ORDER BY 2 DESC LIMIT 10
    """
    df1 = session.sql(query1).to_pandas()
    if not df1.empty:
        # Bleu Électrique Intense (#00D4FF)
        st.bar_chart(df1.sort_values("OFFRES", ascending=True), x="TITRE", y="OFFRES", horizontal=True, color="#00D4FF")
    else:
        st.warning("Données indisponibles.")

with col_right:
    st.subheader("2-Top 10 Rémunérations (Max)")
    ind2 = st.selectbox("Secteur cible", industry_list, key="sel2")
    
    query2 = f"""
        SELECT jp.title as TITRE, ROUND(AVG(jp.max_salary), 0) AS SALAIRE_MAX
        FROM LINKEDIN.PUBLIC.JOB_POSTINGS jp
        JOIN LINKEDIN.PUBLIC.COMPANY_INDUSTRIES ci ON jp.company_id = ci.company_id
        WHERE ci.industry = '{ind2.replace("'", "''")}' AND jp.max_salary > 0
        GROUP BY 1 HAVING COUNT(*) >= 2 ORDER BY 2 DESC LIMIT 10
    """
    df2 = session.sql(query2).to_pandas()
    if not df2.empty:
        # Corail Vibrant (#FF4B4B)
        st.bar_chart(df2.sort_values("SALAIRE_MAX", ascending=True), x="TITRE", y="SALAIRE_MAX", horizontal=True, color="#FF4B4B")
    else:
        st.warning("Données insuffisantes.")

st.write("")
st.divider()

# ========================================
# ANALYSES 3, 4 & 5 : RÉPARTITIONS STRUCTURELLES (LAYOUTS DÉDIÉS)
# ========================================
st.subheader("📊 Analyse Structurelle du Marché")
st.write("Vue éclatée des segments entreprises, secteurs et types d'emplois.")

# --- SECTION A : Taille des Entreprises (Pleine Largeur pour la progression) ---
with st.container():
    st.markdown("### 3-Répartition par Taille d'Entreprise")
    query3 = """
        SELECT CASE c.company_size 
            WHEN 0 THEN 'Très petite' WHEN 1 THEN 'Petite' WHEN 2 THEN 'PME' 
            WHEN 3 THEN 'Moyenne' WHEN 4 THEN 'Intermédiaire' WHEN 5 THEN 'Grande' 
            WHEN 6 THEN 'Très Grande' WHEN 7 THEN 'Géante' ELSE 'N/R' END AS TAILLE,
            COUNT(*) AS NB
        FROM LINKEDIN.PUBLIC.JOB_POSTINGS jp 
        JOIN LINKEDIN.PUBLIC.COMPANIES c ON jp.company_id = c.company_id
        GROUP BY c.company_size, 1 ORDER BY c.company_size ASC
    """
    # Affichage en pleine largeur pour bien voir la progression des tailles
    st.bar_chart(session.sql(query3).to_pandas(), x="TAILLE", y="NB", color="#10B981")

st.write("")

# --- SECTION B : Secteurs vs Types d'Emploi (Double Colonne pour comparaison) ---
col_secteur, col_type = st.columns(2)

with col_secteur:
    st.markdown("### 4-Répartition par Secteurs")
    query4 = "SELECT industry as SECTEUR, COUNT(*) as NB FROM LINKEDIN.PUBLIC.COMPANY_INDUSTRIES GROUP BY 1 ORDER BY 2 DESC LIMIT 15"
    df4 = session.sql(query4).to_pandas().sort_values("NB", ascending=True)
    # Indigo Intense (#6366F1)
    st.bar_chart(df4, x="SECTEUR", y="NB", horizontal=True, color="#6366F1")

with col_type:
    st.markdown("### 5- Répartition par Type d'Emploi")
    query5 = "SELECT COALESCE(formatted_work_type, 'N/R') as TYPE, COUNT(*) as NB FROM LINKEDIN.PUBLIC.JOB_POSTINGS GROUP BY 1 ORDER BY 2 DESC"
    df5 = session.sql(query5).to_pandas().sort_values("NB", ascending=True)
    # Ambre / Or (#F59E0B)
    st.bar_chart(df5, x="TYPE", y="NB", horizontal=True, color="#F59E0B")
