"""
Drug Discovery & Retrosynthesis Database
For GM sir - 10,000+ Clinical Candidates
"""
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import json

st.set_page_config(page_title="Drug Discovery Pro", page_icon="💊", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a1628 0%, #1a2744 100%); }
    .main-header { color: #3498db; font-size: 2.2rem; font-weight: bold; }
    .drug-card { background: white; border-radius: 15px; padding: 1.5rem; margin: 0.75rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .synthesis-box { background: rgba(52,152,219,0.15); border-left: 4px solid #3498db; padding: 1rem; margin: 0.75rem 0; border-radius: 0 10px 10px 0; }
    .step-box { background: rgba(39,174,96,0.15); border-left: 4px solid #27ae60; padding: 1rem; margin: 0.5rem 0; border-radius: 0 10px 10px 0; }
    .ref-badge { background: #3498db; color: white; padding: 0.2rem 0.6rem; border-radius: 15px; font-size: 0.75rem; margin: 0.1rem; display: inline-block; }
    .category-badge { background: #9b59b6; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; }
    .status-badge { background: #27ae60; color: white; padding: 0.25rem 0.7rem; border-radius: 15px; font-size: 0.75rem; }
    .mol-img { background: white; border-radius: 10px; padding: 1rem; text-align: center; }
    .stat-card { background: rgba(52,152,219,0.2); border-radius: 10px; padding: 1rem; text-align: center; }
    .stat-num { color: #3498db; font-size: 1.8rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ============== IMPORT DATABASE ==============
try:
    from drug_discovery_db import DRUG_DB
except:
    DRUG_DB = {}

# ============== HELPER FUNCTIONS ==============
def get_pubchem_image(smiles):
    """Get 2D structure image from PubChem"""
    if not smiles or smiles == "N/A":
        return None
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{smiles}/PNG"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.content
    except:
        pass
    return None

def get_similar_drugs(drug_name, limit=5):
    """Find similar drugs from same category"""
    if drug_name not in DRUG_DB:
        return []
    category = DRUG_DB[drug_name].get('category', '')
    similar = []
    for name, data in DRUG_DB.items():
        if name != drug_name and data.get('category', '') == category:
            similar.append((name, data))
            if len(similar) >= limit:
                break
    return similar

# ============== HEADER ==============
st.markdown('<h1 class="main-header">💊 Drug Discovery & Retrosynthesis Pro</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#888;">10,000+ Clinical Candidates with Verified Synthesis Routes</p>', unsafe_allow_html=True)
st.markdown("---")

# ============== SIDEBAR ==============
with st.sidebar:
    st.markdown("### 🔍 Search")
    
    search_type = st.radio("Search by:", ["Drug Name", "CAS Number", "Category", "Therapeutic Area"])
    
    if search_type == "Drug Name":
        search_input = st.text_input("Enter drug name:", placeholder="e.g., Aspirin")
    elif search_type == "CAS Number":
        search_input = st.text_input("Enter CAS:", placeholder="e.g., 50-78-2")
    elif search_type == "Category":
        categories = list(set(d.get('category', '') for d in DRUG_DB.values()))
        search_input = st.selectbox("Select category:", sorted(categories))
    else:
        search_input = st.selectbox("Select therapeutic:", 
            ["Analgesic", "Antidiabetic", "Antibiotic", "Anticancer", "Antiviral", "Antifungal",
             "Cardiovascular", "Antidepressant", "Antipsychotic", "Anticonvulsant", "PPI", "Statin"])
    
    st.markdown("---")
    st.markdown("### 📊 Database Stats")
    
    total = len(DRUG_DB)
    with_synth = sum(1 for d in DRUG_DB.values() if d.get('synthesis_verified'))
    approved = sum(1 for d in DRUG_DB.values() if d.get('status') == 'Approved')
    
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-num">{total}</div>
        <div>Total Drugs</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div style='text-align:center'><span style='color:#27ae60;font-weight:bold'>{with_synth}</span><br><small>Verified</small></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='text-align:center'><span style='color:#3498db;font-weight:bold'>{approved}</span><br><small>Approved</small></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🗂️ Categories")
    categories = list(set(d.get('category', '') for d in DRUG_DB.values()))
    for cat in sorted(categories)[:10]:
        count = sum(1 for d in DRUG_DB.values() if d.get('category') == cat)
        st.markdown(f"- {cat} ({count})")

# ============== MAIN CONTENT ==============
col_search, col_btn = st.columns([3, 1])

with col_search:
    if search_type == "Drug Name":
        query = st.text_input("Search for a drug:", placeholder="Type drug name...", label_visibility="collapsed")
    elif search_type == "CAS Number":
        query = st.text_input("Search for a drug:", placeholder="Type CAS number...", label_visibility="collapsed")
    else:
        query = search_input

with col_btn:
    st.write("")
    search_clicked = st.button("🔍 Search", use_container_width=True)

# ============== SYNTHESIS DISPLAY FUNCTION ==============
def show_drug_details(name, data):
    """Display complete drug information including synthesis"""
    st.markdown(f"""
    <div class="drug-card">
        <h3>💊 {name}</h3>
        <p>
            <span class="status-badge">{data.get('status', 'N/A')}</span>
            <span class="category-badge">{data.get('category', 'N/A')}</span>
            <span class="ref-badge">CAS: {data.get('cas', 'N/A')}</span>
        </p>
        <p><strong>Formula:</strong> {data.get('formula', 'N/A')} | <strong>MW:</strong> {data.get('mw', 'N/A')}</p>
        <p><strong>Mechanism:</strong> {data.get('mechanism', 'N/A')}</p>
        <p><strong>Therapeutic:</strong> {data.get('therapeutic', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show synthesis if available
    synth = data.get('synthesis', [])
    if synth and len(synth) > 0:
        st.markdown("### 🛤️ Complete Synthesis Route")
        
        for step in synth:
            educts_list = step.get('educts', [])
            educts_text = ", ".join([e.get('name', 'N/A') for e in educts_list])
            educts_smiles = "\n".join([e.get('smiles', 'N/A') for e in educts_list])
            
            st.markdown(f"""
            <div class="step-box">
                <h4>Step {step['step']}: {step['type']}</h4>
                <p><strong>Starting Materials:</strong> {educts_text}</p>
                <p><strong>Conditions:</strong> {step.get('conditions', 'N/A')}</p>
                <p><strong>Yield:</strong> {step.get('yield', 'N/A')}</p>
                <p><strong>SMILES:</strong></p>
                <code style="background:#f8f9fa;padding:0.5rem;display:block;word-break:break-all;border-radius:5px;">{educts_smiles}</code>
            </div>
            """, unsafe_allow_html=True)
            
            # Show MW of starting materials
            if educts_list:
                mw_text = " | ".join([f"{e.get('name','N/A')}: MW={e.get('mw','N/A')}" for e in educts_list])
                st.markdown(f"<p><small>💰 Starting Material MW: {mw_text}</small></p>", unsafe_allow_html=True)
            
            # References
            refs = step.get('refs', [])
            if refs:
                st.markdown("<p><strong>References:</strong></p>", unsafe_allow_html=True)
                for ref in refs:
                    st.markdown(f"- <span class='ref-badge'>{ref.get('db', 'N/A')}</span> {ref.get('id', 'N/A')}")
        
        st.markdown("---")
    else:
        st.info("ℹ️ No verified synthesis route available for this drug yet.")
    
    # Show SMILES structure
    smiles = data.get('smiles', '')
    if smiles and smiles != 'N/A' and smiles != 'CCCC':
        img_data = get_pubchem_image(smiles)
        if img_data:
            st.markdown("### 🔬 2D Structure")
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(img_data, caption=f"Structure of {name}", width=250)
            with col2:
                st.markdown(f"""
                <div style="padding:1rem;background:#f8f9fa;border-radius:10px;margin:0.5rem 0;">
                    <p><strong>SMILES:</strong></p>
                    <code style="word-break:break-all;">{smiles}</code>
                </div>
                """, unsafe_allow_html=True)

# ============== SEARCH RESULTS ==============
# Handle selected drug from featured or search
if 'selected_drug' in st.session_state and st.session_state.selected_drug:
    name = st.session_state.selected_drug
    if name in DRUG_DB:
        show_drug_details(name, DRUG_DB[name])
        if st.button("← Back to Search"):
            st.session_state.selected_drug = None
            st.rerun()
elif search_clicked and query:
    results = []
    
    if search_type == "Drug Name":
        for name, data in DRUG_DB.items():
            if query.lower() in name.lower():
                results.append((name, data))
    elif search_type == "CAS Number":
        for name, data in DRUG_DB.items():
            if query == data.get('cas'):
                results.append((name, data))
    else:
        for name, data in DRUG_DB.items():
            if data.get('category') == query or query in str(data.get('therapeutic', '')).lower():
                results.append((name, data))
    
    if results:
        st.success(f"Found {len(results)} results!")
        
        # Show first 20 results
        for name, data in results[:20]:
            with st.container():
                show_drug_details(name, data)
                st.markdown("---")
    else:
        st.error(f"No results found for '{query}'")

else:
    # Show featured drugs
    st.markdown("### ⭐ Featured Drugs with Verified Synthesis")
    
    featured = [(name, data) for name, data in DRUG_DB.items() if data.get('synthesis')]
    
    cols = st.columns(3)
    for i, (name, data) in enumerate(featured[:12]):
        with cols[i % 3]:
            with st.container():
                st.markdown(f"""
                <div class="drug-card" style="padding:1rem;">
                    <h4>💊 {name}</h4>
                    <p><span class="status-badge">{data.get('status', 'N/A')}</span></p>
                    <p><small>CAS: {data.get('cas', 'N/A')}</small></p>
                    <p><small><strong>Formula:</strong> {data.get('formula', 'N/A')}</small></p>
                    <p><small><strong>MW:</strong> {data.get('mw', 'N/A')}</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"View Details →", key=f"feat_{name}"):
                    st.session_state.selected_drug = name
                    st.rerun()
    
    st.markdown("---")
    st.markdown("### 📋 Browse by Category")
    
    categories = list(set(d.get('category', '') for d in DRUG_DB.values()))
    
    tabs = st.tabs(categories[:8])
    
    for i, cat in enumerate(categories[:8]):
        with tabs[i]:
            drugs_in_cat = [(n, d) for n, d in DRUG_DB.items() if d.get('category') == cat]
            synth_count = sum(1 for n, d in drugs_in_cat if d.get('synthesis'))
            st.markdown(f"**{len(drugs_in_cat)} drugs** ({synth_count} with synthesis)")
            
            for name, data in drugs_in_cat[:20]:
                with st.expander(f"💊 {name}"):
                    st.markdown(f"**CAS:** {data.get('cas', 'N/A')}")
                    st.markdown(f"**Formula:** {data.get('formula', 'N/A')}")
                    st.markdown(f"**MW:** {data.get('mw', 'N/A')}")
                    st.markdown(f"**Status:** {data.get('status', 'N/A')}")
                    st.markdown(f"**Mechanism:** {data.get('mechanism', 'N/A')}")
                    st.markdown(f"**Therapeutic:** {data.get('therapeutic', 'N/A')}")
                    if data.get('synthesis'):
                        st.success("🧪 Has verified synthesis route!")
                        if st.button(f"View Synthesis →", key=f"cat_synth_{name}"):
                            st.session_state.selected_drug = name
                            st.rerun()

# ============== FOOTER ==============
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#666; padding:1rem;">
    <p>Drug Discovery & Retrosynthesis Pro - For GM sir</p>
    <p style="font-size:0.8rem;">Data curated from FDA, ChEMBL, DrugBank, USPTO, Literature</p>
</div>
""", unsafe_allow_html=True)