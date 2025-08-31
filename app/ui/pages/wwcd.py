import streamlit as st

from app.repository.store import Repository


def render_wwcd(repo: Repository) -> None:
    st.header("What Would a CEO Do?")
    situation = st.text_input(
        "Describe your situation",
        placeholder="missed quarterly target, key employee left, etc.",
    )
    if not situation:
        st.info("Enter a situation to see responses.")
        return
    results = repo.query_by_situation(situation)
    if not results:
        st.warning("No tagged responses found. Try different phrasing.")
        return
    for ceo_name, items in results.items():
        with st.expander(ceo_name, expanded=False):
            for item in items:
                st.markdown(f"- **{item['title']}**: {item['response']}")


