"""Artisan-Direct viability dashboard. Reads the result tables produced by code/02_clean_and_analyze.py.
Run:  streamlit run streamlit_app.py     (the survey data is SIMULATED)"""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

OUT = Path(__file__).resolve().parent
st.set_page_config(page_title="Artisan-Direct viability", page_icon="🧵", layout="wide")

@st.cache_data
def load(name):
    return pd.read_csv(OUT / f"result_{name}.csv")

kpi = load("kpi").set_index("metric")["value"]
clf, conf, dec, imp = load("clf_models"), load("clf_confusion"), load("clf_deciles"), load("clf_importance")
prof, pca, kdf = load("cluster_profile"), load("cluster_pca"), load("cluster_k")
rules, svc, pairs = load("rules"), load("svc_support"), load("pair_lift")
regm, regi, regt = load("reg_models"), load("reg_importance"), load("reg_by_tier")
scen, seg, sens = load("scenarios"), load("segment_econ"), load("sensitivity")
clean, outl = load("cleaning"), load("outliers")
dnum, score, cmap = load("descriptive_numeric"), load("algorithm_scorecard"), load("column_map")

st.title("🧵 Artisan-Direct: is the idea sustainable?")
st.caption("Mobile app connecting traditional artisans directly to customers. Survey data is simulated (seed 2026) with planted noise and outliers.")

page = st.sidebar.radio("Section", ["Overview", "1. Data quality", "2. Classification", "3. Clustering", "4. Association rules",
                                    "5. Regression", "6. Business viability", "Algorithm scorecard & column map"])

if page == "Overview":
    best = clf.sort_values("test_auc").iloc[-1]
    base = scen[scen.scenario == "Base"].iloc[0]
    c = st.columns(4)
    c[0].metric("Usable responses", f"{int(float(kpi.get('usable', 0))):,}", f"of {int(float(kpi.get('raw_responses', 0))):,} raw")
    c[1].metric("Best classifier AUC", f"{best.test_auc:.3f}", best.model)
    c[2].metric("Base LTV/CAC", f"{base.ltv_cac:.2f}", "target 3+")
    c[3].metric("Base break-even buyers", f"{int(base.breakeven_buyers):,}")
    st.subheader("Reading the verdict")
    st.write("Interest is predictable and concentrated in one segment, but unit economics only clear the usual 3x LTV/CAC bar in the optimistic case. "
             "The idea is viable if the app targets the high-probability segment and keeps acquisition cost low.")
    st.dataframe(kpi.reset_index(), hide_index=True, width="stretch")

elif page == "1. Data quality":
    st.subheader("Cleaning steps")
    st.dataframe(clean, hide_index=True, width="stretch")
    st.subheader("Outliers handled")
    st.dataframe(outl, hide_index=True, width="stretch")
    st.subheader("Descriptive statistics")
    st.dataframe(dnum, hide_index=True, width="stretch")

elif page == "2. Classification":
    st.subheader("Model comparison (interested = intent 4 or 5)")
    st.dataframe(clf, hide_index=True, width="stretch")
    a, b = st.columns(2)
    cm = conf.set_index("actual")
    a.plotly_chart(px.imshow(cm, text_auto=True, color_continuous_scale="Blues", title="Confusion matrix (hold-out)"), width="stretch")
    b.plotly_chart(px.bar(imp.sort_values("importance"), x="importance", y="feature", orientation="h", title="What drives interest"), width="stretch")
    st.plotly_chart(px.bar(dec, x="decile", y="interested_rate", title="Interested rate by predicted-score decile (lift)"), width="stretch")

elif page == "3. Clustering":
    st.subheader("Customer tiers (k-means, k=3)")
    st.dataframe(prof, hide_index=True, width="stretch")
    a, b = st.columns(2)
    a.plotly_chart(px.scatter(pca, x="pc1", y="pc2", color="tier", opacity=.5, title="PCA map of segments"), width="stretch")
    b.plotly_chart(px.line(kdf, x="k", y="silhouette", markers=True, title="Silhouette by number of clusters"), width="stretch")

elif page == "4. Association rules":
    a, b = st.columns(2)
    a.plotly_chart(px.bar(svc.sort_values("support_pct"), x="support_pct", y="service", orientation="h", title="Demand for each of the 10 services (%)"), width="stretch")
    p = pairs.pivot(index="a", columns="b", values="lift")
    b.plotly_chart(px.imshow(p, color_continuous_scale="Teal", title="Pairwise lift"), width="stretch")
    st.subheader("Strongest two-service rules")
    top = rules[rules.n_ante == 2].sort_values("lift", ascending=False)
    minsup = st.slider("Minimum support %", 2.0, 15.0, 5.0)
    st.dataframe(top[top.support_pct >= minsup][["rule_names", "support_pct", "confidence_pct", "lift"]].head(15), hide_index=True, width="stretch")

elif page == "5. Regression":
    st.subheader("Model comparison")
    st.dataframe(regm, hide_index=True, width="stretch")
    st.caption("R² on the log scale is the fair measure; plain OLS in rupees is hurt by outliers.")
    t = st.selectbox("Target", regi.target.unique())
    d = regi[regi.target == t].sort_values("importance")
    st.plotly_chart(px.bar(d, x="importance", y="feature", orientation="h", title=f"Drivers: {t}"), width="stretch")
    st.subheader("Spend by customer tier")
    st.dataframe(regt, hide_index=True, width="stretch")

elif page == "6. Business viability":
    st.subheader("Scenario economics (assumption-driven)")
    st.dataframe(scen, hide_index=True, width="stretch")
    st.plotly_chart(px.bar(scen, x="scenario", y="ltv_cac", title="LTV/CAC by scenario (3x = healthy)"), width="stretch")
    st.subheader("Segment economics")
    st.dataframe(seg, hide_index=True, width="stretch")
    st.subheader("Sensitivity: LTV/CAC vs acquisition cost and take rate")
    st.plotly_chart(px.imshow(sens.pivot(index="cac", columns="take_rate_pct", values="ltv_cac"), text_auto=True, color_continuous_scale="RdYlGn", aspect="auto"), width="stretch")
    st.info("Fixed cost, take rate, CAC and customer life are assumptions chosen for illustration, not survey findings.")

else:
    st.subheader("Algorithm scorecard")
    st.dataframe(score, hide_index=True, width="stretch")
    st.subheader("Which column feeds which algorithm")
    st.dataframe(cmap, hide_index=True, width="stretch")
