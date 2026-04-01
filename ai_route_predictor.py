"""
AI Route Predictor Module
Predicts synthesis routes using IBM RXN API or local ASKCos
For GM sir - On-demand AI-based route prediction
"""
import requests
import json
import time

# IBM RXN API Configuration
IBM_RXN_KEY = ""  # Add your IBM RXN API key here
IBM_RXN_URL = "https://rxn.resonance.ai/rxn"

def predict_routes_ibm(smiles):
    """
    Use IBM RXN API to predict synthesis routes
    Returns: List of predicted routes with confidence scores
    """
    if not IBM_RXN_KEY:
        return None, "IBM RXN API key not configured"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {IBM_RXN_KEY}"
    }
    
    data = {
        "preferences": {
            "retrosynthesis": True,
            "selectivity": "ALL",
            "steps": 5
        },
        "smiles": smiles
    }
    
    try:
        # Start retrosynthesis prediction
        response = requests.post(
            f"{IBM_RXN_URL}/api/v1/retrosynthesis",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            
            # Poll for results
            for _ in range(30):  # 30 attempts
                time.sleep(2)
                status_response = requests.get(
                    f"{IBM_RXN_URL}/api/v1/retrosynthesis/{task_id}",
                    headers=headers
                )
                
                if status_response.status_code == 200:
                    status = status_response.json()
                    if status.get("status") == "SUCCESS":
                        return status.get("routes", []), None
                    elif status.get("status") == "FAILED":
                        return None, "Prediction failed"
                
            return None, "Timeout waiting for results"
        else:
            return None, f"API error: {response.status_code}"
            
    except Exception as e:
        return None, str(e)

def predict_routes_local(smiles):
    """
    Use local RDKit-based rules for simple predictions
    Fallback when IBM RXN is not available
    """
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors
    
    results = []
    
    # Basic transformations
    transformations = [
        {"name": "Ester hydrolysis", "smarts": "C(=O)OC>>C(=O)O", "conditions": "NaOH, H2O"},
        {"name": "Amide formation", "smarts": "C(=O)O>>C(=O)N", "conditions": "EDCI, HOBt"},
        {"name": "Oxidation (alcohol to acid)", "smarts": "CO>>CO", "conditions": "PCC, DCM"},
        {"name": "Reduction (ester to alcohol)", "smarts": "C(=O)OC>>C(O)CO", "conditions": "LiAlH4, THF"},
        {"name": "Nucleophilic substitution", "smarts": "C-Cl>>C-N", "conditions": "K2CO3, DMF"},
    ]
    
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return [], "Invalid SMILES"
    
    for trans in transformations:
        try:
            rxn = AllChem.ReactionFromSmarts(trans["smarts"])
            if rxn:
                products = rxn.RunReactants((mol,))
                if products:
                    for prod_set in products:
                        for prod in prod_set:
                            prod_smiles = Chem.MolToSmiles(prod)
                            if prod_smiles and prod_smiles != smiles:
                                results.append({
                                    "step": 1,
                                    "name": trans["name"],
                                    "conditions": trans["conditions"],
                                    "educts": [{"smiles": smiles, "name": "Starting material"}],
                                    "product_smiles": prod_smiles,
                                    "yield": "Variable",
                                    "confidence": 60
                                })
        except:
            continue
    
    return results[:5], None  # Return top 5

def get_ai_prediction(smiles, drug_name):
    """
    Main function to get AI-predicted route
    Tries IBM RXN first, falls back to local
    """
    # Try IBM RXN first
    routes, error = predict_routes_ibm(smiles)
    
    if error and "not configured" in error:
        # Fall back to local predictions
        routes, error = predict_routes_local(smiles)
        if routes:
            return {
                "name": f"AI-Local Prediction for {drug_name}",
                "confidence": 65,
                "steps": routes,
                "total_yield": "Variable",
                "method": "Local RDKit-based rules",
                "advantages": "Available offline, instant prediction"
            }
    
    if routes:
        return {
            "name": f"IBM RXN AI Prediction for {drug_name}",
            "confidence": 85,
            "steps": routes,
            "total_yield": "Variable",
            "method": "IBM RXN AI retrosynthesis",
            "advantages": "State-of-the-art AI prediction"
        }
    
    return {
        "name": f"Novel Route Suggestion for {drug_name}",
        "confidence": 50,
        "steps": [{
            "step": 1,
            "name": "Literature search recommended",
            "conditions": "Manual analysis required",
            "educts": [{"smiles": smiles, "name": drug_name}],
            "yield": "N/A",
            "suggestion": "Search ChEMBL, DrugBank, or USPTO for reported syntheses"
        }],
        "total_yield": "N/A",
        "method": "No prediction available",
        "advantages": "Manual route planning suggested"
    }

def format_route_for_db(route, drug_name):
    """Format AI prediction for database storage"""
    return {
        "name": route.get("name", f"AI Route for {drug_name}"),
        "confidence": route.get("confidence", 75),
        "steps": [
            {
                "step": s.get("step", i+1),
                "name": s.get("name", "Reaction"),
                "conditions": s.get("conditions", "Standard conditions"),
                "reagents": s.get("educts", []),
                "yield": s.get("yield", "Variable"),
                "smiles": s.get("product_smiles", "")
            }
            for i, s in enumerate(route.get("steps", []))
        ],
        "total_yield": route.get("total_yield", "Variable"),
        "advantages": route.get("advantages", ""),
        "confidence_score": route.get("confidence", 75)
    }

# Demo function
def demo_prediction():
    """Demo with simple molecule"""
    test_smiles = "CC(=O)Oc1ccccc1C(=O)O"  # Aspirin
    result = get_ai_prediction(test_smiles, "Aspirin (demo)")
    return result

if __name__ == "__main__":
    print("AI Route Predictor - Demo")
    result = demo_prediction()
    print(json.dumps(result, indent=2))
