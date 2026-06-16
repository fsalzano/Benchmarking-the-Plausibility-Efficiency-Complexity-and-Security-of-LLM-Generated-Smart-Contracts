from sentence_transformers import SentenceTransformer, util
import pandas as pd
import os

# Show full text in DataFrame columns
pd.set_option('display.max_colwidth', None)

def normalize_text(s):
    return ' '.join(str(s).strip().split())

def find_similar_notice_matches(query_notice,
                                top_k=5,
                                threshold=0.7,
                                file_notice_only='functions_dataset_only_notices.csv',
                                file_full='functions_dataset.csv'):

    # Absolute path to the directory of the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Relative paths to the CSV files
    path_notice_only = os.path.join(base_dir, file_notice_only)
    path_full = os.path.join(base_dir, file_full)

    # Load model and encode the query
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_notice = normalize_text(query_notice)
    query_emb = model.encode(query_notice, convert_to_tensor=True)

    # === Step 1: Search in the notice_comment dataset ===
    df_notice = pd.read_csv(path_notice_only)
    df_notice['notice_comment'] = (
        df_notice['notice_comment']
        .fillna('')
        .astype(str)
        .apply(normalize_text)
    )

    notice_embeddings = model.encode(df_notice['notice_comment'].tolist(), convert_to_tensor=True)
    similarities = util.cos_sim(query_emb, notice_embeddings)[0]
    df_notice['similarity'] = similarities.cpu().numpy()

    # Filter and remove duplicates based on notice content
    filtered_notice = df_notice[
        (df_notice['similarity'] >= threshold) & (df_notice['similarity'] < 1.0)
    ].copy()
    filtered_notice = filtered_notice.drop_duplicates(subset=['notice_comment'])

    top_matches = filtered_notice.sort_values(by='similarity', ascending=False).head(top_k)

    # If enough high-confidence matches found, return them
    if len(top_matches) >= top_k:
        top_matches['match_source'] = 'notice_comment'
        return top_matches

    # === Step 2: Fallback to full_comment dataset ===
    df_full = pd.read_csv(path_full)
    df_full['full_comment'] = (
        df_full['full_comment']
        .fillna('')
        .astype(str)
        .apply(normalize_text)
    )

    full_embeddings = model.encode(df_full['full_comment'].tolist(), convert_to_tensor=True)
    similarities_full = util.cos_sim(query_emb, full_embeddings)[0]
    df_full['similarity'] = similarities_full.cpu().numpy()

    # Filter and remove duplicates based on full comment
    filtered_full = df_full[
        (df_full['similarity'] >= threshold) & (df_full['similarity'] < 1.0)
    ].copy()
    filtered_full = filtered_full.drop_duplicates(subset=['full_comment'])

    fallback_matches = filtered_full.sort_values(by='similarity', ascending=False).head(top_k)


    fallback_matches['match_source'] = 'full_comment'
    return fallback_matches
