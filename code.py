import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(layout="wide", page_title="LinkedIn Dashboard")
st.title("📊 Analyse des Offres d'Emploi LinkedIn")

session = get_active_session()

# ========================================
# ANALYSE 1 : Top 10 titres par industrie
# ========================================
st.header("1️⃣ Top 10 des titres de postes par industrie")
try:
    industries_df = session.sql("""
        SELECT DISTINCT industry 
        FROM LINKEDIN.PUBLIC.COMPANY_INDUSTRIES 
        WHERE industry IS NOT NULL 
        ORDER BY industry
    """).to_pandas()
    
    if not industries_df.empty:
        selected_industry = st.selectbox(
            "Sélectionnez un secteur", 
            industries_df["INDUSTRY"].tolist(), 
            key="ind1"
        )
        
        safe_industry = selected_industry.replace("'", "''")
        
        query1 = f"""
        SELECT 
            jp.title, 
            COUNT(DISTINCT jp.job_id) AS nb_offres
        FROM LINKEDIN.PUBLIC.JOB_POSTINGS jp
        JOIN LINKEDIN.PUBLIC.COMPANIES c ON jp.company_id = c.company_id
        JOIN LINKEDIN.PUBLIC.COMPANY_INDUSTRIES ci ON c.company_id = ci.company_id
        WHERE ci.industry = '{safe_industry}'
            AND jp.title IS NOT NULL
        GROUP BY jp.title
        ORDER BY nb_offres DESC
        LIMIT 10
        """
        
        df1 = session.sql(query1).to_pandas()
        
        if not df1.empty:
            st.bar_chart(data=df1, x="TITLE", y="NB_OFFRES", height=400)
            st.dataframe(df1, use_container_width=True)
        else:
            st.warning("Aucune donnée pour cette industrie.")
    else:
        st.error("Impossible de charger les industries.")
        
except Exception as e:
    st.error(f"Erreur Analyse 1 : {e}")

st.divider()

# ========================================
# ANALYSE 2 : Top 10 salaires par industrie 
# ========================================
st.header("2️⃣ Top 10 des postes les mieux rémunérés par industrie")
try:
    if 'industries_df' not in locals() or industries_df.empty:
        industries_df = session.sql("""
            SELECT DISTINCT industry 
            FROM LINKEDIN.PUBLIC.COMPANY_INDUSTRIES 
            WHERE industry IS NOT NULL 
            ORDER BY industry
        """).to_pandas()
    
    if not industries_df.empty:
        selected_industry2 = st.selectbox(
            "Sélectionnez un secteur", 
            industries_df["INDUSTRY"].tolist(), 
            key="ind2"
        )
        
        safe_industry2 = selected_industry2.replace("'", "''")
        
        query2 = f"""
        SELECT 
            jp.title,
            ROUND(AVG(jp.max_salary), 0) AS salaire_max_moyen,
            ROUND(AVG(jp.min_salary), 0) AS salaire_min_moyen,
            ROUND(AVG((jp.max_salary + jp.min_salary) / 2), 0) AS salaire_moyen_estime,
            COUNT(DISTINCT jp.job_id) AS nb_offres
        FROM LINKEDIN.PUBLIC.JOB_POSTINGS jp
        JOIN LINKEDIN.PUBLIC.COMPANIES c ON jp.company_id = c.company_id
        JOIN LINKEDIN.PUBLIC.COMPANY_INDUSTRIES ci ON c.company_id = ci.company_id
        WHERE ci.industry = '{safe_industry2}'
            AND jp.max_salary IS NOT NULL
            AND jp.max_salary > 0
            AND jp.max_salary < 1000000
        GROUP BY jp.title
        HAVING COUNT(DISTINCT jp.job_id) >= 2
        ORDER BY salaire_max_moyen DESC
        LIMIT 10
        """
        
        df2 = session.sql(query2).to_pandas()
        
        if not df2.empty:
            # Graphique avec MAX salary
            st.bar_chart(data=df2, x="TITLE", y="SALAIRE_MAX_MOYEN", height=400)
            st.dataframe(df2, use_container_width=True)
        else:
            st.warning("Aucune donnée de salaire pour cette industrie.")
    else:
        st.error("Impossible de charger les industries.")
        
except Exception as e:
    st.error(f"Erreur Analyse 2 : {e}")

st.divider()

# ========================================
# ANALYSE 3 : Répartition par taille d'entreprise 
# ========================================
st.header("3️⃣ Répartition des offres par taille d'entreprise")
try:
    query3 = """
    WITH sizes AS (
        SELECT 
            c.company_size,
            CASE 
                WHEN c.company_size = 0 THEN '0 - Très petite'
                WHEN c.company_size = 1 THEN '1 - Petite'
                WHEN c.company_size = 2 THEN '2 - Petite-Moyenne'
                WHEN c.company_size = 3 THEN '3 - Moyenne'
                WHEN c.company_size = 4 THEN '4 - Moyenne-Grande'
                WHEN c.company_size = 5 THEN '5 - Grande'
                WHEN c.company_size = 6 THEN '6 - Très Grande'
                WHEN c.company_size = 7 THEN '7 - Géante'
                ELSE 'Non renseigné'
            END AS taille,
            COUNT(DISTINCT jp.job_id) AS nb_offres
        FROM LINKEDIN.PUBLIC.JOB_POSTINGS jp
        JOIN LINKEDIN.PUBLIC.COMPANIES c ON jp.company_id = c.company_id
        GROUP BY c.company_size, taille
    )
    SELECT taille, nb_offres
    FROM sizes
    ORDER BY COALESCE(company_size, 99)
    """
    
    df3 = session.sql(query3).to_pandas()
    
    if not df3.empty:
        st.bar_chart(data=df3, x="TAILLE", y="NB_OFFRES", height=400)
        st.dataframe(df3, use_container_width=True)
    else:
        st.warning("Aucune donnée.")
        
except Exception as e:
    st.error(f"Erreur Analyse 3 : {e}")

st.divider()

# ========================================
# ANALYSE 4 : Répartition par secteur d'activité
# ========================================
st.header("4️⃣ Répartition des offres par secteur d'activité")
try:
    query4 = """
    SELECT 
        ci.industry AS secteur,
        COUNT(DISTINCT jp.job_id) AS nb_offres
    FROM LINKEDIN.PUBLIC.JOB_POSTINGS jp
    JOIN LINKEDIN.PUBLIC.COMPANIES c ON jp.company_id = c.company_id
    JOIN LINKEDIN.PUBLIC.COMPANY_INDUSTRIES ci ON c.company_id = ci.company_id
    WHERE ci.industry IS NOT NULL
    GROUP BY ci.industry
    ORDER BY nb_offres DESC
    LIMIT 15
    """
    
    df4 = session.sql(query4).to_pandas()
    
    if not df4.empty:
        st.bar_chart(data=df4, x="SECTEUR", y="NB_OFFRES", height=400)
        st.dataframe(df4, use_container_width=True)
    else:
        st.warning("Aucune donnée.")
        
except Exception as e:
    st.error(f"Erreur Analyse 4 : {e}")

st.divider()

# ========================================
# ANALYSE 5 : Répartition par type d'emploi
# ========================================
st.header("5️⃣ Répartition des offres par type d'emploi")
try:
    query5 = """
    SELECT 
        COALESCE(formatted_work_type, 'Non renseigné') AS type_emploi,
        COUNT(*) AS nb_offres,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pourcentage
    FROM LINKEDIN.PUBLIC.JOB_POSTINGS
    GROUP BY formatted_work_type
    ORDER BY nb_offres DESC
    """
    
    df5 = session.sql(query5).to_pandas()
    
    if not df5.empty:
        st.bar_chart(data=df5, x="TYPE_EMPLOI", y="NB_OFFRES", height=400)
        st.dataframe(df5, use_container_width=True)
    else:
        st.warning("Aucune donnée.")
        
except Exception as e:
    st.error(f"Erreur Analyse 5 : {e}")

# ========================================
# STATISTIQUES GLOBALES 
# ========================================
st.divider()
st.subheader("📈 Statistiques Globales")

col1, col2, col3, col4 = st.columns(4)

try:
    total_jobs = session.sql("SELECT COUNT(*) as total FROM LINKEDIN.PUBLIC.JOB_POSTINGS").to_pandas()
    col1.metric("Total Offres", f"{total_jobs['TOTAL'].iloc[0]:,}")
except:
    col1.metric("Total Offres", "N/A")

try:
    total_companies = session.sql("SELECT COUNT(*) as total FROM LINKEDIN.PUBLIC.COMPANIES").to_pandas()
    col2.metric("Total Entreprises", f"{total_companies['TOTAL'].iloc[0]:,}")
except:
    col2.metric("Total Entreprises", "N/A")

try:
    # CORRIGÉ : Utiliser la moyenne entre MAX et MIN au lieu de MED
    avg_salary = session.sql("""
        SELECT ROUND(AVG((max_salary + min_salary) / 2), 0) as avg_sal 
        FROM LINKEDIN.PUBLIC.JOB_POSTINGS 
        WHERE max_salary > 0 
            AND min_salary > 0
            AND max_salary < 1000000
    """).to_pandas()
    col3.metric("Salaire Moyen Estimé", f"${avg_salary['AVG_SAL'].iloc[0]:,.0f}")
except:
    col3.metric("Salaire Moyen Estimé", "N/A")

try:
    total_industries = session.sql("""
        SELECT COUNT(DISTINCT industry) as total 
        FROM LINKEDIN.PUBLIC.COMPANY_INDUSTRIES
    """).to_pandas()
    col4.metric("Secteurs d'activité", f"{total_industries['TOTAL'].iloc[0]}")
except:
    col4.metric("Secteurs d'activité", "N/A")

st.caption("📊 Source : LinkedIn Job Postings - Snowflake Analytics")
