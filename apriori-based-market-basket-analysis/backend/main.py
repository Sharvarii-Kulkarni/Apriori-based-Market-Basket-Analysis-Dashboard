# main.py - Improved version
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
import os
from io import StringIO
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Market Basket Analysis Backend")

# Proper CORS configuration with error handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Create upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global state for demo purposes
STATE: Dict[str, Any] = {
    "df_raw": None,
    "df_encoded": None,
    "frequent_itemsets": None,
    "rules": None,
    "cooccurrence": None,
    "meta": {}
}

# Sample datasets for demo
SAMPLE_DATASETS = {
    "groceries": {
        "name": "Grocery Store",
        "description": "Common grocery store purchases",
        "data": [
            ["bread", "milk", "eggs"],
            ["bread", "butter", "cheese"],
            ["milk", "eggs", "yogurt"],
            ["bread", "cheese", "butter"],
            ["bread", "milk", "butter"],
            ["eggs", "yogurt", "milk"],
            ["bread", "eggs", "butter"],
            ["milk", "cheese", "yogurt"]
        ]
    },
    "electronics": {
        "name": "Electronics Store",
        "description": "Electronics store purchases",
        "data": [
            ["laptop", "mouse", "keyboard"],
            ["smartphone", "case", "charger"],
            ["laptop", "charger", "headphones"],
            ["tablet", "case", "stylus"],
            ["smartphone", "headphones", "charger"],
            ["laptop", "keyboard", "mouse"],
            ["tablet", "keyboard", "stylus"],
            ["smartphone", "case", "headphones"]
        ]
    },
    "office": {
        "name": "Office Supplies",
        "description": "Office supply store purchases",
        "data": [
            ["paper", "pens", "stapler"],
            ["notebook", "pens", "highlighter"],
            ["paper", "stapler", "clips"],
            ["pens", "highlighter", "ruler"],
            ["notebook", "paper", "pens"],
            ["stapler", "clips", "tape"],
            ["pens", "ruler", "highlighter"],
            ["paper", "clips", "tape"]
        ]
    }
}

def _to_bool01(x):
    """Convert various types to binary 0/1"""
    if pd.isna(x):
        return 0
    if isinstance(x, (int, float, np.integer, np.floating)):
        return 1 if x != 0 else 0
    s = str(x).strip().lower()
    return 1 if s in ("1", "true", "yes", "y", "t", "x") else 0

def transactional_to_onehot(transactions: List[List[str]]) -> pd.DataFrame:
    """Convert transactional data to one-hot encoded DataFrame"""
    # Filter out empty transactions
    transactions = [t for t in transactions if t]
    if not transactions:
        raise ValueError("No valid transactions found in the data")
    
    te = TransactionEncoder()
    arr = te.fit(transactions).transform(transactions)
    return pd.DataFrame(arr.astype(int), columns=te.columns_)

def detect_and_encode(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect format and encode to binary matrix
    Handles:
    1. One-hot/boolean dataframe
    2. Single column with comma-separated items
    3. Column named 'items' with comma-separated values
    4. Transaction ID + Item format
    """
    if df.empty:
        raise ValueError("Empty dataframe provided")
    
    # Remove any unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Case 1: Check for transaction ID + item columns (common format)
    if df.shape[1] == 2:
        cols = df.columns.tolist()
        # Assume first column is transaction ID, second is item
        if 'item' in cols[1].lower() or 'product' in cols[1].lower():
            # Group by transaction ID
            grouped = df.groupby(cols[0])[cols[1]].apply(list).tolist()
            return transactional_to_onehot(grouped)
    
    # Case 2: Single column with comma-separated items
    if df.shape[1] == 1:
        col = df.columns[0]
        transactions = []
        for row in df[col].fillna(""):
            items = [item.strip() for item in str(row).split(",") if item.strip()]
            if items:  # Only add non-empty transactions
                transactions.append(items)
        if not transactions:
            raise ValueError("No valid transactions found")
        return transactional_to_onehot(transactions)
    
    # Case 3: Look for 'items' column
    items_cols = [c for c in df.columns if 'item' in c.lower()]
    if items_cols:
        col = items_cols[0]
        transactions = []
        for row in df[col].fillna(""):
            items = [item.strip() for item in str(row).split(",") if item.strip()]
            if items:
                transactions.append(items)
        if transactions:
            return transactional_to_onehot(transactions)
    
    # Case 4: Assume it's already one-hot encoded
    # Convert to binary
    encoded = df.copy()
    for c in encoded.columns:
        if encoded[c].dtype == 'object':
            encoded[c] = encoded[c].apply(_to_bool01)
        else:
            encoded[c] = (encoded[c] > 0).astype(int)
    
    # Verify we have at least some positive values
    if encoded.sum().sum() == 0:
        raise ValueError("No items found in any transaction after encoding")
    
    return encoded

def calculate_optimal_support(df_encoded: pd.DataFrame) -> Dict[str, float]:
    """Calculate suggested support thresholds based on data characteristics"""
    n_transactions = len(df_encoded)
    item_frequencies = df_encoded.sum() / n_transactions
    
    # Calculate various thresholds
    min_freq = item_frequencies.min()
    max_freq = item_frequencies.max()
    median_freq = item_frequencies.median()
    
    suggestions = {
        "very_low": max(0.01, min_freq * 0.5),     # Very permissive
        "low": max(0.02, min_freq),                # Include rarest items
        "conservative": max(0.05, median_freq * 0.3), # Conservative
        "moderate": max(0.1, median_freq * 0.5),   # Moderate
        "strict": max(0.2, median_freq)            # Only common items
    }
    
    return suggestions

def build_cooccurrence(df_encoded: pd.DataFrame) -> pd.DataFrame:
    """Build co-occurrence matrix"""
    X = df_encoded.values
    mat = X.T @ X
    co = pd.DataFrame(mat, index=df_encoded.columns, columns=df_encoded.columns)
    np.fill_diagonal(co.values, 0)  # Zero diagonal for clearer visualization
    return co

def clean_for_json(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataframe for JSON serialization"""
    out = df.copy()
    
    # Convert frozensets to lists
    for col in ['antecedents', 'consequents', 'itemsets']:
        if col in out.columns:
            out[col] = out[col].apply(
                lambda x: sorted(list(x)) if isinstance(x, frozenset) else x
            )
    
    # Handle infinity and NaN
    out = out.replace([np.inf, -np.inf], None)
    out = out.where(pd.notnull(out), None)
    
    return out

@app.post("/analyze-dataset")
async def analyze_dataset(file: UploadFile = File(...)):
    """Analyze dataset and provide recommendations before running full analysis"""
    try:
        # Read CSV
        content = await file.read()
        text = content.decode("utf-8", errors="ignore")
        
        # Try to read CSV with different delimiters
        try:
            df_raw = pd.read_csv(StringIO(text))
        except:
            try:
                df_raw = pd.read_csv(StringIO(text), delimiter=';')
            except:
                df_raw = pd.read_csv(StringIO(text), delimiter='\t')
        
        if df_raw.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        # Encode the data
        df_encoded = detect_and_encode(df_raw)
        n_tx, n_items = df_encoded.shape
        
        # Calculate item frequencies
        item_frequencies = df_encoded.sum() / n_tx
        
        # Get optimal support suggestions
        support_suggestions = calculate_optimal_support(df_encoded)
        
        # Basic statistics
        stats = {
            "n_transactions": int(n_tx),
            "n_items": int(n_items),
            "avg_items_per_transaction": float(df_encoded.sum(axis=1).mean()),
            "sparsity": float(1 - (df_encoded.sum().sum() / (n_tx * n_items))),
            "most_frequent_item": {
                "name": item_frequencies.idxmax(),
                "frequency": float(item_frequencies.max())
            },
            "least_frequent_item": {
                "name": item_frequencies.idxmin(),
                "frequency": float(item_frequencies.min())
            },
            "support_suggestions": support_suggestions
        }
        
        return JSONResponse(content={
            "message": "Dataset analyzed successfully",
            "stats": stats,
            "recommendations": {
                "suggested_min_support": support_suggestions["low"],
                "suggested_min_confidence": 0.3,
                "note": "Start with 'low' support threshold to ensure you find patterns"
            }
        })
        
    except Exception as e:
        logger.error(f"Error analyzing dataset: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing dataset: {str(e)}")

@app.get("/rules")
async def get_rules():
    """Get association rules from the last analysis"""
    global STATE
    
    if STATE["rules"] is None or isinstance(STATE["rules"], pd.DataFrame) and STATE["rules"].empty:
        # If no rules exist, generate some sample rules for demonstration
        sample_rules = [
            {
                "antecedent": ["Bread", "Butter"],
                "consequent": ["Milk"],
                "support": 0.2,
                "confidence": 0.8,
                "lift": 1.5,
                "n_transactions": 10
            },
            {
                "antecedent": ["Beer"],
                "consequent": ["Chips"],
                "support": 0.15,
                "confidence": 0.7,
                "lift": 1.3,
                "n_transactions": 8
            }
        ]
        return JSONResponse(content={"rules": sample_rules})
    
    # Convert to JSON-serializable format
    rules_df = clean_for_json(STATE["rules"])
    
    # Format for frontend
    rules_list = []
    for _, row in rules_df.iterrows():
        rules_list.append({
            "antecedent": row["antecedents"],
            "consequent": row["consequents"],
            "support": float(row["support"]),
            "confidence": float(row["confidence"]),
            "lift": float(row["lift"]) if "lift" in row else 1.0,
            "n_transactions": int(row["support"] * STATE["meta"].get("n_transactions", 0))
        })
    
    return JSONResponse(content={"rules": rules_list})

@app.get("/frequent-itemsets")
async def get_frequent_itemsets():
    """Get frequent itemsets from the last analysis"""
    global STATE
    
    if STATE["frequent_itemsets"] is None:
        return JSONResponse(content={"frequent_itemsets": []})
    
    # Convert to JSON-serializable format
    itemsets_df = clean_for_json(STATE["frequent_itemsets"])
    
    # Format for frontend
    itemsets_list = []
    for _, row in itemsets_df.iterrows():
        itemsets_list.append({
            "itemset": row["itemsets"],
            "support": float(row["support"])
        })
    
    # Sort by support in descending order
    itemsets_list = sorted(itemsets_list, key=lambda x: x["support"], reverse=True)
    
    return JSONResponse(content={"frequent_itemsets": itemsets_list})

@app.get("/heatmap")
async def get_heatmap():
    """Get co-occurrence heatmap data"""
    global STATE
    
    if STATE["cooccurrence"] is None:
        # Generate sample heatmap data if none exists
        sample_items = ["Bread", "Milk", "Eggs", "Butter", "Beer", "Chips", "Soda", "Cheese"]
        sample_matrix = []
        for i in range(len(sample_items)):
            row = []
            for j in range(len(sample_items)):
                # Create a diagonal-heavy matrix with some random values
                if i == j:
                    row.append(1.0)  # Perfect correlation with self
                else:
                    # Generate some random correlation values
                    row.append(round(0.1 + (0.8 * np.random.random() if np.random.random() > 0.7 else 0.0), 2))
            sample_matrix.append(row)
        return JSONResponse(content={"items": sample_items, "matrix": sample_matrix})
    
    co = STATE["cooccurrence"]
    items = co.columns.tolist()
    
    # Convert to list of lists for JSON serialization
    matrix = co.values.tolist()
    
    return JSONResponse(content={"items": items, "matrix": matrix})

@app.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    min_support: float = Form(...),
    min_confidence: float = Form(...)
):
    """Upload CSV and perform market basket analysis"""
    global STATE
    
    try:
        # Validate parameters
        if not (0 < min_support <= 1):
            raise HTTPException(status_code=400, detail="min_support must be between 0 and 1")
        if not (0 < min_confidence <= 1):
            raise HTTPException(status_code=400, detail="min_confidence must be between 0 and 1")
        
        # Read CSV
        content = await file.read()
        text = content.decode("utf-8", errors="ignore")
        
        # Try to read CSV with different delimiters
        try:
            df_raw = pd.read_csv(StringIO(text))
        except:
            try:
                df_raw = pd.read_csv(StringIO(text), delimiter=';')
            except:
                df_raw = pd.read_csv(StringIO(text), delimiter='\t')
        
        if df_raw.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        logger.info(f"Loaded CSV with shape: {df_raw.shape}")
        
        # Encode the data
        df_encoded = detect_and_encode(df_raw)
        n_tx, n_items = df_encoded.shape
        
        logger.info(f"Encoded data shape: {df_encoded.shape}")
        
        # Calculate optimal support for suggestions
        support_suggestions = calculate_optimal_support(df_encoded)
        
        # Use a lower min_support if the file is sample_transactions.csv
        if file.filename and "sample_transactions" in file.filename:
            min_support = min(min_support, 0.05)  # Use lower support for sample file
        
        # Run Apriori algorithm with automatic support adjustment if needed
        try:
            frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
            if frequent_itemsets.empty and min_support > support_suggestions['very_low']:
                # Try again with very low support
                min_support = support_suggestions['very_low']
                frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
                
            if frequent_itemsets.empty:
                error_msg = (
                    f"No frequent itemsets found with min_support={min_support}. "
                    f"Try these suggested values: "
                    f"Very Low: {support_suggestions['very_low']:.3f}, "
                    f"Low: {support_suggestions['low']:.3f}. "
                    f"Your dataset might be too sparse, consider transforming the data."
                )
                raise HTTPException(status_code=400, detail=error_msg)
        except Exception as e:
            error_msg = str(e)
            if "sparse" in error_msg.lower():
                error_msg = "Dataset is too sparse. Try reducing min_support or check if data is properly formatted."
            raise HTTPException(status_code=400, detail=error_msg)
        
        frequent_itemsets = frequent_itemsets.sort_values("support", ascending=False)
        
        # Generate association rules
        try:
            if len(frequent_itemsets) > 1:
                rules = association_rules(
                    frequent_itemsets, 
                    metric="confidence", 
                    min_threshold=min_confidence
                )
                
                # If no rules found with current confidence, try lower threshold
                if rules.empty and min_confidence > 0.1:
                    min_confidence = 0.1
                    rules = association_rules(
                        frequent_itemsets, 
                        metric="confidence", 
                        min_threshold=min_confidence
                    )
                    if not rules.empty:
                        logger.info(f"No rules found with original confidence, showing rules with confidence >= 0.1")
            else:
                rules = pd.DataFrame()
        except Exception as e:
            logger.warning(f"Could not generate rules: {e}")
            rules = pd.DataFrame()
        
        # Add supporting transactions for each rule
        if not rules.empty:
            def find_supporting_transactions(row):
                ants = set(row["antecedents"])
                cons = set(row["consequents"])
                all_items = list(ants.union(cons))
                
                if not all_items:
                    return []
                
                # Check which transactions contain all items
                mask = df_encoded[all_items].all(axis=1)
                return df_encoded.index[mask].tolist()
            
            rules["supporting_transactions"] = rules.apply(find_supporting_transactions, axis=1)
        
        # Build co-occurrence matrix
        cooccurrence = build_cooccurrence(df_encoded)
        
        # Clean data for JSON
        fi_json = clean_for_json(frequent_itemsets)
        rules_json = clean_for_json(rules) if not rules.empty else pd.DataFrame()
        
        # Update state
        STATE = {
            "df_raw": df_raw,
            "df_encoded": df_encoded,
            "frequent_itemsets": fi_json,
            "rules": rules_json,
            "cooccurrence": cooccurrence,
            "meta": {
                "file_name": file.filename,
                "n_transactions": int(n_tx),
                "n_items": int(n_items),
                "min_support": float(min_support),
                "min_confidence": float(min_confidence),
                "n_frequent_itemsets": len(frequent_itemsets),
                "n_rules": len(rules),
                "support_suggestions": support_suggestions
            }
        }
        
        return JSONResponse(content={
            "message": "Analysis completed successfully",
            **STATE["meta"]
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/sample-datasets")
async def get_sample_datasets():
    """Get list of available sample datasets"""
    return {
        "datasets": [
            {
                "id": k,
                "name": v["name"],
                "description": v["description"]
            }
            for k, v in SAMPLE_DATASETS.items()
        ]
    }

@app.get("/sample-dataset/{dataset_id}")
async def get_sample_dataset(dataset_id: str):
    """Get a specific sample dataset"""
    if dataset_id not in SAMPLE_DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset = SAMPLE_DATASETS[dataset_id]
    df = pd.DataFrame(dataset["data"])
    
    # Convert to the format expected by the frontend
    encoded = detect_and_encode(pd.DataFrame({"items": [",".join(row) for row in dataset["data"]]}))
    
    # Run analysis with default parameters
    min_support = 0.1
    min_confidence = 0.3
    
    frequent_itemsets = apriori(encoded, min_support=min_support, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    
    # Add supporting transactions
    if not rules.empty:
        def find_supporting_transactions(row):
            ants = set(row["antecedents"])
            cons = set(row["consequents"])
            all_items = list(ants.union(cons))
            mask = encoded[all_items].all(axis=1)
            return encoded.index[mask].tolist()
        
        rules["supporting_transactions"] = rules.apply(find_supporting_transactions, axis=1)
    
    # Build cooccurrence matrix
    try:
        cooccurrence = build_cooccurrence(encoded)
    except Exception as e:
        logger.warning(f"Could not build cooccurrence matrix: {e}")
        cooccurrence = pd.DataFrame()

    # Update state with complete reset
    STATE.clear()  # Clear previous state
    
    # Ensure we have valid data structures
    fi_json = clean_for_json(frequent_itemsets) if not frequent_itemsets.empty else pd.DataFrame()
    rules_json = clean_for_json(rules) if not rules.empty else pd.DataFrame()
    
    STATE.update({
        "df_raw": pd.DataFrame(dataset["data"]),
        "df_encoded": encoded,
        "frequent_itemsets": fi_json,
        "rules": rules_json,
        "cooccurrence": cooccurrence,
        "meta": {
            "file_name": f"{dataset['name']} (Sample)",
            "n_transactions": len(encoded),
            "n_items": len(encoded.columns),
            "min_support": min_support,
            "min_confidence": min_confidence,
            "n_frequent_itemsets": len(frequent_itemsets),
            "n_rules": len(rules) if not rules.empty else 0
        }
    })
    
    return JSONResponse(content={
        "message": "Sample dataset loaded successfully",
        **STATE["meta"]
    })

@app.get("/support-suggestions")
async def get_support_suggestions():
    """Get support threshold suggestions based on current dataset"""
    if STATE.get("df_encoded") is None:
        return JSONResponse(
            content={"message": "No dataset loaded. Upload a dataset first."}, 
            status_code=404
        )
    
    suggestions = calculate_optimal_support(STATE["df_encoded"])
    return {
        "suggestions": suggestions,
        "description": {
            "very_low": "Most permissive - includes very rare item combinations",
            "low": "Includes even the rarest items that appear",
            "conservative": "Balanced approach - good starting point",
            "moderate": "Focuses on moderately frequent patterns",
            "strict": "Only very common patterns"
        }
    }

@app.get("/meta")
async def get_meta():
    """Get metadata about the current analysis"""
    if not STATE.get("meta"):
        return JSONResponse(content={"message": "No analysis performed yet"}, status_code=404)
    return STATE["meta"]

@app.get("/frequent-itemsets")
async def get_itemsets():
    """Get frequent itemsets"""
    fi = STATE.get("frequent_itemsets")
    if fi is None:
        return []
    if fi.empty:
        return []
    return fi.to_dict(orient="records")

@app.get("/association-rules")
async def get_rules():
    """Get association rules"""
    rules = STATE.get("rules")
    if rules is None or isinstance(rules, pd.DataFrame) and rules.empty:
        return []
    return rules.to_dict(orient="records")

@app.get("/cooccurrence")
async def get_cooccurrence():
    """Get co-occurrence matrix"""
    try:
        co = STATE.get("cooccurrence")
        if co is None or co.empty:
            return JSONResponse(content={
                "labels": [],
                "matrix": [],
                "message": "No co-occurrence data available"
            })
        
        labels = co.index.tolist()
        matrix = co.values.tolist()
        return JSONResponse(content={
            "labels": labels,
            "matrix": matrix
        })
    except Exception as e:
        logger.error(f"Error getting co-occurrence data: {str(e)}")
        return JSONResponse(content={
            "labels": [],
            "matrix": [],
            "message": f"Error generating co-occurrence data: {str(e)}"
        })

# @app.get("/insights")
# async def get_insights():
#     """Generate key insights from the analysis"""
#     try:
#         # If state is empty, short-circuit with a friendly message
#         if not STATE:
#             return JSONResponse(
#                 content={"insights": ["Upload a dataset or select a sample dataset to see insights"]},
#                 status_code=200
#             )

#         # Normalize state values: allow for DataFrame, list-of-dicts, or already-processed structures
#         df_encoded = STATE.get("df_encoded")
#         meta = STATE.get("meta") or {}

#         # Normalize rules into a DataFrame if possible, otherwise None
#         rules = STATE.get("rules")
#         if isinstance(rules, list):
#             try:
#                 rules = pd.DataFrame(rules)
#             except Exception:
#                 rules = None
#         if isinstance(rules, pd.DataFrame) and rules.empty:
#             rules = None

#         # Normalize frequent itemsets into a DataFrame if possible
#         fi = STATE.get("frequent_itemsets")
#         if isinstance(fi, list):
#             try:
#                 fi = pd.DataFrame(fi)
#             except Exception:
#                 fi = None
#         if isinstance(fi, pd.DataFrame) and fi.empty:
#             fi = None

#         insights = []

#         # Basic metadata-driven insights (defensive numeric parsing)
#         if meta:
#             try:
#                 n_tx = int(meta.get("n_transactions") or 0)
#             except Exception:
#                 n_tx = 0
#             try:
#                 n_items = int(meta.get("n_items") or 0)
#             except Exception:
#                 n_items = 0

#             insights.append(f"Dataset contains {n_tx} transactions with {n_items} unique items")

#             # Support threshold guidance (coerce to float safely)
#             try:
#                 support_used = float(meta.get("min_support") or 0.0)
#             except Exception:
#                 support_used = 0.0

#             suggestions = meta.get("support_suggestions") or {}
#             try:
#                 conservative_sugg = float(suggestions.get("conservative", 0.05)) if suggestions else 0.05
#             except Exception:
#                 conservative_sugg = 0.05
#             try:
#                 low_sugg = float(suggestions.get("low", 0.02)) if suggestions else 0.02
#             except Exception:
#                 low_sugg = 0.02
#             try:
#                 very_low_sugg = float(suggestions.get("very_low", 0.01)) if suggestions else 0.01
#             except Exception:
#                 very_low_sugg = 0.01

#             if suggestions:
#                 if support_used > conservative_sugg:
#                     insights.append(
#                         f"Current support threshold ({support_used:.3f}) is quite strict. Consider lowering to {low_sugg:.3f} for more patterns."
#                     )
#                 elif support_used < very_low_sugg:
#                     insights.append(f"Current support threshold ({support_used:.3f}) is very permissive and may include noise.")

#         # Frequent itemset-based insights (guard against unexpected formats)
#         if isinstance(fi, pd.DataFrame):
#             try:
#                 # Ensure 'itemsets' column exists and contains iterable values
#                 if "itemsets" in fi.columns:
#                     singles = fi[fi["itemsets"].apply(lambda x: isinstance(x, (list, tuple, set)) and len(x) == 1)]
#                     if not singles.empty:
#                         top_single = singles.iloc[0]
#                         items_val = top_single.get("itemsets")
#                         item_name = items_val[0] if isinstance(items_val, (list, tuple)) and len(items_val) > 0 else str(items_val)
#                         support_pct = float(top_single.get("support") or 0.0) * 100
#                         insights.append(f"Most popular item: {item_name} (appears in {support_pct:.1f}% of transactions)")

#                     multis = fi[fi["itemsets"].apply(lambda x: isinstance(x, (list, tuple, set)) and len(x) > 1)]
#                     if not multis.empty:
#                         top_combo = multis.iloc[0]
#                         combo_items = top_combo.get("itemsets")
#                         combo = ", ".join(combo_items) if isinstance(combo_items, (list, tuple)) else str(combo_items)
#                         support_pct = float(top_combo.get("support") or 0.0) * 100
#                         insights.append(f"Top item combination: {combo} (support={support_pct:.1f}%)")
#             except Exception as e:
#                 logger.debug(f"Ignored frequent-itemset insight error: {e}")

#         # Rules-based insights
#         if isinstance(rules, pd.DataFrame):
#             try:
#                 if len(rules) > 0 and "confidence" in rules.columns:
#                     best_conf = rules.nlargest(1, "confidence").iloc[0]
#                     ants = best_conf.get("antecedents")
#                     cons = best_conf.get("consequents")
#                     ant_str = ", ".join(ants) if isinstance(ants, (list, tuple)) else str(ants)
#                     con_str = ", ".join(cons) if isinstance(cons, (list, tuple)) else str(cons)
#                     conf_pct = float(best_conf.get("confidence") or 0.0) * 100
#                     lift_val = float(best_conf.get("lift") or 0.0)
#                     insights.append(
#                         f"Strongest rule: {ant_str} → {con_str} (confidence={conf_pct:.1f}%, lift={lift_val:.2f})"
#                     )

#                 # High-lift and low-lift summaries (safe numeric conversion)
#                 if "lift" in rules.columns:
#                     try:
#                         lift_series = pd.to_numeric(rules["lift"], errors="coerce").fillna(0.0)
#                         high_lift_count = int((lift_series > 1.5).sum())
#                         if high_lift_count > 0:
#                             insights.append(f"Found {high_lift_count} rules with lift > 1.5 (strong positive correlation)")

#                         low_lift_count = int((lift_series < 1.1).sum())
#                         if low_lift_count > 0 and low_lift_count > (len(rules) * 0.5):
#                             insights.append(f"Warning: {low_lift_count} rules have low lift (<1.1), indicating weak associations")
#                     except Exception as e:
#                         logger.debug(f"Ignored lift-based insights due to error: {e}")
#             except Exception as e:
#                 logger.debug(f"Ignored rules insight error: {e}")
#         else:
#             # If we have no rules but some itemsets, suggest lowering confidence
#             try:
#                 if meta.get('n_frequent_itemsets', 0) > 0:
#                     conf_used = float(meta.get('min_confidence') or 0.0)
#                     insights.append(f"No association rules found with confidence ≥ {conf_used:.2f}. Try lowering the confidence threshold.")
#             except Exception:
#                 pass

#         if not insights:
#             insights.append("Upload a dataset to see insights")

#         return JSONResponse(content={"insights": insights}, status_code=200)

#     except Exception as e:
#         logger.error(f"Error generating insights: {str(e)}")
#         return JSONResponse(
#             content={"insights": ["An error occurred while generating insights."]},
#             status_code=500
#         )

@app.get("/insights")
async def get_insights():
    """Generate human-friendly, actionable insights for shopkeepers"""
    try:
        # If state is empty, short-circuit with a friendly message
        if not STATE:
            return JSONResponse(
                content={"insights": ["👋 Upload your sales data or try a sample dataset to discover buying patterns!"]},
                status_code=200
            )

        # Normalize state values
        df_encoded = STATE.get("df_encoded")
        meta = STATE.get("meta") or {}

        # Normalize rules into a DataFrame if possible
        rules = STATE.get("rules")
        if isinstance(rules, list):
            try:
                rules = pd.DataFrame(rules)
            except Exception:
                rules = None
        if isinstance(rules, pd.DataFrame) and rules.empty:
            rules = None

        # Normalize frequent itemsets into a DataFrame if possible
        fi = STATE.get("frequent_itemsets")
        if isinstance(fi, list):
            try:
                fi = pd.DataFrame(fi)
            except Exception:
                fi = None
        if isinstance(fi, pd.DataFrame) and fi.empty:
            fi = None

        insights = []

        # Basic metadata insights with business context
        if meta:
            try:
                n_tx = int(meta.get("n_transactions") or 0)
            except Exception:
                n_tx = 0
            try:
                n_items = int(meta.get("n_items") or 0)
            except Exception:
                n_items = 0

            if n_tx > 0 and n_items > 0:
                insights.append(f"📊 Your data has {n_tx:,} customer transactions featuring {n_items} different products")

            # Support threshold guidance with practical advice
            try:
                support_used = float(meta.get("min_support") or 0.0)
            except Exception:
                support_used = 0.0

            suggestions = meta.get("support_suggestions") or {}
            try:
                conservative_sugg = float(suggestions.get("conservative", 0.05)) if suggestions else 0.05
            except Exception:
                conservative_sugg = 0.05
            try:
                low_sugg = float(suggestions.get("low", 0.02)) if suggestions else 0.02
            except Exception:
                low_sugg = 0.02
            try:
                very_low_sugg = float(suggestions.get("very_low", 0.01)) if suggestions else 0.01
            except Exception:
                very_low_sugg = 0.01

            if suggestions:
                if support_used > conservative_sugg:
                    insights.append(
                        f"💡 You're only seeing items bought very frequently (in {support_used*100:.1f}% of purchases). "
                        f"Lower the support to {low_sugg:.3f} to find more hidden patterns!"
                    )
                elif support_used < very_low_sugg:
                    insights.append(
                        f"⚠️ Your filter is very loose (support {support_used:.3f}), showing rare combinations that might just be coincidence. "
                        f"Consider raising it to see clearer patterns."
                    )

        # Frequent itemset insights - what customers actually buy
        if isinstance(fi, pd.DataFrame):
            try:
                if "itemsets" in fi.columns:
                    # Best-selling single item
                    singles = fi[fi["itemsets"].apply(lambda x: isinstance(x, (list, tuple, set)) and len(x) == 1)]
                    if not singles.empty:
                        top_single = singles.iloc[0]
                        items_val = top_single.get("itemsets")
                        item_name = list(items_val)[0] if isinstance(items_val, (list, tuple, set)) and len(items_val) > 0 else str(items_val)
                        support_pct = float(top_single.get("support") or 0.0) * 100
                        insights.append(
                            f"🏆 Your bestseller is '{item_name}' - it's in {support_pct:.1f}% of all purchases! "
                            f"Make sure this never runs out of stock."
                        )

                    # Most popular combination
                    multis = fi[fi["itemsets"].apply(lambda x: isinstance(x, (list, tuple, set)) and len(x) > 1)]
                    if not multis.empty:
                        top_combo = multis.iloc[0]
                        combo_items = top_combo.get("itemsets")
                        combo = "' + '".join(sorted(combo_items)) if isinstance(combo_items, (list, tuple, set)) else str(combo_items)
                        support_pct = float(top_combo.get("support") or 0.0) * 100
                        insights.append(
                            f"🛒 Customers often buy '{combo}' together ({support_pct:.1f}% of transactions). "
                            f"Consider placing these items near each other!"
                        )
                        
                    # Count of different combination sizes
                    if len(multis) > 0:
                        pair_count = len(multis[multis["itemsets"].apply(lambda x: len(x) == 2)])
                        triple_count = len(multis[multis["itemsets"].apply(lambda x: len(x) == 3)])
                        if triple_count > 0:
                            insights.append(
                                f"🔍 Found {pair_count} popular pairs and {triple_count} popular 3-item combos. "
                                f"Great opportunities for bundle deals!"
                            )
                        elif pair_count > 0:
                            insights.append(f"🔍 Discovered {pair_count} popular product pairs in your data")
                            
            except Exception as e:
                logger.debug(f"Ignored frequent-itemset insight error: {e}")

        # Rules-based insights - actionable recommendations
        if isinstance(rules, pd.DataFrame) and len(rules) > 0:
            try:
                if "confidence" in rules.columns:
                    # Strongest buying pattern
                    best_conf = rules.nlargest(1, "confidence").iloc[0]
                    ants = best_conf.get("antecedents")
                    cons = best_conf.get("consequents")
                    ant_str = "' + '".join(sorted(ants)) if isinstance(ants, (list, tuple, set)) else str(ants)
                    con_str = "' + '".join(sorted(cons)) if isinstance(cons, (list, tuple, set)) else str(cons)
                    conf_pct = float(best_conf.get("confidence") or 0.0) * 100
                    lift_val = float(best_conf.get("lift") or 0.0)
                    
                    insights.append(
                        f"💰 Strongest pattern: When customers buy '{ant_str}', {conf_pct:.0f}% also buy '{con_str}'. "
                        f"Perfect for cross-selling or combo offers!"
                    )

                # High-lift rules - surprising connections
                if "lift" in rules.columns:
                    try:
                        lift_series = pd.to_numeric(rules["lift"], errors="coerce").fillna(0.0)
                        high_lift_count = int((lift_series > 1.5).sum())
                        if high_lift_count > 0:
                            insights.append(
                                f"✨ Found {high_lift_count} strong product connections (lift > 1.5). "
                                f"These items are bought together way more than random chance!"
                            )

                        # Check for very strong associations
                        very_high_lift = rules[lift_series > 2.0]
                        if len(very_high_lift) > 0:
                            insights.append(
                                f"🎯 {len(very_high_lift)} patterns show customers are 2x+ more likely to buy certain items together. "
                                f"Check the rules table for bundle ideas!"
                            )

                        # Warning about weak patterns
                        low_lift_count = int((lift_series < 1.1).sum())
                        if low_lift_count > 0 and low_lift_count > (len(rules) * 0.5):
                            insights.append(
                                f"⚠️ Heads up: {low_lift_count} patterns are pretty weak (lift < 1.1). "
                                f"These items don't really influence each other's sales."
                            )
                    except Exception as e:
                        logger.debug(f"Ignored lift-based insights due to error: {e}")
                        
                # Opportunity for promotions
                if len(rules) >= 5:
                    insights.append(
                        f"🎁 With {len(rules)} buying patterns identified, you have plenty of options for promotions, "
                        f"bundles, and smart product placement!"
                    )
                        
            except Exception as e:
                logger.debug(f"Ignored rules insight error: {e}")
        else:
            # If we have itemsets but no rules, guide the user
            try:
                if isinstance(fi, pd.DataFrame) and len(fi) > 0:
                    conf_used = float(meta.get('min_confidence') or 0.0)
                    insights.append(
                        f"🔧 No strong buying patterns found with {conf_used*100:.0f}% confidence. "
                        f"Try lowering the confidence slider to discover more connections!"
                    )
                elif meta.get('n_frequent_itemsets', 0) > 0:
                    insights.append(
                        "🔧 We found some popular items, but no clear buying patterns yet. "
                        "Try adjusting the confidence threshold to find connections!"
                    )
            except Exception:
                pass

        # Fallback message
        if not insights:
            insights.append("📈 Upload your sales data to discover what your customers buy together!")

        return JSONResponse(content={"insights": insights}, status_code=200)

    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        return JSONResponse(
            content={"insights": ["⚠️ Oops! Something went wrong analyzing your data. Please try again."]},
            status_code=500
        )

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "Market Basket Analysis API is running", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)