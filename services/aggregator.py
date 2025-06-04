"""
AITON-RAG Aggregator Service
Strukturiert Markdown-Dateien für Custom GPT Actions Optimierung
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai

from config import Config

class Aggregator:
    """Actions-optimierte Strukturierung von RAG-Inhalten"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # OpenAI setup
        if self.config.OPENAI_API_KEY:
            openai.api_key = self.config.OPENAI_API_KEY
        else:
            self.logger.warning("OpenAI API Key not configured")
    
    def aggregate_knowledge_base(self) -> Dict[str, Any]:
        """
        Aggregiert alle RAG-Dateien zu einer strukturierten Wissensbasis
        
        Returns:
            Strukturierte Wissensbasis für Custom GPT Actions
        """
        try:
            # Load all RAG files
            rag_files = self._load_rag_files()
            
            if not rag_files:
                self.logger.info("No RAG files found")
                return self._create_empty_knowledge_base()
            
            # Structure content using OpenAI
            structured_content = self._structure_content_with_ai(rag_files)
            
            # Build knowledge base
            knowledge_base = self._build_knowledge_base(rag_files, structured_content)
            
            # Save to knowledge base directory
            self._save_knowledge_base(knowledge_base)
            
            return knowledge_base
            
        except Exception as e:
            self.logger.error(f"Error aggregating knowledge base: {str(e)}")
            return self._create_empty_knowledge_base()
    
    def _load_rag_files(self) -> List[Dict]:
        """Lädt alle Markdown-Dateien aus dem RAG-Verzeichnis"""
        rag_files = []
        
        for file_path in self.config.RAG_DIR.glob('*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse frontmatter
                metadata, markdown_content = self._parse_frontmatter(content)
                
                rag_files.append({
                    'file_path': str(file_path),
                    'filename': file_path.name,
                    'metadata': metadata,
                    'content': markdown_content
                })
                
            except Exception as e:
                self.logger.error(f"Error loading {file_path}: {str(e)}")
                
        return rag_files
    
    def _parse_frontmatter(self, content: str) -> tuple:
        """Parst YAML Frontmatter aus Markdown"""
        metadata = {}
        markdown_content = content
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                markdown_content = parts[2].strip()
                
                # Simple YAML parsing
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
        
        return metadata, markdown_content
    
    def _structure_content_with_ai(self, rag_files: List[Dict]) -> Dict[str, Any]:
        """Strukturiert Inhalte mit OpenAI für Actions-Optimierung"""
        if not self.config.OPENAI_API_KEY:
            return self._structure_content_fallback(rag_files)
        
        try:
            # Prepare content for AI processing
            combined_content = self._prepare_content_for_ai(rag_files)
            
            # Load system prompt
            system_prompt = self._load_system_prompt()
            
            # Call OpenAI
            response = openai.ChatCompletion.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": combined_content}
                ],
                max_tokens=self.config.OPENAI_MAX_TOKENS,
                temperature=0.3
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            structured_content = self._parse_ai_response(ai_response)
            
            return structured_content
            
        except Exception as e:
            self.logger.error(f"Error structuring with AI: {str(e)}")
            return self._structure_content_fallback(rag_files)
    
    def _prepare_content_for_ai(self, rag_files: List[Dict]) -> str:
        """Bereitet Inhalte für AI-Verarbeitung vor"""
        content_parts = []
        
        for file_data in rag_files:
            filename = file_data['filename']
            content = file_data['content']
            
            # Truncate very long content
            if len(content) > 2000:
                content = content[:2000] + "... [truncated]"
            
            content_parts.append(f"=== FILE: {filename} ===\n{content}\n")
        
        return "\n".join(content_parts)
    
    def _load_system_prompt(self) -> str:
        """Lädt System Prompt für Actions-Optimierung"""
        prompt_path = self.config.BASE_DIR / "prompts" / "actions_system_prompt.md"
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """Standard System Prompt falls keine Datei vorhanden"""
        return """# Rolle: Custom GPT Actions Daten-Optimierer

Du bist ein spezialisierter Assistent zur Aufbereitung von Dokumenten für ChatGPT Custom GPT Actions.

## Aufgabe
Erstelle eine strukturierte, Custom GPT Actions-optimierte Wissensbasis aus bereitgestellten Dokumenten.

## Kategorisierungs-Schema
- **processes**: Workflows, Anleitungen, Schritt-für-Schritt Prozesse
- **definitions**: Begriffe, Definitionen, Glossare, Erklärungen
- **analysis**: Berichte, Analysen, Erkenntnisse, Daten
- **reference**: Spezifikationen, Manuals, Referenzmaterialien

## Output Format
Antworte ausschließlich mit gültigem JSON in folgendem Format:
{
  "categories": {
    "processes": ["process1", "process2"],
    "definitions": ["term1: definition", "term2: definition"],
    "analysis": ["insight1", "insight2"],
    "reference": ["ref1", "ref2"]
  },
  "key_concepts": {
    "concept_name": {
      "description": "detailed explanation",
      "category": "category_name",
      "related_topics": ["topic1", "topic2"]
    }
  },
  "structured_procedures": {
    "procedure_name": {
      "steps": ["step1", "step2"],
      "requirements": ["req1", "req2"],
      "category": "processes"
    }
  }
}"""
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parst AI-Response zu strukturierten Daten"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Fallback to empty structure
        return {
            "categories": {"processes": [], "definitions": [], "analysis": [], "reference": []},
            "key_concepts": {},
            "structured_procedures": {}
        }
    
    def _structure_content_fallback(self, rag_files: List[Dict]) -> Dict[str, Any]:
        """Fallback-Strukturierung ohne AI"""
        categories = {"processes": [], "definitions": [], "analysis": [], "reference": []}
        key_concepts = {}
        structured_procedures = {}
        
        for file_data in rag_files:
            content = file_data['content'].lower()
            filename = file_data['filename']
            
            # Simple keyword-based categorization
            if any(word in content for word in ['schritt', 'prozess', 'anleitung', 'workflow']):
                categories['processes'].append(filename)
            elif any(word in content for word in ['definition', 'bedeutung', 'begriff']):
                categories['definitions'].append(filename)
            elif any(word in content for word in ['analyse', 'bericht', 'ergebnis']):
                categories['analysis'].append(filename)
            else:
                categories['reference'].append(filename)
        
        return {
            "categories": categories,
            "key_concepts": key_concepts,
            "structured_procedures": structured_procedures
        }
    
    def _build_knowledge_base(self, rag_files: List[Dict], structured_content: Dict[str, Any]) -> Dict[str, Any]:
        """Baut die finale Wissensbasis für Custom GPT Actions"""
        
        # Build search index
        search_index = self._build_search_index(rag_files)
        
        knowledge_base = {
            "action_response": {
                "status": "success",
                "action_type": "knowledge_base",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "knowledge_base": {
                        "action_metadata": {
                            "api_version": self.config.API_VERSION,
                            "last_updated": datetime.now().isoformat(),
                            "document_count": len(rag_files),
                            "action_compatible": True,
                            "custom_gpt_optimized": True
                        },
                        "categories": self._format_categories_for_actions(structured_content.get("categories", {})),
                        "structured_content": {
                            "action_optimized": True,
                            "key_concepts": structured_content.get("key_concepts", {}),
                            "procedures": structured_content.get("structured_procedures", {}),
                            "definitions": self._extract_definitions(rag_files, structured_content)
                        },
                        "action_search_index": search_index,
                        "documents": [
                            {
                                "filename": file_data['filename'],
                                "content_preview": file_data['content'][:200] + "..." if len(file_data['content']) > 200 else file_data['content'],
                                "metadata": file_data['metadata']
                            }
                            for file_data in rag_files
                        ]
                    }
                },
                "action_guidance": {
                    "custom_gpt_instructions": "Use this structured knowledge base to answer user questions. Reference specific documents and provide detailed, contextual responses.",
                    "response_suggestions": [
                        "I found relevant information in your documents...",
                        "Based on the uploaded materials...",
                        "According to your documentation..."
                    ],
                    "follow_up_actions": [
                        "Would you like me to search for more specific information?",
                        "Shall I look for related topics in your knowledge base?"
                    ]
                }
            }
        }
        
        return knowledge_base
    
    def _format_categories_for_actions(self, categories: Dict[str, List]) -> Dict[str, Any]:
        """Formatiert Kategorien für Actions-Optimierung"""
        formatted_categories = {}
        
        for category, items in categories.items():
            formatted_categories[category] = {
                "count": len(items),
                "action_summary": f"{category.title()} available for Custom GPT queries",
                "documents": items,
                "action_relevant": True
            }
        
        return formatted_categories
    
    def _extract_definitions(self, rag_files: List[Dict], structured_content: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahiert Definitionen aus den Inhalten"""
        definitions = {}
        
        # Use AI-extracted definitions if available
        if "definitions" in structured_content.get("categories", {}):
            for definition in structured_content["categories"]["definitions"]:
                if ":" in definition:
                    term, desc = definition.split(":", 1)
                    definitions[term.strip()] = {
                        "definition": desc.strip(),
                        "source": "ai_extracted",
                        "action_priority": "high"
                    }
        
        return definitions
    
    def _build_search_index(self, rag_files: List[Dict]) -> Dict[str, Any]:
        """Baut Search Index für Actions"""
        all_text = " ".join([file_data['content'] for file_data in rag_files])
        
        # Extract keywords (simple approach)
        words = re.findall(r'\w+', all_text.lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only meaningful words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:50]
        keywords = [word for word, freq in top_keywords]
        
        return {
            "optimized_for_actions": True,
            "keywords": keywords,
            "topics": list(set([file_data['filename'].split('_')[0] for file_data in rag_files])),
            "entities": [],  # Could be enhanced with NER
            "custom_gpt_queries": [
                "What processes are documented?",
                "What are the key definitions?",
                "What analysis is available?",
                "What reference materials exist?"
            ],
            "context_hints": [
                "Use 'processes' for step-by-step guidance",
                "Use 'definitions' for term explanations",
                "Use 'analysis' for insights and data",
                "Use 'reference' for specifications"
            ]
        }
    
    def _save_knowledge_base(self, knowledge_base: Dict[str, Any]) -> None:
        """Speichert die Wissensbasis"""
        try:
            knowledge_base_path = self.config.KNOWLEDGE_BASE_DIR / "knowledge_base.json"
            
            with open(knowledge_base_path, 'w', encoding='utf-8') as f:
                json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Knowledge base saved to {knowledge_base_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving knowledge base: {str(e)}")
    
    def _create_empty_knowledge_base(self) -> Dict[str, Any]:
        """Erstellt leere Wissensbasis"""
        return {
            "action_response": {
                "status": "success",
                "action_type": "knowledge_base",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "knowledge_base": {
                        "action_metadata": {
                            "api_version": self.config.API_VERSION,
                            "last_updated": datetime.now().isoformat(),
                            "document_count": 0,
                            "action_compatible": True,
                            "custom_gpt_optimized": True
                        },
                        "categories": {},
                        "structured_content": {"action_optimized": True},
                        "action_search_index": {"optimized_for_actions": True},
                        "documents": []
                    }
                },
                "action_guidance": {
                    "custom_gpt_instructions": "No documents have been uploaded yet. Please upload documents to build the knowledge base.",
                    "response_suggestions": ["Upload documents to get started"],
                    "follow_up_actions": ["Upload your first document"]
                }
            }
        }
    
    def search_knowledge_base(self, query: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Durchsucht die Wissensbasis
        
        Args:
            query: Suchbegriff
            category: Optional category filter
            
        Returns:
            Suchergebnisse für Custom GPT Actions
        """
        try:
            # Load knowledge base
            knowledge_base_path = self.config.KNOWLEDGE_BASE_DIR / "knowledge_base.json"
            
            if not knowledge_base_path.exists():
                return self._create_empty_search_result(query)
            
            with open(knowledge_base_path, 'r', encoding='utf-8') as f:
                knowledge_base = json.load(f)
            
            # Perform search
            search_results = self._perform_search(knowledge_base, query, category)
            
            return {
                "action_response": {
                    "status": "success",
                    "action_type": "search",
                    "timestamp": datetime.now().isoformat(),
                    "query": query,
                    "category_filter": category,
                    "data": search_results,
                    "action_guidance": {
                        "custom_gpt_instructions": f"Present these search results for query '{query}' in a helpful, structured way",
                        "response_suggestions": [
                            f"I found information about '{query}' in your documents",
                            f"Here's what I found regarding '{query}'"
                        ]
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error searching knowledge base: {str(e)}")
            return self._create_empty_search_result(query)
    
    def _perform_search(self, knowledge_base: Dict, query: str, category: Optional[str]) -> Dict[str, Any]:
        """Führt die tatsächliche Suche durch"""
        results = {
            "matches": [],
            "categories": [],
            "concepts": [],
            "documents": []
        }
        
        query_lower = query.lower()
        kb_data = knowledge_base.get("action_response", {}).get("data", {}).get("knowledge_base", {})
        
        # Search in categories
        categories = kb_data.get("categories", {})
        for cat_name, cat_data in categories.items():
            if category and cat_name != category:
                continue
            
            if query_lower in cat_name or any(query_lower in doc.lower() for doc in cat_data.get("documents", [])):
                results["categories"].append({
                    "category": cat_name,
                    "summary": cat_data.get("action_summary", ""),
                    "relevance": "high"
                })
        
        # Search in documents
        for doc in kb_data.get("documents", []):
            if query_lower in doc.get("content_preview", "").lower() or query_lower in doc.get("filename", "").lower():
                results["documents"].append({
                    "filename": doc.get("filename"),
                    "preview": doc.get("content_preview"),
                    "relevance": "medium"
                })
        
        return results
    
    def _create_empty_search_result(self, query: str) -> Dict[str, Any]:
        """Erstellt leeres Suchergebnis"""
        return {
            "action_response": {
                "status": "success",
                "action_type": "search",
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "data": {"matches": [], "message": "No documents found. Please upload documents first."},
                "action_guidance": {
                    "custom_gpt_instructions": "Inform the user that no documents are available for search",
                    "response_suggestions": ["No documents have been uploaded yet"]
                }
            }
        }
