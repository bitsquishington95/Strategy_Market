import streamlit as st

from app.repository.store import Repository


def render_compare(repo: Repository) -> None:
    st.header("Comparative Analysis")
    names = sorted(repo.list_ceo_names())
    left, right = st.columns(2)
    with left:
        a = st.selectbox("CEO A", names, key="cmp_a")
    with right:
        b = st.selectbox("CEO B", names, key="cmp_b")
    trait = st.selectbox(
        "Trait",
        [
            "strategic_philosophy",
            "leadership",
            "operational_cadence",
            "personal_ethos",
        ],
    )
    if a and b:
        ap = repo.get_ceo(a).get(trait, {})
        bp = repo.get_ceo(b).get(trait, {})
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(a)
            for k, v in ap.items():
                st.markdown(f"**{k.replace('_',' ').title()}:** {v}")
        with c2:
            st.subheader(b)
            for k, v in bp.items():
                st.markdown(f"**{k.replace('_',' ').title()}:** {v}")


