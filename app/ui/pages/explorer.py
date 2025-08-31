import streamlit as st

from app.repository.store import Repository


def render_explorer(repo: Repository) -> None:
    st.header("CEO Explorer")
    names = sorted(repo.list_ceo_names())
    name = st.selectbox("Select CEO", names)
    if not name:
        return
    profile = repo.get_ceo(name)
    if not profile:
        st.info("No profile found.")
        return
    st.subheader(f"{name} Profile")
    for pillar_name, pillar in profile.items():
        with st.expander(pillar_name.capitalize(), expanded=False):
            if isinstance(pillar, dict):
                for key, value in pillar.items():
                    st.markdown(f"**{key.replace('_',' ').title()}:** {value}")
            else:
                st.write(pillar)


