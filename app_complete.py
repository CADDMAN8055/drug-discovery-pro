"""
Drug Discovery - Complete Retrosynthesis Database
Full ROS: Commercial + AI-Predicted Novel Routes
For GM sir - 46 drugs with complete synthesis information
"""
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Complete Retrosynthesis Pro", page_icon="🧬", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a1628 0%, #1a2744 100%); }
    .main-header { color: #00d4ff; font-size: 2.2rem; font-weight: bold; }
    .drug-card { background: white; border-radius: 15px; padding: 1.5rem; margin: 0.75rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .synth-box { background: rgba(52,152,219,0.15); border-left: 4px solid #3498db; padding: 1rem; margin: 0.75rem 0; border-radius: 0 10px 10px 0; }
    .step-box { background: rgba(39,174,96,0.15); border-left: 4px solid #27ae60; padding: 1rem; margin: 0.5rem 0; border-radius: 0 10px 10px 0; }
    .ksm-box { background: rgba(155,89,182,0.15); border-left: 4px solid #9b59b6; padding: 1rem; margin: 0.5rem 0; border-radius: 0 10px 10px 0; }
    .ai-box { background: rgba(230,126,34,0.15); border-left: 4px solid #e67e22; padding: 1rem; margin: 0.5rem 0; border-radius: 0 10px 10px 0; }
    .ref-badge { background: #3498db; color: white; padding: 0.2rem 0.6rem; border-radius: 15px; font-size: 0.75rem; margin: 0.1rem; display: inline-block; }
    .category-badge { background: #9b59b6; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; }
    .status-badge { background: #27ae60; color: white; padding: 0.25rem 0.7rem; border-radius: 15px; font-size: 0.75rem; }
    .confidence-badge { background: #e67e22; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; }
    .mol-img { background: white; border-radius: 10px; padding: 1rem; text-align: center; }
    .stat-card { background: rgba(52,152,219,0.2); border-radius: 10px; padding: 1rem; text-align: center; }
    .stat-num { color: #3498db; font-size: 1.8rem; font-weight: bold; }
    .yield-high { color: #27ae60; font-weight: bold; }
    .yield-med { color: #f39c12; font-weight: bold; }
    .yield-low { color: #e74c3c; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🧬 Complete Retrosynthesis Pro</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#88a4c4;">Full Commercial Routes + AI-Predicted Novel Routes with ALL Intermediates</p>', unsafe_allow_html=True)
st.markdown("---")

# Import database
try:
    from complete_retro_db import DRUG_DB
except:
    DRUG_DB = {}

def get_pubchem_image(smiles, size=300):
    """Get 2D structure image from PubChem"""
    if not smiles or smiles == "N/A" or len(smiles) < 3:
        return None
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{smiles}/PNG?image_size={size}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.content
    except:
        pass
    return None

def get_yield_class(yield_str):
    """Get yield color class"""
    try:
        y = int(yield_str.replace('%','').split('-')[0])
        if y >= 80:
            return "yield-high"
        elif y >= 60:
            return "yield-med"
        else:
            return "yield-low"
    except:
        return ""

# Sidebar
with st.sidebar:
    st.markdown("### 🔍 Search Drug")
    search_term = st.text_input("Enter drug name:", placeholder="e.g., Aspirin")
    
    st.markdown("---")
    st.markdown("### 📊 Database Stats")
    
    total = len(DRUG_DB)
    with_commercial = sum(1 for d in DRUG_DB.values() if 'synthesis_routes' in d and 'commercial' in d['synthesis_routes'])
    with_ai = sum(1 for d in DRUG_DB.values() if 'synthesis_routes' in d and 'ai_predicted_novel' in d['synthesis_routes'])
    
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-num">{total}</div>
        <div>Total Drugs</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div style='text-align:center'><span style='color:#27ae60;font-weight:bold'>{with_commercial}</span><br><small>Commercial</small></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='text-align:center'><span style='color:#e67e22;font-weight:bold'>{with_ai}</span><br><small>AI Routes</small></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📋 Categories")
    categories = list(set(d.get('category', 'Unknown') for d in DRUG_DB.values()))
    for cat in sorted(categories)[:8]:
        count = sum(1 for d in DRUG_DB.values() if d.get('category') == cat)
        st.markdown(f"- {cat} ({count})")
    
    st.markdown("---")
    st.markdown("""
    ### 🧬 What You Get
    
    **For each drug:**
    - ✅ Commercial/industrial route
    - ✅ AI-predicted novel route  
    - ✅ ALL intermediates with SMILES
    - ✅ Yields for each step
    - ✅ Conditions
    - ✅ References
    - ✅ KSM cost analysis
    """)

# Main content
if search_term:
    # Search for drug
    results = [name for name in DRUG_DB.keys() if search_term.lower() in name.lower()]
    
    if results:
        st.success(f"Found {len(results)} results!")
        
        for drug_name in results:
            drug = DRUG_DB[drug_name]
            synth = drug.get('synthesis_routes', {})
            
            # Drug header
            st.markdown(f"""
            <div class="drug-card">
                <h2>💊 {drug_name}</h2>
                <p>
                    <span class="status-badge">{drug.get('status', 'N/A')}</span>
                    <span class="category-badge">{drug.get('category', 'N/A')}</span>
                    <span style="color:#888;">CAS: {drug.get('cas', 'N/A')}</span>
                </p>
                <p><strong>Formula:</strong> {drug.get('formula', 'N/A')} | <strong>MW:</strong> {drug.get('mw', 'N/A')}</p>
                <p><strong>Mechanism:</strong> {drug.get('mechanism', 'N/A')}</p>
                <p><strong>Therapeutic:</strong> {drug.get('therapeutic', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show structure
            smiles = drug.get('smiles', '')
            if smiles and smiles != "N[A]" and len(smiles) > 3:
                img = get_pubchem_image(smiles, 400)
                if img:
                    st.image(img, caption=f"2D Structure of {drug_name}", width=300)
            
            st.markdown("---")
            
            # COMMERCIAL SYNTHESIS
            if 'commercial' in synth:
                comm = synth['commercial']
                st.markdown("### 🏭 Commercial/Industrial Synthesis")
                st.markdown(f"**{comm.get('name', 'Industrial Route')}**")
                
                if 'ksm_cost' in comm:
                    st.markdown(f"💰 **KSM Cost:** {comm['ksm_cost']}")
                
                if 'total_yield' in comm:
                    yield_class = get_yield_class(str(comm['total_yield']))
                    st.markdown(f"📊 **Total Yield:** <span class='{yield_class}'>{comm['total_yield']}</span>", unsafe_allow_html=True)
                
                st.markdown("#### 📝 Complete Synthesis Steps:")
                
                steps = comm.get('steps', [])
                for step in steps:
                    with st.container():
                        st.markdown(f"""
                        <div class="step-box">
                            <h4>Step {step.get('step', '?')}: {step.get('name', 'Reaction')}</h4>
                            <p><strong>Reaction:</strong> {step.get('reaction', step.get('name', 'N/A'))}</p>
                            <p><strong>Conditions:</strong> {step.get('conditions', 'N/A')}</p>
                            <p><strong>Reagents:</strong> {', '.join(step.get('reagents', []))}</p>
                            <p><strong>Yield:</strong> <span class='{get_yield_class(str(step.get('yield', '0%')))}'>{step.get('yield', 'N/A')}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show SMILES if available
                        step_smiles = step.get('smiles', '')
                        if step_smiles and step_smiles != 'N/A' and len(step_smiles) > 3:
                            mol_img = get_pubchem_image(step_smiles, 200)
                            if mol_img:
                                col1, col2 = st.columns([1, 3])
                                with col1:
                                    st.image(mol_img, width=150)
                
                # References
                if 'refs' in comm:
                    st.markdown("**References:**")
                    for ref in comm['refs']:
                        st.markdown(f"- <span class='ref-badge'>USPTO/Lit</span> {ref}")
            
            st.markdown("---")
            
            # AI NOVEL SYNTHESIS
            if 'ai_predicted_novel' in synth:
                ai = synth['ai_predicted_novel']
                st.markdown("### 🤖 AI-Predicted Novel Synthesis")
                st.markdown(f"**{ai.get('name', 'AI Route')}**")
                
                conf = ai.get('confidence_score', ai.get('confidence', 0))
                st.markdown(f"<span class='confidence-badge'>AI Confidence: {conf}%</span>", unsafe_allow_html=True)
                
                if 'total_yield' in ai and ai['total_yield'] != 'N/A':
                    st.markdown(f"📊 **Total Yield:** <span class='{get_yield_class(str(ai['total_yield']))}'>{ai['total_yield']}</span>", unsafe_allow_html=True)
                
                if 'advantages' in ai:
                    st.markdown(f"✨ **Advantages:** {ai['advantages']}")
                
                st.markdown("#### 📝 AI-Generated Steps:")
                
                ai_steps = ai.get('steps', [])
                for step in ai_steps:
                    with st.container():
                        st.markdown(f"""
                        <div class="ai-box">
                            <h4>Step {step.get('step', '?')}: {step.get('name', 'Reaction')}</h4>
                            <p><strong>Conditions:</strong> {step.get('conditions', 'N/A')}</p>
                            <p><strong>Reagents:</strong> {', '.join(step.get('reagents', []))}</p>
                            <p><strong>Yield:</strong> <span class='{get_yield_class(str(step.get('yield', '0%')))}'>{step.get('yield', 'N/A')}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        step_smiles = step.get('smiles', '')
                        if step_smiles and step_smiles != 'N/A' and len(step_smiles) > 3:
                            mol_img = get_pubchem_image(step_smiles, 200)
                            if mol_img:
                                st.image(mol_img, width=150)
                
                if 'confidence_score' in ai:
                    st.markdown(f"<span class='confidence-badge'>AI Confidence Score: {ai['confidence_score']}%</span>", unsafe_allow_html=True)
            
            st.markdown("---")
    
    elif search_term:
        st.error(f"Drug '{search_term}' not found. Try another name.")

else:
    # Show all drugs
    st.markdown("### 💊 Available Drugs with Complete Retrosynthesis")
    
    cols = st.columns(4)
    for i, (name, drug) in enumerate(sorted(DRUG_DB.items())):
        with cols[i % 4]:
            with st.container():
                synth = drug.get('synthesis_routes', {})
                has_commercial = 'commercial' in synth
                has_ai = 'ai_predicted_novel' in synth
                
                badges = ""
                if has_commercial:
                    badges += " 🏭"
                if has_ai:
                    badges += " 🤖"
                
                st.markdown(f"""
                <div class="drug-card" style="padding:1rem; cursor:pointer;">
                    <h4>💊 {name}{badges}</h4>
                    <p><small>{drug.get('category', 'N/A')}</small></p>
                    <p><span class="status-badge">{drug.get('status', 'N/A')}</span></p>
                    <p><small>MW: {drug.get('mw', 'N/A')}</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"View Full ROS →", key=f"btn_{name}"):
                    st.session_state.search_drug = name
                    st.rerun()
    
    st.markdown("---")
    st.markdown("""
    ### 🧬 How to Use
    
    1. **Search** for a drug name in the sidebar
    2. **View** complete commercial synthesis route (all steps)
    3. **Compare** with AI-predicted novel route
    4. **See** yields, conditions, SMILES, and references for EACH step
    
    ### 📊 Database Coverage
    
    - **46 Major drugs** with complete retrosynthesis
    - All intermediates shown with structures
    - Commercial vs AI-predicted routes
    - KSM cost analysis
    - Literature references
    """)

# Footer
st.markdown("""
<div style="text-align:center; color:#666; padding:1rem;">
    <p>Complete Retrosynthesis Database - For GM sir</p>
    <p style="font-size:0.8rem;">Data: Commercial routes from USPTO/Literature | AI routes predicted</p>
</div>
""", unsafe_allow_html=True)
