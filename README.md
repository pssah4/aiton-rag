# AITON-RAG Tool

Ein Python-basiertes Tool für Datei-Upload, Konvertierung zu Markdown und automatische **strukturierte Zusammenstellung** mit **ChatGPT Custom GPT Actions** Integration.

## 🎯 Projektziel

**Upload von Dateien → Konvertierung zu Markdown → Strukturierte Zusammenstellung → Custom GPT Actions API**

Das Tool ermöglicht es, verschiedene Dokumentformate hochzuladen, automatisch in eine strukturierte Wissensbasis zu konvertieren und diese optimal für **ChatGPT Custom GPT Actions** bereitzustellen - ohne Informationsverlust durch Zusammenfassungen.

## 🏗️ Lösungsarchitektur

### Deployment-Strategie
- **Entwicklung**: GitHub Codespace für lokale Tests
- **Produktion**: Cloud-Deployment (Railway/Render) für permanente Verfügbarkeit
- **Trigger-basiert**: Alle Prozesse werden durch User-Upload ausgelöst (ressourceneffizient)

### System-Komponenten (Custom GPT Actions optimiert)
```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Upload UI     │ →  │ File Process │ →  │   Aggregator    │
│ (Desktop/Web)   │    │   Service    │    │ (Actions-ready) │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                ↓
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│ ChatGPT Custom  │ ←  │ Actions API  │ ←  │  Knowledge Base │
│ GPT (Actions)   │    │   Server     │    │ (JSON optimiert)│
└─────────────────┘    └──────────────┘    └─────────────────┘
```

### Custom GPT Actions Workflow
```
1. User stellt Frage an Custom GPT
   ↓
2. Custom GPT erkennt: "Brauche Daten aus AITON-RAG"
   ↓
3. Custom GPT triggert Action: getKnowledgeBase() oder searchKnowledge()
   ↓
4. AITON-RAG API liefert strukturierte, action-optimierte Daten
   ↓
5. Custom GPT verarbeitet Daten und antwortet kontextuell
   ↓
6. User erhält intelligente Antwort basierend auf hochgeladenen Dokumenten
```

## 📁 Projektstruktur

```
aiton-rag/
├── 🚀 run.py                    # Starter-Skript (Desktop UI + Server)
├── 🌐 app.py                    # Flask Haupt-Application
├── ⚙️ config.py                 # Zentrale Konfiguration
├── 📦 requirements.txt          # Python Dependencies
├── 🔒 .env.example             # Environment Template
├── 🚫 .gitignore               # Git Ignore Regeln
├── 📊 Procfile                 # Cloud Deployment Config
│
├── 🛠️ services/                # Core Business Logic
│   ├── __init__.py
│   ├── file_processor.py       # Datei → Markdown Konverter
│   ├── aggregator.py           # Actions-optimierte Strukturierung
│   ├── watcher.py              # Dateiüberwachung Service
│   └── actions_api.py          # Custom GPT Actions Integration
│
├── 🎨 ui/                      # User Interface
│   ├── __init__.py
│   └── desktop_ui.py           # Tkinter Desktop Application
│
├── 🌐 templates/               # Web Templates
│   ├── upload.html             # Upload Interface
│   └── status.html             # Status Dashboard
│
├── 📱 static/                  # Frontend Assets
│   ├── css/
│   │   └── style.css           # Minimalistisches Design
│   └── js/
│       └── upload.js           # Upload Functionality
│
├── 📂 data/                    # Datenverzeichnisse
│   ├── uploads/                # Upload-Verzeichnis (temporär)
│   ├── rag/                    # Markdown-Dateien (verarbeitet)
│   └── knowledge_base/         # Actions-optimierte Wissensbasis
│
├── 🔌 custom_gpt_config/       # Custom GPT Actions Setup
│   ├── actions_schema.json     # OpenAPI Schema für Custom GPT Actions
│   ├── actions_setup_guide.txt # Schritt-für-Schritt Setup Anleitung
│   ├── api_auth.txt           # API Authentication Details
│   └── test_queries.txt        # Test-Queries für Actions
│
└── 📋 prompts/                 # AI Prompts
    ├── actions_system_prompt.md # System Prompt für Actions-Optimierung
    └── actions_response_template.json # Response Template für Actions
```

## 🔄 Automatisierter Workflow

### 1. Upload-Prozess
```
Benutzer wählt Datei(en) → Desktop UI / Web Interface → Upload zu /data/uploads/
```

### 2. Verarbeitungs-Pipeline (Actions-optimiert)
```
1. 📁 File Detection
   └── Neue Datei in uploads/ erkannt
   
2. 🔍 File Type Analysis  
   └── PDF, DOCX, TXT, HTML, MD, etc.
   
3. 📝 Markdown Conversion
   └── Intelligente Konvertierung mit Metadaten
   
4. 💾 RAG Storage
   └── Speicherung in /data/rag/ mit Struktur
   
5. 🧠 Actions-optimierte Aggregation (GPT-4o)
   └── System Prompt für Custom GPT Actions Optimierung
   
6. 📊 Knowledge Base Update
   └── JSON-Struktur speziell für Custom GPT Actions
   
7. 🔌 Actions API Update
   └── Neue Daten über Custom GPT Actions abrufbar
```

### 3. Custom GPT Actions Integration
```
Custom GPT User Query → Action Trigger → AITON-RAG API → Strukturierte Response → Custom GPT Answer
```

## 🛠️ Technologie-Stack

### Backend Framework
- **Flask**: Lightweight Web-Framework mit Actions API
- **python-dotenv**: Environment Management
- **watchdog**: Dateiüberwachung
- **pathlib**: Moderne Pfad-Verarbeitung

### AI Integration (Actions-optimiert) 
- **openai**: GPT-4o API Integration für Actions-Strukturierung
- **tiktoken**: Token-Management für Actions
- **tenacity**: Retry-Logic für API-Calls

### File Processing
- **markdownify**: HTML → Markdown
- **python-docx**: Word-Dokumente
- **PyPDF2**: PDF-Verarbeitung  
- **python-magic**: Automatische Dateityp-Erkennung
- **chardet**: Encoding-Detection

### UI & Web
- **tkinter**: Desktop UI (Python Built-in)
- **flask-uploads**: Sichere File-Uploads
- **jinja2**: Template Engine

### Security & Utils
- **werkzeug**: HTTP Utilities & Security
- **uuid**: Eindeutige Identifiers
- **hashlib**: File Checksums
- **json**: Strukturierte Daten für Actions

## 🎛️ Kern-Komponenten im Detail

### 1. **app.py** - Haupt-Application (Actions-ready)
```python
# Zentrale Flask-Application mit Custom GPT Actions Support
- Custom GPT Actions API Endpoints (/api/actions/*)
- Web Upload Interface
- Health Checks & Monitoring für Actions
- Service Koordination
- Actions-spezifisches Error Handling & Logging
```

### 2. **services/file_processor.py** - Intelligente Dateiverarbeitung
```python
# Unterstützte Formate & Features
- PDF: Text + Metadaten Extraktion
- DOCX: Vollständige Formatierung
- HTML: Clean Markdown Conversion
- TXT: Encoding-sichere Verarbeitung
- Batch-Processing für mehrere Dateien
- Duplikats-Erkennung via Hash
- Actions-optimierte Metadaten Extraktion
```

### 3. **services/aggregator.py** - Actions-optimierte Strukturierung
```python
# GPT-4o Integration speziell für Custom GPT Actions
- Actions-spezifische System Prompts
- Response Format für optimale Actions Integration
- Kategorisierung für Actions-Queries
- Context-Preservation für Custom GPT Verständnis
- Incremental Updates (nur Änderungen)
- Actions Metadata Generation
```

### 4. **services/actions_api.py** - Custom GPT Actions Integration
```python
# Speziell für ChatGPT Custom GPT Actions entwickelt
- OpenAPI Schema Generation für Actions
- Actions-kompatible Response Formate
- Authentication für Custom GPT Actions
- Rate Limiting für Action Calls
- Actions-spezifische Error Handling
```

### 5. **ui/desktop_ui.py** - Desktop Interface
```python
# Moderne Tkinter UI
- Drag & Drop Support
- Multi-File Selection
- Progress Indicators mit Actions Status
- Actions Connectivity Status
- Keine Browser-Abhängigkeit
```

### 6. **services/watcher.py** - Automatische Überwachung
```python
# File System Monitoring mit Actions Integration
- Real-time Upload Detection
- Actions API Update Triggers
- Duplicate Prevention
- Actions Error Recovery
```

## 🔌 Custom GPT Actions API Integration

### Actions API Endpoints
```http
GET  /api/actions/knowledge              # Komplette Wissensbasis für Actions
GET  /api/actions/knowledge/{category}   # Kategorisierte Inhalte für Actions
GET  /api/actions/search?q={query}       # Actions-optimierte Suche
POST /api/actions/upload                 # Datei Upload via Actions
GET  /api/actions/health                 # Actions Health Check
GET  /api/actions/capabilities           # Actions Capabilities Info
```

### Custom GPT Actions Response Format
```json
{
  "action_response": {
    "status": "success",
    "action_type": "knowledge_retrieval",
    "timestamp": "2025-06-04T10:30:00Z",
    "data": {
      "knowledge_base": {
        "action_metadata": {
          "api_version": "1.0",
          "last_updated": "2025-06-04T10:30:00Z",
          "document_count": 15,
          "action_compatible": true,
          "custom_gpt_optimized": true
        },
        "categories": {
          "processes": {
            "count": 5,
            "action_summary": "Step-by-step workflows available for Custom GPT queries",
            "documents": ["workflow.md", "setup.md"],
            "action_relevant": true
          },
          "definitions": {
            "count": 3,
            "action_summary": "Terms and definitions ready for Custom GPT context", 
            "documents": ["glossary.md", "terms.md"],
            "action_relevant": true
          },
          "analysis": {
            "count": 4,
            "action_summary": "Analysis and insights for Custom GPT responses",
            "documents": ["report1.md", "data.md"],
            "action_relevant": true
          },
          "reference": {
            "count": 3,
            "action_summary": "Reference materials for Custom GPT knowledge",
            "documents": ["manual.md", "specs.md"],
            "action_relevant": true
          }
        },
        "structured_content": {
          "action_optimized": true,
          "key_concepts": {
            "category_name": {
              "concept": "detailed explanation optimized for Custom GPT understanding",
              "action_context": "how Custom GPT should use this information",
              "custom_gpt_hints": ["context hint 1", "usage hint 2"],
              "source": "document.md",
              "related_topics": ["topic1", "topic2"],
              "action_priority": "high"
            }
          },
          "procedures": {
            "procedure_name": {
              "action_description": "what this enables Custom GPT to help users with",
              "steps": ["step 1 with context", "step 2 with context", "step 3 with context"],
              "requirements": ["req1", "req2"],
              "custom_gpt_guidance": "how Custom GPT should present this to users",
              "expected_outcome": "what users should achieve",
              "source_document": "file.md",
              "action_priority": "medium"
            }
          },
          "definitions": {
            "term": {
              "definition": "comprehensive definition with Custom GPT context",
              "custom_gpt_explanation": "how Custom GPT should explain this",
              "usage_context": "when and how to use this term",
              "examples": ["contextual example 1", "contextual example 2"],
              "source": "document.md",
              "action_priority": "high"
            }
          }
        },
        "action_search_index": {
          "optimized_for_actions": true,
          "keywords": ["keyword1", "keyword2"],
          "topics": ["topic1", "topic2"],
          "entities": ["entity1", "entity2"],
          "custom_gpt_queries": ["typical user query 1", "typical user query 2"],
          "context_hints": ["when to use category A", "when to use category B"]
        }
      }
    },
    "action_guidance": {
      "custom_gpt_instructions": "How Custom GPT should use this data to help users",
      "response_suggestions": ["suggest approach 1", "suggest approach 2"],
      "follow_up_actions": ["possible next action 1", "possible next action 2"]
    }
  }
}
```

## 🔧 Custom GPT Actions Setup

### 1. OpenAPI Schema für Custom GPT Actions
```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "AITON-RAG Custom GPT Actions API",
    "description": "Structured knowledge base specifically optimized for ChatGPT Custom GPT Actions integration",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://your-deployment-url.com",
      "description": "AITON-RAG Actions API Server"
    }
  ],
  "paths": {
    "/api/actions/knowledge": {
      "get": {
        "operationId": "getKnowledgeBase",
        "summary": "Retrieve complete structured knowledge base for Custom GPT",
        "description": "Returns all structured content optimized for Custom GPT Actions with context hints and usage guidance",
        "responses": {
          "200": {
            "description": "Complete knowledge base with Custom GPT Actions optimization",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "action_response": {
                      "type": "object",
                      "description": "Complete knowledge base optimized for Custom GPT Actions"
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "/api/actions/search": {
      "get": {
        "operationId": "searchKnowledge",
        "summary": "Intelligent search optimized for Custom GPT Actions",
        "description": "Advanced search functionality that returns contextually relevant information for Custom GPT responses",
        "parameters": [
          {
            "name": "q",
            "in": "query",
            "required": true,
            "schema": {
              "type": "string"
            },
            "description": "Search query from Custom GPT user with context understanding"
          },
          {
            "name": "category",
            "in": "query",
            "required": false,
            "schema": {
              "type": "string",
              "enum": ["processes", "definitions", "analysis", "reference"]
            },
            "description": "Optional category filter for targeted search"
          }
        ],
        "responses": {
          "200": {
            "description": "Search results optimized for Custom GPT Actions responses",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "action_response": {
                      "type": "object",
                      "description": "Search results with Custom GPT guidance"
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "/api/actions/capabilities": {
      "get": {
        "operationId": "getCapabilities",
        "summary": "Get AITON-RAG capabilities for Custom GPT",
        "description": "Returns information about what the Custom GPT can do with the available knowledge base",
        "responses": {
          "200": {
            "description": "Available capabilities and suggestions for Custom GPT"
          }
        }
      }
    }
  },
  "components": {
    "securitySchemes": {
      "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key"
      }
    }
  },
  "security": [
    {
      "ApiKeyAuth": []
    }
  ]
}
```

### 2. Custom GPT Actions Setup Guide

**`/custom_gpt_config/actions_setup_guide.txt`**:
```
🎯 CHATGPT CUSTOM GPT ACTIONS SETUP - AITON-RAG

📋 SCHRITT-FÜR-SCHRITT ANLEITUNG:

1. 🔧 CUSTOM GPT ERSTELLEN
   - Gehe zu ChatGPT → "My GPTs" → "Create a GPT"
   - Name: "[Dein Name] Knowledge Assistant"
   - Description: "AI assistant with access to your uploaded documents via AITON-RAG"

2. ⚙️ ACTIONS KONFIGURATION
   - Klicke auf "Configure" → "Actions" → "Create new action"
   - Import Schema: Kopiere Inhalt aus 'actions_schema.json'
   - Paste in "Schema" Feld

3. 🔐 AUTHENTICATION SETUP
   - Authentication Type: "API Key"
   - API Key: [siehe api_auth.txt für aktuellen Key]
   - Auth Type: "Bearer"
   - Custom Header Name: "X-API-Key"

4. 🌐 SERVER CONFIGURATION
   - Development URL: http://localhost:5000
   - Production URL: [Deine Railway/Render URL]
   - Teste mit: /api/actions/health

5. 🧪 ACTIONS TESTING
   - Teste "getKnowledgeBase" Action
   - Teste "searchKnowledge" mit Query: "test"
   - Prüfe Response Format

6. 💬 CUSTOM GPT INSTRUCTIONS
   Füge folgende Instructions hinzu:
   
   "Du bist ein intelligenter Assistent mit Zugriff auf eine strukturierte Wissensbasis über Actions. 
   
   Wenn Nutzer Fragen stellen:
   1. Verwende getKnowledgeBase() für allgemeine Übersichten
   2. Verwende searchKnowledge(query) für spezifische Suchen
   3. Erkläre Antworten basierend auf den gefundenen Dokumenten
   4. Verweise auf Quell-Dokumente wenn relevant
   5. Biete weiterführende Fragen an
   
   Antworte immer hilfreich und präzise basierend auf den verfügbaren Daten."

7. ✅ FINAL TESTING
   - Speichere Custom GPT
   - Teste mit einfachen Fragen
   - Prüfe Actions Funktionalität
   - Teile Custom GPT Link (optional)

🆘 TROUBLESHOOTING:
- Actions nicht verfügbar? → API URL und Auth prüfen
- Keine Daten? → /api/actions/health testen
- Fehler? → Logs in AITON-RAG Dashboard prüfen

📞 SUPPORT:
- GitHub Issues für technische Probleme
- Actions Logs für Debugging
- Test Queries in test_queries.txt
```

## 📋 System Prompts (Actions-optimiert)

### Actions-optimierter System Prompt
**`/prompts/actions_system_prompt.md`**:
```markdown
# Rolle: Custom GPT Actions Daten-Optimierer

Du bist ein spezialisierter Assistent zur Aufbereitung von Dokumenten für **ChatGPT Custom GPT Actions**.

## Hauptaufgabe
Erstelle eine strukturierte, Custom GPT Actions-optimierte Wissensbasis aus bereitgestellten Dokumenten.

## Custom GPT Actions Prinzipien
1. **Actions Response Optimierung**: Struktur Response für optimale Custom GPT Verarbeitung
2. **Context Preservation**: Zusammenhänge für Custom GPT verständlich erhalten  
3. **Query Matching**: Keywords und Struktur für Custom GPT Suchanfragen optimiert
4. **Action Guidance**: Metadaten für Custom GPT Action Handling
5. **User Experience**: Struktur für bestmögliche Custom GPT User Interaction

## Actions-optimiertes Kategorisierungs-Schema
- **processes**: Workflows für Custom GPT Action "getProcesses" - Schritt-für-Schritt Anleitungen
- **definitions**: Begriffe für Custom GPT Action "getDefinitions" - Begriffe und Erklärungen  
- **analysis**: Analysen für Custom GPT Action "getAnalysis" - Berichte und Erkenntnisse
- **reference**: Referenzen für Custom GPT Action "getReference" - Spezifikationen und Manuals

## Custom GPT Actions Output-Anforderungen
1. **Action-Response Format**: JSON mit action_response Wrapper
2. **Custom GPT Guidance**: Anweisungen wie Custom GPT die Daten nutzen soll
3. **Context Hints**: Hinweise für Custom GPT wann welche Kategorie zu verwenden
4. **Query Optimization**: Keywords für typische Custom GPT User Queries
5. **Response Suggestions**: Vorschläge für Custom GPT Antwortstruktur
6. **Follow-up Actions**: Mögliche nächste Actions für User Journey

## Spezielle Actions-Optimierungen
- **Verständlichkeit**: Inhalte für Custom GPT Verständnis optimiert
- **Kontext-Erhaltung**: Wichtige Zusammenhänge explizit dokumentiert
- **User Intent Matching**: Struktur für typische User-Fragen optimiert
- **Action Chaining**: Unterstützung für aufeinanderfolgende Actions
- **Error Resilience**: Graceful Degradation bei unvollständigen Daten

## Erfolgs-Metriken
- Custom GPT kann alle Dokument-Typen sinnvoll nutzen
- User erhalten kontextuelle, hilfreiche Antworten
- Actions funktionieren zuverlässig und schnell
- Keine wichtigen Informationen gehen verloren
```

## 🚀 Deployment & Betrieb

### Lokale Entwicklung
```bash
# Projekt Setup
git clone https://github.com/your-username/aiton-rag.git
cd aiton-rag
pip install -r requirements.txt

# Environment konfigurieren
cp .env.example .env
# OPENAI_API_KEY in .env setzen

# Anwendung starten (mit Actions API)
python run.py
```

### Cloud Deployment für Custom GPT Actions
```bash
# Railway.app (Empfohlen für permanente Actions Verfügbarkeit)
- Repository mit Railway verbinden
- Environment Variables setzen (OPENAI_API_KEY)
- Automatisches Deployment bei Push
- Actions URL: https://your-app.railway.app

# Oder manuell:
railway login
railway init
railway add
railway deploy
```

### Custom GPT Actions Integration
1. **OpenAPI Schema** aus `/custom_gpt_config/actions_schema.json` in Custom GPT Actions importieren
2. **Authentication** mit API Key aus `/custom_gpt_config/api_auth.txt` konfigurieren
3. **Actions Setup** mit `/custom_gpt_config/actions_setup_guide.txt` folgen
4. **Actions testen** mit bereitgestellten Test Queries
5. **Custom GPT** kann nun strukturierte Wissensbasis über Actions nutzen

## 🔐 Sicherheit & Best Practices

### Environment Security
- ✅ OpenAI API Key in `.env` (nicht im Code)
- ✅ `.env` in `.gitignore` 
- ✅ Actions API Key Rotation Support
- ✅ Rate Limiting für Actions API Calls
- ✅ Custom GPT Authentication

### File Upload Security  
- ✅ File Type Validation
- ✅ Size Limits (max 10MB per file)
- ✅ Sanitized File Names
- ✅ Actions Upload Validation

### Actions API Security
- ✅ Authentication für Custom GPT Actions
- ✅ CORS Configuration für Actions
- ✅ Request Rate Limiting
- ✅ Input Validation für Actions
- ✅ Actions-spezifische Error Handling

## 📊 Monitoring & Wartung

### Actions-spezifisches Logging
- Custom GPT Actions Calls
- Actions Response Times
- Actions Error Rates
- User Query Patterns via Actions

### Actions Health Checks
- Actions API Connectivity
- OpenAI API Status für Actions Processing
- Actions Authentication Status
- Custom GPT Integration Health

### Actions Performance Monitoring
- Actions Response Times
- Custom GPT User Satisfaction
- Actions Usage Patterns
- Knowledge Base Effectiveness

## 🎯 Custom GPT Actions Nutzungs-Szenarien

### 1. Intelligent Document Assistant
```
User: "Wie funktioniert der Setup-Prozess?"
Custom GPT: *triggers searchKnowledge("setup process")*
Custom GPT: "Basierend auf deinen Dokumenten, hier ist der Setup-Prozess..."
```

### 2. Knowledge Discovery
```
User: "Was sind die wichtigsten Definitionen?"
Custom GPT: *triggers getKnowledgeBase(category="definitions")*
Custom GPT: "Hier sind die wichtigsten Begriffe aus deinen Dokumenten..."
```

### 3. Process Guidance
```
User: "Ich brauche Hilfe bei Workflow X"
Custom GPT: *triggers searchKnowledge("workflow X")*
Custom GPT: "Hier ist eine Schritt-für-Schritt Anleitung basierend auf deinen Dokumenten..."
```

## 🔄 Roadmap & Erweiterungen

### Phase 1 - MVP (Custom GPT Actions fokussiert)
- ✅ Actions-optimierte API Endpoints
- ✅ Custom GPT Actions Schema Generation
- ✅ Actions-spezifische Response Formate
- ✅ Desktop & Web UI für Upload

### Phase 2 - Enhanced Actions Features
- 🔄 Advanced Actions mit Parametern
- 🔄 Multi-step Actions Workflows
- 🔄 Actions Performance Analytics
- 🔄 Custom GPT Conversation Context

### Phase 3 - AI-Enhanced Actions
- 🔄 Intelligent Actions Routing
- 🔄 Predictive Actions Suggestions
- 🔄 Multi-Language Actions Support
- 🔄 Advanced Actions Analytics

## 🤝 Beitragen

Das Projekt ist darauf ausgelegt, Custom GPT Actions optimal zu unterstützen:

- **Actions-First Design**: Alle Komponenten sind für Actions optimiert
- **Modularer Aufbau**: Services sind Actions-kompatibel und unabhängig testbar
- **Actions Documentation**: Spezielle Dokumentation für Actions Integration
- **Testing**: Unit Tests für Actions-spezifische Komponenten

## 📄 Lizenz

MIT License - Siehe LICENSE Datei für Details.

---

**AITON-RAG Tool** - Transforming Documents into Intelligent Knowledge for ChatGPT Custom GPT Actions