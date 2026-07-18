import os
import numpy as np
from openai import OpenAI

class VectorStore:
    def __init__(self):
        # Local document storage
        self.documents = []
        self.embeddings = []
        self.client = None
        
        # Initialize OpenAI client if key is present
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
            except Exception:
                self.client = None
                
        self._seed_resilience_kb()

    def _seed_resilience_kb(self):
        # Seed standard procedures and maritime logs for crude supply chain risk management
        knowledge_base = [
            {
                "id": "kb_hormuz_sop",
                "title": "Strait of Hormuz Disruption Standard Operating Procedure",
                "content": "In case of a partial or full blockage of the Strait of Hormuz, Persian Gulf crude suppliers (Iraq, Saudi Arabia, Kuwait, Qatar) are severely bottlenecked. Emergency response requires: 1. Activating the Saudi East-West pipeline to bypass Hormuz, routing shipments via Yanbu on the Red Sea. 2. Utilizing UAE Fujairah exports outside the Gulf. 3. Immediately sourcing replacement crude from West Africa (Nigeria) or South America (Brazil) to match Indian West Coast refinery configurations."
            },
            {
                "id": "kb_bab_el_mandeb_risk",
                "title": "Bab el-Mandeb & Red Sea Shipping Geopolitical Briefing",
                "content": "The Bab el-Mandeb strait between Yemen and Djibouti is a high-risk choke point. Active drone/missile strikes or pirate activity increases the base geopolitical risk of the Suez Canal route to 75. Recommended mitigations include: re-routing tankers around the Cape of Good Hope, adding 10-15 transit days and $2.50 per barrel in shipping premiums."
            },
            {
                "id": "kb_refinery_specs",
                "title": "Indian Refinery Crude Blending & Compatibility Guidelines",
                "content": "Indian refineries are categorized by complexity. Jamnagar (Reliance) is a highly complex refinery capable of processing heavy sour crude (low API, high sulfur) with high yield. Kochi and Paradip also possess high sulfur tolerance. Conversely, Mumbai HPCL/BPCL is optimized for light sweet crude (high API, low sulfur like Brent or US WTI). Blending incorrect crude grades can damage distillation columns and reduce diesel/gasoline output by up to 40%."
            },
            {
                "id": "kb_tanker_logistics",
                "title": "Crude Tanker VLCC Charter and Congestion Manual",
                "content": "Very Large Crude Carriers (VLCC) carrying up to 2 million barrels are the most cost-effective shipping vessels. Indian ports like Mundra, Paradip, and Kochi have VLCC berths. Smaller ports or inland-linked refineries (like Panipat served from Mundra) rely on pipeline transshipment. Average port discharge rates: VLCC requires 24-36 hours of berth time. Congestion factors over 50 require shifting vessels to secondary anchorages."
            },
            {
                "id": "kb_cyclone_sop",
                "title": "Arabian Sea Cyclone & Monsoon Maritime Safety Rules",
                "content": "During the monsoon season or active tropical cyclones in the Arabian Sea, wind speeds exceeding 40 knots or wave heights over 5 meters require suspension of all single buoy mooring (SBM) discharges. Mundra and Mumbai ports must close berths. Port-bound tankers must wait in deep water, increasing average port waiting times to 5-7 days."
            }
        ]
        
        for doc in knowledge_base:
            self.add_document(doc["id"], doc["title"], doc["content"])

    def _get_local_embedding(self, text):
        # Fallback term-frequency vectorizer for offline or no-key runs
        words = ["hormuz", "blockage", "pipeline", "red sea", "refinery", "compatibility", "sour", "sweet", "tanker", "vlcc", "cyclone", "weather", "suez", "cape", "disruption"]
        vector = np.zeros(len(words))
        text_lower = text.lower()
        for idx, word in enumerate(words):
            vector[idx] = text_lower.count(word)
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector.tolist()

    def add_document(self, doc_id, title, content):
        doc = {"id": doc_id, "title": title, "content": content}
        self.documents.append(doc)
        
        # Calculate embedding
        if self.client:
            try:
                response = self.client.embeddings.create(
                    input=content,
                    model="text-embedding-3-small"
                )
                emb = response.data[0].embedding
            except Exception:
                emb = self._get_local_embedding(content)
        else:
            emb = self._get_local_embedding(content)
            
        self.embeddings.append(emb)

    def search(self, query, top_k=2):
        if not self.documents:
            return []
            
        # Get query embedding
        if self.client:
            try:
                response = self.client.embeddings.create(
                    input=query,
                    model="text-embedding-3-small"
                )
                query_emb = response.data[0].embedding
            except Exception:
                query_emb = self._get_local_embedding(query)
        else:
            query_emb = self._get_local_embedding(query)
            
        # Compute cosine similarity
        similarities = []
        for emb in self.embeddings:
            dot_product = np.dot(query_emb, emb)
            norm_q = np.linalg.norm(query_emb)
            norm_e = np.linalg.norm(emb)
            if norm_q > 0 and norm_e > 0:
                sim = dot_product / (norm_q * norm_e)
            else:
                sim = 0.0
            similarities.append(sim)
            
        # Rank document indices
        ranked_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in ranked_indices:
            results.append({
                "document": self.documents[idx],
                "score": float(similarities[idx])
            })
            
        return results
