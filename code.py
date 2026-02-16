import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(layout="wide", page_title="LinkedIn Dashboard")
st.title("Analyse des Offres d'Emploi LinkedIn")

session = get_active_session()

# ANALYSE 1 : Top 10 titres par industrie
st.header("1 - Top 10 des titres de postes par industrie")

try:
    industries_df = session.sql("SELECT DISTINCT industry FROM LINKEDIN.PUBLIC.COMPANY_INDUSTRIES WHERE industry IS NOT NULL ORDER BY industry").to_pandas()
    selected_industry = st.selectbox("Selectionnez un secteur", industries_df["INDUSTRY"].tolist(), key="ind1")
    safe_industry = selected_industry.replace("'", "''")
    query1 = f"SELECT jp.title, COUNT(*) AS nb_offres FROM LINKEDIN.PUBLIC.JOB_POSTINGS jp JOIN LINKEDIN.PUBLIC.COMPANY_INDUSTRIES ci ON ci.company_id = jp.company_id WHERE ci.industry = '{safe_industry}' GROUP BY jp.title ORDER BY nb_offres DESC LIMIT 10"
    df1 = session.sql(query1).to_pandas()
    if not df1.empty:
        st.bar_chart(data=df1, x="TITLE", y="NB_OFFRES")
        st.dataframe(df1, use_container_width=True)
    else:
        st.warning("Aucune donnee pour cette industrie.")
except Exception as e:
    st.error(f"Erreur Analyse 1 : {e}")

st.divider()

# ANALYSE 2 : Top 10 salaires par industrie
st.header("2 - Top 10 des postes les mieux remuneres par industrie")

try:
    selected_industry2 = st.selectbox("Selectionnez un secteur", industries_df["INDUSTRY"].tolist(), key="ind2")
    safe_industry2 = selected_industry2.replace("'", "''")
    query2 = f"SELECT jp.title, ROUND(AVG(jp.max_salary), 2) AS avg_max_salary FROM LINKEDIN.PUBLIC.JOB_POSTINGS jp JOIN LINKEDIN.PUBLIC.COMPANY_INDUSTRIES ci ON ci.company_id = jp.company_id WHERE jp.max_salary IS NOT NULL AND ci.industry = '{safe_industry2}' GROUP BY jp.title ORDER BY avg_max_salary DESC LIMIT 10"
    df2 = session.sql(query2).to_pandas()
    if not df2.empty:
        st.bar_chart(data=df2, x="TITLE", y="AVG_MAX_SALARY")
        st.dataframe(df2, use_container_width=True)
    else:
        st.warning("Aucune donnee de salaire pour cette industrie.")
except Exception as e:
    st.error(f"Erreur Analyse 2 : {e}")

st.divider()

# ANALYSE 3 : Repartition par taille d entreprise
st.header("3 - Repartition des offres par taille d entreprise")

try:
    query3 = "SELECT CASE c.company_size WHEN 0 THEN '0 - Tres petite' WHEN 1 THEN '1 - Petite' WHEN 2 THEN '2 - Petite-Moyenne' WHEN 3 THEN '3 - Moyenne' WHEN 4 THEN '4 - Moyenne-Grande' WHEN 5 THEN '5 - Grande' WHEN 6 THEN '6 - Tres Grande' WHEN 7 THEN '7 - Geante' ELSE 'Non renseigne' END AS taille, COUNT(*) AS nb_offres FROM LINKEDIN.PUBLIC.JOB_POSTINGS jp JOIN LINKEDIN.PUBLIC.COMPANIES c ON jp.company_id = c.company_id GROUP BY taille ORDER BY nb_offres DESC"
    df3 = session.sql(query3).to_pandas()
    if not df3.empty:
        st.bar_chart(data=df3, x="TAILLE", y="NB_OFFRES")
        st.dataframe(df3, use_container_width=True)
    else:
        st.warning("Aucune donnee.")
except Exception as e:
    st.error(f"Erreur Analyse 3 : {e}")

st.divider()

# ANALYSE 4 : Repartition par secteur d activite
st.header("4 - Repartition des offres par secteur d activite")

try:
    query4 = "SELECT ci.industry AS secteur, COUNT(*) AS nb_offres FROM LINKEDIN.PUBLIC.JOB_POSTINGS jp JOIN LINKEDIN.PUBLIC.COMPANY_INDUSTRIES ci ON ci.company_id = jp.company_id WHERE ci.industry IS NOT NULL GROUP BY ci.industry ORDER BY nb_offres DESC LIMIT 15"
    df4 = session.sql(query4).to_pandas()
    if not df4.empty:
        st.bar_chart(data=df4, x="SECTEUR", y="NB_OFFRES")
        st.dataframe(df4, use_container_width=True)
    else:
        st.warning("Aucune donnee.")
except Exception as e:
    st.error(f"Erreur Analyse 4 : {e}")

st.divider()

# ANALYSE 5 : Repartition par type d emploi
st.header("5 - Repartition des offres par type d emploi")

try:
    query5 = "SELECT COALESCE(formatted_work_type, 'Non renseigne') AS type_emploi, COUNT(*) AS nb_offres FROM LINKEDIN.PUBLIC.JOB_POSTINGS GROUP BY type_emploi ORDER BY nb_offres DESC"
    df5 = session.sql(query5).to_pandas()
    if not df5.empty:
        st.bar_chart(data=df5, x="TYPE_EMPLOI", y="NB_OFFRES")
        st.dataframe(df5, use_container_width=True)
    else:
        st.warning("Aucune donnee.")
except Exception as e:
    st.error(f"Erreur Analyse 5 : {e}")

st.caption("Source : LinkedIn Job Postings - Snowflake Analytics")
