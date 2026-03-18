import json
import os
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from core.logger import logger


@dataclass
class MemoryResult:
    collection: str
    text: str
    metadata: dict
    distance: float
    doc_id: str


class SemanticMemory:
    """Núcleo do subsistema de Memória Longa Semântica do ORION."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SemanticMemory, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.chroma_client: Optional[chromadb.PersistentClient] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self.collections: Dict[str, Any] = {}
        
        self.db_path = os.path.join(os.path.dirname(__file__), "chroma_db")
        
        try:
            os.makedirs(self.db_path, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(allow_reset=True, anonymized_telemetry=False)
            )
            
            # Carrega o embedder (leve, multilingue)
            logger.info("[SemanticMemory] Carregando modelo de embedding...")
            self.embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            
            # Garante a criação/carregamento das collections
            self.collections["orion_episodic"] = self.chroma_client.get_or_create_collection(
                name="orion_episodic", metadata={"description": "Conversas temporais passadas"}
            )
            self.collections["orion_semantic"] = self.chroma_client.get_or_create_collection(
                name="orion_semantic", metadata={"description": "Fatos duráveis sobre o usuário"}
            )
            self.collections["orion_procedural"] = self.chroma_client.get_or_create_collection(
                name="orion_procedural", metadata={"description": "Padrões operacionais recorrentes"}
            )
            logger.info("[SemanticMemory] Inicializado com sucesso e conectado ao ChromaDB.")
            
        except Exception as e:
            logger.warning(f"[SemanticMemory] Falhou ao inicializar (o sistema rodará sem memória): {e}")

    def is_available(self) -> bool:
        """Verifica se a memória semântica foi inicializada sem falhas."""
        return self.chroma_client is not None and self.embedding_model is not None

    def store_episode(self, text: str, metadata: dict) -> None:
        """Salva fragmentos de conversa temporal passada na coleção episódica."""
        if not self.is_available():
            return
            
        try:
            doc_id = f"ep_{uuid4().hex[:12]}"
            embeddings = self.embedding_model.encode([text])[0].tolist()
            
            # Garante que timestamps e sources estejam preenchidos
            if "timestamp" not in metadata:
                 metadata["timestamp"] = datetime.utcnow().isoformat()
            if "source" not in metadata:
                 metadata["source"] = "conversation"
                 
            self.collections["orion_episodic"].add(
                ids=[doc_id],
                embeddings=[embeddings],
                documents=[text],
                metadatas=[metadata]
            )
            logger.debug(f"[SemanticMemory] Episódio salvo: {doc_id}")
        except Exception as e:
            logger.error(f"[SemanticMemory] Falha ao salvar episódio: {e}")

    def store_fact(self, fact: str, category: str, confidence: float = 1.0) -> None:
        """Salva fatos duráveis sobre o usuário na coleção semântica."""
        if not self.is_available():
            return
            
        if category not in ("preference", "identity", "context", "skill", "relationship"):
            logger.warning(f"[SemanticMemory] Categoria de fato inválida ignorada: {category}")
            return
            
        try:
            embeddings = self.embedding_model.encode([fact])[0].tolist()
            
            # Verifica existência para atualizar ao invés de duplicar duplicar
            results = self.collections["orion_semantic"].query(
                query_embeddings=[embeddings],
                n_results=1
            )
            
            needs_update = False
            target_id = None
            if results["distances"] and len(results["distances"][0]) > 0:
                dist = results["distances"][0][0]
                # Limite de distáncia para similaridade considerável
                if dist < 0.08: # distance_cosine -> similarity > 0.92
                    needs_update = True
                    target_id = results["ids"][0][0]

            metadata = {
                "category": category,
                "confidence": confidence,
                "created_at": datetime.utcnow().isoformat()
            }
            
            if needs_update and target_id:
                self.collections["orion_semantic"].update(
                    ids=[target_id],
                    embeddings=[embeddings],
                    documents=[fact],
                    metadatas=[metadata]
                )
                logger.debug(f"[SemanticMemory] Fato atualizado: {target_id}")
            else:
                doc_id = f"fact_{uuid4().hex[:12]}"
                self.collections["orion_semantic"].add(
                    ids=[doc_id],
                    embeddings=[embeddings],
                    documents=[fact],
                    metadatas=[metadata]
                )
                logger.debug(f"[SemanticMemory] Fato salvo: {doc_id}")
                
        except Exception as e:
            logger.error(f"[SemanticMemory] Falha ao armazenar fato: {e}")

    def store_procedure(self, trigger: str, sequence: List[str], success_count: int = 1) -> None:
        """Salva padrões operacionais recorrentes ativados por um trigger na coleção procedimental."""
        if not self.is_available():
            return
            
        try:
            doc_id = f"proc_{uuid4().hex[:12]}"
            embeddings = self.embedding_model.encode([trigger])[0].tolist()
            
            metadata = {
                "sequence": json.dumps(sequence),
                "success_count": success_count,
                "last_used": datetime.utcnow().isoformat()
            }
            
            self.collections["orion_procedural"].add(
                ids=[doc_id],
                embeddings=[embeddings],
                documents=[trigger],
                metadatas=[metadata]
            )
            logger.debug(f"[SemanticMemory] Procedimento salvo: {doc_id}")
        except Exception as e:
            logger.error(f"[SemanticMemory] Falha ao armazenar procedimento: {e}")

    def search(self, query: str, collections: Optional[List[str]] = None, top_k: int = 5) -> List[MemoryResult]:
        """Busca vetorizada padronizada sobre as coleções para um texto específico."""
        if not self.is_available():
            return []
            
        targets = collections if collections else list(self.collections.keys())
        results: List[MemoryResult] = []
        
        try:
            embeddings = self.embedding_model.encode([query])[0].tolist()
            
            for col_name in set(targets).intersection(self.collections.keys()):
                 try:
                     col = self.collections[col_name]
                     count = col.count()
                     # Chroma throws exception if checking n_results > doc counts.
                     actual_k = min(top_k, count)
                     
                     if actual_k <= 0:
                         continue
                         
                     res = col.query(
                         query_embeddings=[embeddings],
                         n_results=actual_k
                     )
                     
                     if not res.get("distances") or not res["distances"][0]:
                         continue
                         
                     for i in range(len(res["ids"][0])):
                         dist = res["distances"][0][i]
                         # Threshold base
                         if dist > 0.25:  # Consideramos cosinus_distance. dist > 0.25 significa similaridade < 0.75
                             continue
                             
                         results.append(MemoryResult(
                             collection=col_name,
                             text=res["documents"][0][i],
                             metadata=res["metadatas"][0][i],
                             distance=dist,
                             doc_id=res["ids"][0][i]
                         ))
                 except Exception as e:
                     logger.warning(f"[SemanticMemory] Erro buscando na coleção {col_name}: {e}")
            
            # Ordena por relevância (menor distância no topo)
            results.sort(key=lambda x: x.distance)
            return results[:top_k]
                
        except Exception as e:
            logger.error(f"[SemanticMemory] Busca falhou de forma primária: {e}")
            return []

    def get_context_for_prompt(self, query: str, max_tokens: int = 500) -> str:
        """Retorna as top correspondências convertidas em string legível pelo LLM para contextualização."""
        if not self.is_available():
            return ""
            
        matches = self.search(query, top_k=8)
        
        if not matches:
            return ""
            
        lines = ["[MEMÓRIA RELEVANTE]"]
        char_count = 0
        max_chars = max_tokens * 4
        
        for m in matches:
            # Seleção de formato
            if m.collection == "orion_episodic":
                ts = m.metadata.get("timestamp", "desconhecido").split("T")[0]
                entry = f"- (episódico, {ts}): \"{m.text}\""
            elif m.collection == "orion_semantic":
                cat = m.metadata.get("category", "unclassified")
                entry = f"- (semântico, {cat}): \"{m.text}\""
            elif m.collection == "orion_procedural":
                seq = m.metadata.get("sequence", "[]")
                entry = f"- (procedimental, gatilho sugerido: {m.text}): \"{seq}\""
            else:
                 continue
                 
            if char_count + len(entry) > max_chars:
                break
                
            lines.append(entry)
            char_count += len(entry)
            
        lines.append("[FIM DA MEMÓRIA]")
        
        return "\n".join(lines)
