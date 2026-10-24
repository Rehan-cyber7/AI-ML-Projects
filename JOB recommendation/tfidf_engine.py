"""
Custom TF-IDF Vectorizer & Cosine Similarity Engine.
Implemented purely using NumPy and SciPy (without scikit-learn).
"""

import math
import re
from typing import List, Dict
import numpy as np
import scipy.sparse as sp

class CustomTFIDFVectorizer:
    def __init__(self, max_features: int = None, lowercase: bool = True):
        self.max_features = max_features
        self.lowercase = lowercase
        self.vocabulary_: Dict[str, int] = {}
        self.idf_: np.ndarray = None

    def _tokenize(self, text: str) -> List[str]:
        if self.lowercase:
            text = text.lower()
        return re.findall(r'\b[a-zA-Z0-9+#.-]+\b', text)

    def fit_transform(self, raw_documents: List[str]) -> sp.csr_matrix:
        doc_tokens = [self._tokenize(doc) for doc in raw_documents]
        df = {}
        tf_list = []

        for tokens in doc_tokens:
            counts = {}
            for token in tokens:
                counts[token] = counts.get(token, 0) + 1
            tf_list.append(counts)
            for token in set(counts.keys()):
                df[token] = df.get(token, 0) + 1

        vocab_items = sorted(df.items(), key=lambda x: (-x[1], x[0]))
        if self.max_features is not None:
            vocab_items = vocab_items[:self.max_features]

        self.vocabulary_ = {term: i for i, (term, _) in enumerate(vocab_items)}
        n_docs = len(raw_documents)

        self.idf_ = np.zeros(len(self.vocabulary_))
        for term, idx in self.vocabulary_.items():
            doc_freq = df[term]
            self.idf_[idx] = math.log((1 + n_docs) / (1 + doc_freq)) + 1.0

        return self._build_csr_matrix(tf_list, n_docs)

    def transform(self, raw_documents: List[str]) -> sp.csr_matrix:
        doc_tokens = [self._tokenize(doc) for doc in raw_documents]
        n_docs = len(raw_documents)
        tf_list = []
        for tokens in doc_tokens:
            counts = {}
            for token in tokens:
                counts[token] = counts.get(token, 0) + 1
            tf_list.append(counts)

        return self._build_csr_matrix(tf_list, n_docs)

    def _build_csr_matrix(self, tf_list: List[Dict[str, int]], n_docs: int) -> sp.csr_matrix:
        rows, cols, data = [], [], []
        for doc_idx, counts in enumerate(tf_list):
            doc_len = sum(counts.values())
            if doc_len == 0:
                continue
            for term, count in counts.items():
                if term in self.vocabulary_:
                    col_idx = self.vocabulary_[term]
                    tf = count / doc_len
                    tfidf_val = tf * self.idf_[col_idx]
                    rows.append(doc_idx)
                    cols.append(col_idx)
                    data.append(tfidf_val)

        X = sp.csr_matrix((data, (rows, cols)), shape=(n_docs, len(self.vocabulary_)))
        row_norms = sp.linalg.norm(X, axis=1)
        row_norms[row_norms == 0] = 1.0
        inv_norms = sp.csr_matrix(1.0 / row_norms[:, None])
        return X.multiply(inv_norms).tocsr()

def compute_cosine_similarity(doc1: str, doc2: str) -> float:
    if not doc1.strip() or not doc2.strip():
        return 0.0
    vectorizer = CustomTFIDFVectorizer()
    matrix = vectorizer.fit_transform([doc1, doc2])
    cos_sim = (matrix[0] * matrix[1].T).toarray()[0, 0]
    return float(np.clip(cos_sim, 0.0, 1.0))