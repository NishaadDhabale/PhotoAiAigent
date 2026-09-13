# 📸 PhotoAgent — Local-First AI Photo Organizer

## 📖 Description

PhotoAgent is a **local-first AI-powered photo organization and search application** designed to turn an ordinary folder of images into an intelligent, searchable personal photo library.

Instead of treating photos as simple files, PhotoAgent builds a structured understanding of the collection:

```text
SSD / Photo Folder
        │
        ▼
   Photo Scanner
        │
        ▼
 Metadata Extraction
        │
        ├── filename
        ├── dimensions
        ├── date
        ├── camera
        └── GPS
        │
        ▼
      SQLite
        │
        ├───────────────┐
        ▼               ▼
   Face System      Image Embeddings
        │               │
        ▼               ▼
 People / Groups     ChromaDB
        │               │
        └───────┬───────┘
                ▼
          Search System
                │
                ▼
         LangChain Agent
                │
                ▼
          React Frontend
```

The project combines **traditional structured data systems** with modern AI techniques:

- SQLite for factual and structured photo metadata
- InsightFace for local face detection and face embeddings
- Agglomerative clustering for grouping similar faces
- OpenCLIP / MobileCLIP2 for image and text embeddings
- ChromaDB for vector similarity search
- LangChain for an AI agent that orchestrates search tools
- Gemini for the natural-language agent layer
- FastAPI for the backend API
- React + Vite for the frontend
- Framer Motion and Lucide React for UI polish

The system is intentionally designed around a **local-first privacy model**. The photos themselves are kept on the user's machine and are accessed from their local filesystem. The application uses local ML models for image and face understanding. An online reverse-geocoding service is used only for GPS-coordinate-to-place conversion when location metadata is available.

---

## 🎯 Project Goals

PhotoAgent was designed around several goals.

### 1. Turn folders into a searchable photo library

A normal photo folder might contain:

```text
IMG_001.jpg
IMG_002.jpg
DSC_4521.jpg
Screenshot.png
IMG_2022.jpg
```

PhotoAgent transforms those files into records with structured metadata such as:

```text
Photo ID
Filename
Path
Dimensions
Date taken
Camera
Latitude
Longitude
Location
```

---

### 2. Search using natural language

The user should not need to remember exact filenames.

Examples:

```text
Find photos from 2022
```

```text
Show photos of Nisha
```

```text
Find beach photos
```

```text
Show photos from Mumbai
```

```text
Find my photos from 2023
```

The search system combines structured database queries with semantic similarity search when appropriate.

---

### 3. Understand people in photos

The face pipeline can detect faces, generate face embeddings, and group visually similar faces into person groups.

The UI then exposes these groups through the **People** page.

The user can:

- browse detected people
- rename a person
- select multiple face groups
- mark multiple groups as the same person
- open photos belonging to a person
- open the local file location for a photo
- inspect photo metadata

---

### 4. Provide safe photo organization

PhotoAgent includes a file organization system that can propose moving photos into organized year-based folders.

The system is designed to avoid destructive behavior.

The organization pipeline follows:

```text
Preview
  ↓
Safety checks
  ↓
User confirmation
  ↓
Move files
  ↓
Update SQLite
  ↓
Update vector metadata
```

The planner is read-only.

The executor only runs when explicitly requested.

---

### 5. Provide an AI assistant over the photo library

The LangChain agent acts as a conversational interface to PhotoAgent.

Instead of exposing raw database queries to the user, the agent chooses from application tools such as:

```text
Structured photo search
Semantic image search
Hybrid search
Person search
Location search
Metadata retrieval
Organization planning
Local photo access
```

The agent is intentionally constrained to the application data and tool outputs instead of directly manipulating arbitrary files.

---

# 🧭 Table of Contents

1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [Architecture](#-architecture)
4. [Technology Stack](#-technology-stack)
5. [Project Structure](#-project-structure)
6. [Core Data Model](#-core-data-model)
7. [Photo Processing Pipeline](#-photo-processing-pipeline)
8. [Metadata Extraction](#-metadata-extraction)
9. [Location Detection](#-location-detection)
10. [Face Detection and People](#-face-detection-and-people)
11. [Image Embeddings](#-image-embeddings)
12. [Vector Database](#-vector-database)
13. [Structured Search](#-structured-search)
14. [Semantic Search](#-semantic-search)
15. [Hybrid Search](#-hybrid-search)
16. [LangChain Agent](#-langchain-agent)
17. [Result Normalization](#-result-normalization)
18. [Photo Access](#-photo-access)
19. [Duplicate Detection](#-duplicate-detection)
20. [Safe Organization](#-safe-organization)
21. [Frontend](#-frontend)
22. [Pages and User Experience](#-pages-and-user-experience)
23. [API Documentation](#-api-documentation)
24. [Environment Variables](#-environment-variables)
25. [Installation](#-installation)
26. [Running the Backend](#-running-the-backend)
27. [Running the Frontend](#-running-the-frontend)
28. [Indexing Photos](#-indexing-photos)
29. [Testing](#-testing)
30. [Current Dataset and Validation](#-current-dataset-and-validation)
31. [Privacy Model](#-privacy-model)
32. [Safety Design](#-safety-design)
33. [Important Implementation Decisions](#-important-implementation-decisions)
34. [Known Limitations](#-known-limitations)
35. [Future Improvements](#-future-improvements)
36. [Troubleshooting](#-troubleshooting)
37. [GitHub Checklist](#-github-checklist)
38. [Contributing](#-contributing)
39. [Author](#-author)

---

# 🧠 Overview

PhotoAgent is not a single AI model.

It is an application made by combining multiple systems.

```text
                PHOTO FILE
                    │
                    ▼
              Scanner
                    │
                    ▼
             Metadata Layer
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       SQLite              Image/Face
       Records              Analysis
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
             Face System               CLIP
                 │                         │
                 ▼                         ▼
          People / Groups              ChromaDB
                 │                         │
                 └────────────┬────────────┘
                              ▼
                            Search
                              │
                              ▼
                         Agent Layer
                              │
                              ▼
                           FastAPI
                              │
                              ▼
                         React UI
```

The important architectural idea is that **AI is not responsible for everything**.

A query such as:

```text
Show photos taken in 2022
```

is better answered by SQLite.

A query such as:

```text
Show photos containing a beach
```

is better suited to semantic image search.

A query involving both:

```text
Show beach photos from 2022
```

can be handled through a hybrid pipeline that combines structured and semantic constraints.

---

# ✨ Key Features

## Photo indexing

PhotoAgent scans supported image formats recursively:

- JPG
- JPEG
- PNG
- WEBP
- HEIC
- HEIF

The scanner records the discovered files and sends them into the metadata pipeline.

---

## EXIF metadata extraction

The application extracts:

- filename
- absolute/relative path
- file size
- image width
- image height
- date taken
- camera/device
- GPS latitude
- GPS longitude

GPS data is converted from EXIF degrees/minutes/seconds representation into decimal coordinates.

---

## Reverse geocoding

When GPS coordinates are available, PhotoAgent can convert:

```text
latitude + longitude
```

into a human-readable location.

Example conceptual result:

```json
{
  "city": "Mumbai",
  "state": "Maharashtra",
  "country": "India",
  "country_code": "in"
}
```

Location metadata contains information about how the value was obtained and a confidence score.

---

## Local face detection

InsightFace is used to detect faces locally.

For each detected face, the system stores information such as:

- bounding box
- detection confidence
- face embedding
- person group assignment

The system does not require the user to upload photographs to a face-recognition service.

---

## Face grouping

Face embeddings are compared using cosine similarity.

Similar embeddings are clustered into groups.

The result can look conceptually like:

```text
Face 1 ─┐
Face 4 ─┼── Person Group A
Face 7 ─┘

Face 2 ─┐
Face 8 ─┼── Person Group B
Face 9 ─┘
```

The current implementation uses agglomerative clustering with cosine distance and a configured threshold.

The groups are intentionally treated as **provisional AI-generated groups**, since clustering quality depends on the images and threshold.

---

## Image semantic search

PhotoAgent uses MobileCLIP2-S0 with the `dfndr2b` pretrained checkpoint.

The same embedding space is used for:

```text
Image → vector
Text  → vector
```

This makes natural-language image retrieval possible.

Conceptually:

```text
"beach"

   ↓

text embedding

   ↓

vector similarity search

   ↓

photos whose embeddings are close
```

---

## Vector database

ChromaDB stores image embeddings persistently.

The current vector collection is:

```text
photo_embeddings
```

The configured similarity metric is cosine similarity.

The vector metadata contains enough information to map a vector back to its local photo record.

---

## Structured search

SQLite is used for factual filters.

Supported search concepts include:

- person
- year
- start date
- end date
- location
- camera
- filename

Structured filtering is dynamic, so multiple filters can be combined.

---

## Hybrid search

Hybrid search combines:

```text
SQLite structured filtering
+
semantic similarity
```

This prevents the vector database from being used for queries that are already easier to answer through ordinary database conditions.

---

## LangChain agent

The application includes a LangChain agent backed by Gemini.

The agent is instructed to:

- prefer local tools
- choose structured search for factual conditions
- choose semantic search for visual concepts
- use hybrid search when both kinds of constraints matter
- preserve conversational context
- avoid inventing photo results
- use returned tool results as the source of truth
- avoid arbitrary destructive file operations

The agent communicates with PhotoAgent's own tools rather than directly querying arbitrary application internals.

---

## Photo viewer

The photo viewer provides:

- enlarged photo preview
- previous/next controls
- keyboard navigation
- Escape-to-close
- metadata display
- local file-location opening

The file-location action opens Windows Explorer and selects the underlying image file.

---

## People management

The People page supports:

- viewing people groups
- renaming a person
- selecting groups
- merging groups
- viewing a person's photos
- opening the location associated with a photo when coordinates exist

---

## Duplicate detection

Duplicate detection works in two layers.

### Exact duplicates

SHA-256 hashes are used to detect byte-for-byte duplicate files.

### Near duplicates

MobileCLIP image embeddings are compared to detect visually similar images.

Near-duplicate detection is intentionally **review-only**.

The application does not automatically delete detected duplicates.

---

## Safe organization

Organization is deliberately split into two stages.

### Planner

The planner calculates what would happen.

It identifies:

- source
- destination
- conflicts
- already-organized files
- missing files
- safe operations

### Executor

The executor performs only approved operations.

It also updates:

- SQLite photo paths
- vector database metadata

Rollback logic is included for failures occurring after a file move but before metadata updates are completed.

---

# 🏗️ Architecture

## High-level system

```text
┌─────────────────────────────┐
│        Local Photo Files    │
│          SSD / Disk         │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│        Photo Scanner        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      Metadata Extractor     │
│                             │
│ EXIF / dimensions / dates   │
│ camera / GPS                │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│           SQLite            │
│                             │
│ photos / faces / people     │
└──────┬───────────────┬──────┘
       │               │
       │               │
       ▼               ▼
┌──────────────┐   ┌───────────────┐
│ Face System  │   │ Image Encoder │
│ InsightFace  │   │  MobileCLIP2  │
└──────┬───────┘   └───────┬───────┘
       │                   │
       ▼                   ▼
┌──────────────┐   ┌───────────────┐
│ Face Groups  │   │   ChromaDB     │
└──────┬───────┘   └───────┬───────┘
       │                   │
       └─────────┬─────────┘
                 ▼
        ┌──────────────────┐
        │  Search Service  │
        └────────┬─────────┘
                 ▼
        ┌──────────────────┐
        │ LangChain Agent  │
        └────────┬─────────┘
                 ▼
        ┌──────────────────┐
        │    FastAPI       │
        └────────┬─────────┘
                 ▼
        ┌──────────────────┐
        │ React / Vite UI  │
        └──────────────────┘
```

---

# 🛠️ Technology Stack

## Backend

- **Python**
- **FastAPI**
- **Uvicorn**
- **SQLite**
- **Pillow**
- **exifread**
- **geopy**
- **InsightFace**
- **ONNX Runtime GPU**
- **PyTorch**
- **OpenCLIP / MobileCLIP2**
- **ChromaDB**
- **scikit-learn**
- **LangChain**
- **langchain-core**
- **langchain-google-genai**

## Frontend

- **React**
- **Vite**
- **JavaScript / JSX**
- **React Router**
- **Framer Motion**
- **Lucide React**
- Custom CSS

## AI / ML

### Face understanding

```text
InsightFace
```

### Image-text semantic understanding

```text
MobileCLIP2-S0
dfndr2b
```

### Agent

```text
LangChain
+
Gemini
```

### Vector retrieval

```text
ChromaDB
```

---

# 📂 Project Structure

The project is organized into separate backend and frontend concerns.

```text
PhotoAgent/
│
├── app/
│   │
│   ├── api/
│   │   ├── main.py
│   │   ├── models.py
│   │   └── routes.py
│   │
│   ├── agent/
│   │   ├── agent_runtime.py
│   │   ├── conversation.py
│   │   ├── result_manager.py
│   │   └── result_normalizer.py
│   │
│   ├── database.py
│   ├── duplicate_detector.py
│   ├── duplicate_service.py
│   ├── face_detection.py
│   ├── face_grouping.py
│   ├── image_embeddings.py
│   ├── indexer.py
│   ├── location.py
│   ├── metadata.py
│   ├── organization_executor.py
│   ├── organization_planner.py
│   ├── organization_service.py
│   ├── people_management.py
│   ├── photo_access.py
│   ├── photo_result.py
│   ├── photo_results.py
│   ├── result_extractor.py
│   ├── result_pipeline.py
│   ├── scanner.py
│   ├── search.py
│   ├── semantic_search.py
│   ├── vector_store.py
│   │
│   ├── main.py
│   │
│   └── test_*.py
│
├── frontend/
│   │
│   ├── src/
│   │   ├── api/
│   │   │   └── photoApi.js
│   │   │
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── photos/
│   │   │   ├── search/
│   │   │   └── ...
│   │   │
│   │   ├── pages/
│   │   │   ├── PhotosPage.jsx
│   │   │   ├── PeoplePage.jsx
│   │   │   ├── TimelinePage.jsx
│   │   │   ├── PlacesPage.jsx
│   │   │   ├── AgentPage.jsx
│   │   │   ├── DuplicatesPage.jsx
│   │   │   └── OrganizationPage.jsx
│   │   │
│   │   ├── App.jsx
│   │   └── ...
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── .env
│
├── data/
│   ├── photos.db
│   └── chroma/
│
├── Images/
│   └── local photo dataset
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

> The exact local repository may contain additional helper files and test modules. The structure above represents the major application components and their responsibilities.

---

# 🗄️ Core Data Model

PhotoAgent uses SQLite as the factual source of truth.

## Photos table

The `photos` table stores information such as:

```text
id
filename
path
size_bytes
width
height
date_taken
camera
latitude
longitude
location_name
location_source
location_confidence
```

The `path` column is unique.

This allows a scanned photo to be updated rather than duplicated when the scanner is run again.

---

## Faces table

The faces table contains:

```text
id
photo_id
face_index
x
y
width
height
confidence
embedding
person_group_id
```

The relationship is:

```text
Photo
  │
  ├── Face 1
  ├── Face 2
  └── Face 3
```

Face rows reference their parent photo.

Deleting a photo can therefore cascade to its faces.

---

## People table

The people table stores:

```text
id
name
person_group_id
```

A person group is a system-generated grouping of visually similar face embeddings.

A user can rename a group without modifying the underlying image files.

---

# 🔄 Photo Processing Pipeline

The main processing pipeline can be summarized as:

```text
1. Scan files
       ↓
2. Extract metadata
       ↓
3. Save metadata in SQLite
       ↓
4. Resolve GPS location
       ↓
5. Detect faces
       ↓
6. Save face embeddings
       ↓
7. Group faces
       ↓
8. Generate image embeddings
       ↓
9. Index embeddings in ChromaDB
       ↓
10. Expose data through FastAPI
       ↓
11. Display through React
```

The stages are intentionally separated so that each system can be tested independently.

---

# 🗂️ Metadata Extraction

Metadata processing uses Pillow and EXIF parsing.

The system reads:

```text
Filename
Path
File size
Width
Height
Date
Camera
GPS
```

GPS values can appear in EXIF as degrees/minutes/seconds with directional indicators.

The parser converts them into decimal coordinates.

Conceptually:

```text
EXIF GPS
   ↓
DMS coordinates
   ↓
decimal latitude/longitude
   ↓
reverse geocoder
   ↓
city/state/country
```

---

# 📍 Location Detection

Location information can originate from GPS metadata.

The location fields are designed to preserve both the human-readable location and provenance.

Example:

```text
location_name:
Mumbai, Maharashtra, India

location_source:
gps

location_confidence:
1.0
```

When GPS information is missing, PhotoAgent does not pretend to know the location.

Future versions can introduce local/offline inference, but that is intentionally separate from the current GPS-based pipeline.

---

# 👤 Face Detection and People

## Face detection

InsightFace is used to detect faces.

The detector returns:

```text
number of faces
bounding boxes
confidence
face embeddings
```

The embeddings are stored as binary data in SQLite.

---

## Face grouping

The grouping stage loads the face embeddings and clusters them.

The current implementation uses:

```text
AgglomerativeClustering
metric = cosine
linkage = average
distance threshold = 0.40
```

Conceptually, the system considers embeddings close when their cosine similarity is sufficiently high.

The resulting group IDs are then stored against the individual face rows.

---

## Why grouping is separate from detection

Detection answers:

```text
Is there a face?
Where is it?
```

Recognition/grouping answers:

```text
Which detected faces appear to belong together?
```

Keeping these stages separate makes the system easier to debug and improve.

---

## People management

Renaming does not change a face embedding.

Merging groups works conceptually as:

```text
Group A
Group B
Group C

      ↓ user confirms

Group A
├── faces from A
├── faces from B
└── faces from C
```

The merge updates the database group assignments and removes redundant person records.

The underlying images are not deleted or modified.

---

# 🧮 Image Embeddings

PhotoAgent uses MobileCLIP2-S0.

The configured pretrained checkpoint is:

```text
dfndr2b
```

The embedding dimension is:

```text
512
```

Embeddings are normalized before similarity search.

The model supports two important operations:

```text
embed_image(image)
embed_text(text)
```

This makes it possible to compare:

```text
text embedding
        ↕
image embedding
```

in the same semantic space.

---

# 🧠 Vector Database

ChromaDB is used as the persistent vector store.

Current collection:

```text
photo_embeddings
```

Distance metric:

```text
cosine
```

The vector record is associated with the corresponding SQLite photo ID.

The architecture is:

```text
SQLite
  │
  │ photo ID
  ▼
ChromaDB
  │
  │ embedding
  ▼
semantic similarity
```

SQLite remains the source of truth for factual metadata.

ChromaDB exists for vector retrieval.

---

# 🔎 Structured Search

Structured search operates directly against SQLite.

Examples:

```text
year = 2022
```

```text
camera = "Motorola ..."
```

```text
location = "Mumbai"
```

```text
filename contains "IMG"
```

Date filters can be expressed as:

```text
start_date
end_date
```

Person filters can connect photo records to face/person-group information.

Structured search is preferred whenever the query can be answered using exact metadata.

---

# 🧠 Semantic Search

Semantic search converts the user's text query into a CLIP text embedding.

For example:

```text
"sunset at the beach"
```

becomes a numerical vector.

ChromaDB then finds image vectors that are close to the query vector.

This means the user does not need exact textual tags inside the photo metadata.

---

# 🔀 Hybrid Search

Some searches require both semantic and structured conditions.

Example:

```text
Find beach photos from 2022
```

The system can treat this as:

```text
Structured condition:
date between 2022-01-01 and 2022-12-31

+

Semantic condition:
photo is similar to "beach"
```

This is more powerful than forcing every query through a single retrieval method.

---

# 🤖 LangChain Agent

The LangChain agent is the conversational orchestration layer.

Its job is not to replace the search system.

Instead:

```text
User language
      ↓
   Agent
      ↓
Choose tool
      ↓
Search / metadata / organization
      ↓
Tool result
      ↓
Agent explanation
```

---

## Agent responsibilities

The agent can:

- interpret user requests
- decide which search method is appropriate
- preserve previous conversation context
- call PhotoAgent tools
- explain results
- avoid fabricating photo information

---

## Tool selection philosophy

### Structured query

Use when the user requests exact information:

```text
Show photos from 2022.
```

### Semantic search

Use when the request is visual/conceptual:

```text
Find photos of beaches.
```

### Hybrid search

Use when both are required:

```text
Find beach photos from 2022.
```

---

## Gemini integration

Gemini is used for natural-language reasoning and response generation through LangChain.

The actual photo files remain under the local application's file system.

The current agent is fundamentally a tool-oriented text agent; it is not a general-purpose service that uploads the user's entire photo library.

The API key is stored in an environment variable and should never be committed to GitHub.

---

# 🧹 Result Normalization

AI tool responses can arrive in multiple formats.

Examples include:

```text
Python dictionaries
JSON strings
lists
Gemini content blocks
LangChain ToolMessage content
```

PhotoAgent therefore separates:

```text
result extraction
```

from:

```text
result normalization
```

The normalized internal representation is based around `PhotoResult`.

This allows the frontend to receive predictable photo objects regardless of how the agent produced the original tool response.

---

# 🖼️ Photo Result Model

The photo result abstraction contains fields such as:

```text
id
filename
path
date_taken
camera
latitude
longitude
location_name
similarity
```

The abstraction is useful because it separates:

```text
database representation
```

from:

```text
UI representation
```

---

# 📂 Photo Access

PhotoAgent provides a controlled local photo-access layer.

It validates that:

1. the photo ID exists
2. the stored path exists
3. the path points to an actual file

The system can then:

```text
Open photo
```

or:

```text
Open file location
```

On Windows, the file-location operation launches Explorer and selects the corresponding local file.

---

# 🔁 Duplicate Detection

## Exact duplicates

Exact duplicates are identified with SHA-256:

```text
file
 ↓
SHA-256
 ↓
hash
```

If two files have the same hash, they are byte-for-byte identical.

---

## Near duplicates

Near duplicates use MobileCLIP image similarity.

Conceptually:

```text
Photo A → embedding A
Photo B → embedding B

cosine similarity(A, B)

         ↓

high similarity

         ↓

possible near duplicate
```

The configured threshold is:

```text
0.92
```

Near duplicates are presented for review.

PhotoAgent does not automatically delete them.

---

# 📁 Safe File Organization

The organization feature is deliberately conservative.

## Planner

The planner produces a proposal such as:

```text
Photo
   ↓
Year detected: 2022
   ↓
Destination:
Organized/2022/filename.jpg
```

Before execution it checks:

- file exists
- destination is available
- destination conflicts
- duplicate destination paths
- already organized state

---

## Executor

Execution requires an explicit confirmation flag.

The executor:

```text
1. preflights the complete operation
2. moves only safe items
3. updates SQLite
4. updates Chroma metadata
5. rolls back where possible if metadata updates fail
```

This design prevents the AI agent from silently restructuring the user's filesystem.

---

# 🎨 Frontend

The frontend is a Vite React application.

The UI is organized around dedicated pages and reusable components.

---

# 🧭 Pages and User Experience

## Photos

The main photo library.

Capabilities:

- browse all photos
- semantic/natural-language search
- open photos
- next/previous photo navigation
- display metadata
- open file location

The photo grid uses responsive layouts and compact thumbnails so the page behaves more like a photo-library application than a portfolio grid.

---

## People

The People page displays detected person groups.

Actions include:

```text
Rename
Merge
Open person
View photos
Open photo
```

Photos belonging to a person can be opened in the common photo viewer.

---

## Timeline

The Timeline page organizes photos chronologically.

The UI presents photos grouped by date/year/month where metadata is available.

Photos without usable dates are handled separately as undated content.

---

## Places

The Places page is intended to provide location-oriented browsing.

Location data originates from stored GPS metadata and reverse-geocoding results.

---

## Agent

The Agent page provides the natural-language interface.

Example interactions:

```text
User:
Show me photos of Nisha.
```

```text
Agent:
I found 2 matching photos.
```

The returned photos can then be opened in the shared viewer.

---

## Duplicates

The Duplicates page presents:

- exact duplicate groups
- near-duplicate candidates
- similarity scores

The UI is review-oriented.

---

## Organization

The Organization page is intentionally separate from the normal photo browsing experience.

It can show:

```text
Preview
Safe files
Conflicts
Already organized
Missing files
```

and then provide an explicit execution flow.

---

# 🔌 API Documentation

The FastAPI backend exposes application functionality to the React frontend.

The exact request/response models are defined in:

```text
app/api/models.py
```

and the endpoint implementations are defined in:

```text
app/api/routes.py
```

## Health

```http
GET /api/health
```

Used to verify that the API is alive.

---

## Photos

```http
GET /api/photos
```

Returns the indexed photo collection.

---

## Photo image

```http
GET /api/photos/{photo_id}/image
```

Returns the local image content for a photo.

---

## Open photo location

```http
POST /api/photos/{photo_id}/open-location
```

Opens the local Windows Explorer location containing the requested photo.

---

## People

```http
GET /api/people
```

Returns the current people/group information.

---

## Rename person

```http
PATCH /api/people/{person_id}
```

Request:

```json
{
  "name": "Nisha"
}
```

---

## Merge people

```http
POST /api/people/merge
```

Request:

```json
{
  "group_ids": [1, 2],
  "target_group_id": 1
}
```

---

## Timeline

```http
GET /api/timeline
```

Returns the timeline-oriented photo information used by the frontend.

---

## Places

```http
GET /api/places
```

Returns location-oriented information.

---

## Semantic / structured search

Search endpoints are exposed through the API layer and internally dispatch to the structured, semantic, or hybrid search pipeline.

The core implementation lives in the search-related backend modules.

---

## Agent

```http
POST /api/agent/chat
```

The agent request contains a user message and optional conversation context.

The response can contain:

```text
assistant answer
+
normalized photo results
```

The frontend uses the returned photo IDs to construct image URLs.

---

## Duplicates

```http
GET /api/duplicates
```

Returns duplicate analysis including:

```text
exact duplicate groups
near duplicates
threshold
photo metadata
```

---

## Organization preview

```http
POST /api/organization/preview
```

Returns the proposed organization plan.

---

## Organization execute

```http
POST /api/organization/execute
```

Executes a confirmed safe organization plan.

Execution is intentionally separated from planning.

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

Example:

```env
GOOGLE_API_KEY=your_google_api_key
```

Frontend environment:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Never commit secrets.

The root `.gitignore` should include:

```gitignore
.env
.env.*
```

---

# ⚙️ Installation

The following instructions assume a fresh clone.

## Prerequisites

Install:

- Git
- Python 3.x
- Node.js
- npm

An NVIDIA GPU is useful for accelerating some ML workloads, but the architecture should not assume that every user has one.

---

## Clone

```bash
git clone <your-github-repo-url>
cd PhotoAgent
```

---

## Backend environment

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows Git Bash:

```bash
source .venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

> The current development environment used during implementation contains a CUDA-enabled PyTorch installation and GPU-enabled ONNX Runtime. Dependency versions should be kept consistent when publishing the repository.

---

# ▶️ Running the Backend

From:

```text
PhotoAgent/app
```

run:

```bash
python -m uvicorn api.main:app --reload
```

Or, depending on the local project entry point:

```bash
python main.py
```

The FastAPI development server normally runs at:

```text
http://127.0.0.1:8000
```

---

# ▶️ Running the Frontend

From:

```text
PhotoAgent/frontend
```

install dependencies:

```bash
npm install
```

Run Vite:

```bash
npm run dev
```

The frontend will display a local development URL, commonly similar to:

```text
http://localhost:5173
```

---

# 🔄 Indexing Photos

The main indexing pipeline can be triggered from the backend application.

The pipeline updates SQLite records using the photo path as a unique identifier.

This means rescanning the same photo does not simply create another photo record.

The embedding index is also incremental.

Before embedding a photo, the vector index checks whether its photo ID is already present.

Conceptually:

```text
Photo ID
   ↓
Already in Chroma?
   │
 ┌─┴─┐
Yes  No
 │    │
skip embed
```

This reduces unnecessary embedding computation.

---

# 🧪 Testing

The project contains targeted test modules for different subsystems.

Examples include:

```text
test_result_pipeline.py
test_agent_api_results.py
test_photo_results.py
test_photo_open.py
test_duplicate_detector.py
test_duplicates_api.py
test_organization_planner.py
test_organization_executor.py
test_organization_api.py
```

Additional unit and integration tests may exist in the repository.

---

## Running tests

From the `app` directory:

```bash
python test_result_pipeline.py
```

or run an individual test module:

```bash
python test_duplicate_detector.py
```

For projects with pytest configured:

```bash
pytest
```

---

# ✅ Current Dataset and Validation

During development, the test collection contained:

```text
29 photos
23 detected faces
17 face groups
```

Person data included one named person group and multiple unidentified groups.

Date distribution included both dated and undated photos.

The actual dataset is small and serves primarily as a development and validation collection.

---

## Face pipeline validation

A deterministic test image used during development successfully produced:

```text
7 detected faces
```

The complete dataset produced:

```text
23 detected faces
```

---

## Vector indexing validation

The image-embedding index was successfully populated for:

```text
29 photos
```

The incremental indexing path subsequently reported the indexed photos as already present rather than recomputing them.

---

## Duplicate validation

The development dataset produced:

```text
Exact duplicates: 0
Near duplicates: 0
```

with the current near-duplicate threshold of:

```text
0.92
```

---

## Organization validation

The organization planner produced:

```text
29 photos
29 safe
0 conflicts
0 already organized
0 missing
```

The organization feature was subsequently tested with the UI.

---

# 🔒 Privacy Model

Privacy is a central design principle of PhotoAgent.

## Photos remain local

The application's photo files are stored and accessed from the user's local filesystem.

The face and image understanding pipelines run locally.

---

## Local face processing

Face detection and face embedding generation are performed by local models rather than by uploading the photo collection to a third-party face-recognition provider.

---

## Local semantic image processing

The image embeddings are generated using a locally loaded MobileCLIP2 model.

The image vectors are then stored in local ChromaDB storage.

---

## Network use

There are two important categories of external communication:

### Reverse geocoding

When GPS coordinates are present, reverse geocoding may use an external geocoding service to convert coordinates into a place name.

In that case:

```text
GPS coordinates
```

may leave the computer.

The actual image does not need to be uploaded for GPS reverse geocoding.

### Gemini agent

Gemini is used as the natural-language agent layer.

The current agent architecture sends the user's conversational request and tool-related text to Gemini as needed.

The photo-management system itself remains grounded in locally stored records and locally generated search results.

Users deploying the project should review their chosen model/provider policies before using sensitive data with external services.

---

# 🛡️ Safety Design

PhotoAgent deliberately avoids treating an AI agent as an unrestricted filesystem administrator.

The organization architecture requires:

```text
Plan
 ↓
Review
 ↓
Explicit confirmation
 ↓
Execute
```

This is particularly important for photo collections because accidental moves or deletion operations can affect hundreds or thousands of files.

---

## No automatic deletion

Duplicate detection is review-only.

A similarity score does not automatically authorize deletion.

---

## No silent organization

The planner does not modify the filesystem.

The executor requires explicit confirmation.

---

## Path validation

Photo access validates that the file:

```text
exists
```

and:

```text
is actually a file
```

before opening it.

---

# 🧩 Important Implementation Decisions

## Why SQLite + ChromaDB?

The two databases solve different problems.

### SQLite

Best for:

```text
facts
filters
relationships
metadata
```

### ChromaDB

Best for:

```text
embeddings
similarity
semantic retrieval
```

Therefore:

```text
SQLite = factual source of truth
ChromaDB = semantic retrieval index
```

---

## Why not only use a vector database?

A vector database is unnecessary for queries such as:

```text
Find photos from 2022
```

SQLite can answer this exactly and efficiently.

Vector similarity is valuable for:

```text
Find sunset photos
```

Using both systems gives PhotoAgent the strengths of both.

---

# 🧠 AI vs Non-AI Responsibilities

A major design principle is to avoid using AI where deterministic code is better.

## Deterministic systems

Use:

```text
SQLite
EXIF parser
file scanner
SHA-256
path validation
organization safety checks
```

for factual operations.

## ML systems

Use:

```text
InsightFace
MobileCLIP2
clustering
vector similarity
```

for visual understanding.

## LLM system

Use:

```text
LangChain + Gemini
```

for natural-language reasoning and tool selection.

This layered design is more reliable than trying to solve every problem with one LLM.

---

# ⚠️ Known Limitations

## Face grouping can chain incorrectly

Agglomerative clustering can create groups through a chaining effect.

For example:

```text
A similar to B
B similar to C
```

does not always mean:

```text
A is truly the same person as C
```

The current grouping threshold is therefore a practical heuristic rather than a guarantee of identity accuracy.

A future version should support better representative selection, centroid-based thresholds, manual review, or graph-based grouping.

---

## Location inference is currently GPS-driven

The location system is strongest when photos contain GPS coordinates.

Photos without GPS do not automatically receive a guaranteed location.

Future versions could introduce:

- offline visual geolocation
- local scene/place inference
- clustering by nearby coordinates
- user corrections

---

## Duplicate detection is conservative

A threshold of `0.92` is intentionally review-oriented.

Changing the threshold can dramatically change the number of near-duplicate candidates.

---

## Small validation dataset

The current development dataset contains only a few dozen photos.

Performance and retrieval quality should be evaluated again on much larger collections.

---

## Gemini dependency

The agent depends on an external model provider.

This introduces:

- API-key configuration
- network dependency
- provider quota/rate limitations
- provider-side model availability considerations

The underlying photo intelligence remains locally oriented, but the LLM agent layer is not completely offline.

---

# 🚧 Future Improvements

## Better people recognition

Potential improvements:

```text
Face centroid profiles
Representative face selection
Better threshold calibration
Manual face labeling
Person confirmation
Undo merge
Split incorrect groups
```

---

## Better semantic search

Potential improvements:

```text
Re-ranking
Query expansion
Multi-query retrieval
Better embeddings
Metadata-aware semantic ranking
Similarity explanations
```

---

## Better location intelligence

Potential improvements:

```text
Offline reverse geocoder
Visual geolocation
Place clustering
Map-based browsing
Location confidence visualization
```

---

## Better duplicate handling

Potential improvements:

```text
Duplicate review UI
Keep/delete recommendations
Image quality comparison
Resolution comparison
File-size comparison
Burst-photo detection
```

---

## More organization modes

Future organization strategies could include:

```text
Year
Year / Month
Location
Person
Event
Camera
Custom user-defined rules
```

---

## Advanced agent capabilities

Potential future agent commands:

```text
Organize my 2022 photos
```

```text
Show all photos of Nisha taken in Mumbai
```

```text
Find photos from my trip and group them by location
```

```text
Show me possible duplicate photos
```

```text
Explain why these photos are related
```

The safety model should remain unchanged:

```text
inspect → propose → confirm → modify
```

---

# 🐛 Troubleshooting

## Backend does not start

Check that the correct Python environment is active:

```bash
which python
```

On Windows Git Bash, confirm it points to the intended Python environment.

Then:

```bash
python -m uvicorn api.main:app --reload
```

---

## Frontend cannot reach backend

Check:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

and confirm the backend is running.

---

## Images do not appear

Check:

1. the photo exists
2. the SQLite path is correct
3. the `/api/photos/{photo_id}/image` endpoint is reachable
4. the frontend API base URL is correct

---

## Image location cannot open

The local file-location feature currently depends on Windows Explorer.

The supported path is:

```text
Windows
    ↓
Explorer
    ↓
/select, <photo path>
```

---

## Search returns unexpected results

Determine which search path is being used.

For exact conditions:

```text
SQLite
```

For visual concepts:

```text
CLIP + ChromaDB
```

For both:

```text
hybrid search
```

Semantic retrieval should be evaluated using realistic queries because an embedding model measures similarity rather than exact truth.

---

## Chroma telemetry warnings

Development logs may contain telemetry-related warnings from the Chroma stack.

These warnings are unrelated to core photo indexing when vector operations themselves continue to work.

They should be treated separately from actual indexing failures.

---

# 📦 Runtime Data

The following directories contain generated or local data and generally should **not** be committed to GitHub:

```text
data/photos.db
data/chroma/
Images/
.env
```

A recommended `.gitignore` includes:

```gitignore
.env
.env.*
.venv/
__pycache__/
*.pyc

data/photos.db
data/chroma/

Images/

frontend/node_modules/
frontend/dist/
```

The exact ignore policy may be adjusted depending on whether a small sanitized sample dataset is intentionally included.

---

# 📊 Performance Considerations

PhotoAgent performs several computationally expensive operations:

```text
Face detection
Face embedding generation
Image embedding generation
Vector indexing
Semantic queries
```

The development machine used during implementation includes:

```text
Intel Core i5-12500H
16 GB RAM
NVIDIA RTX 3050 Laptop GPU
4 GB VRAM
```

CUDA-enabled inference is used when available.

Because VRAM is limited, models should be loaded carefully and batch sizes should remain conservative.

The architecture should remain capable of operating on CPU-only machines, although inference will generally be slower.

---

# 🧪 Development Workflow

A typical development loop is:

```text
1. Change backend/frontend code
        ↓
2. Start backend
        ↓
3. Start frontend
        ↓
4. Test feature manually
        ↓
5. Run targeted tests
        ↓
6. Run production build
        ↓
7. Commit
```

Frontend build validation:

```bash
npm run build
```

Backend targeted tests:

```bash
python test_<feature>.py
```

---

# 🌳 Suggested Git Workflow

```bash
git status
```

Review changes:

```bash
git diff
```

Add files:

```bash
git add .
```

Commit:

```bash
git commit -m "feat: improve photo organization"
```

Push:

```bash
git push origin main
```

A cleaner alternative is feature branches:

```bash
git checkout -b feature/semantic-search
```

---

# 🚀 GitHub Publication Checklist

Before publishing PhotoAgent:

## Remove secrets

Confirm no API keys are committed.

Search for:

```text
GOOGLE_API_KEY=
```

or any actual secret values.

---

## Remove local personal data

Do not commit:

```text
data/photos.db
data/chroma/
Images/
```

unless they are intentionally sanitized test assets.

---

## Verify `.gitignore`

Ensure:

```text
.env
.venv
node_modules
database files
vector database files
local photo directory
```

are excluded.

---

## Verify README

The repository should contain:

```text
README.md
```

with:

- project description
- architecture
- setup
- features
- API information
- testing
- privacy notes
- limitations
- future work

---

## Verify frontend build

```bash
cd frontend
npm run build
```

The production build should succeed before pushing.

---

## Verify backend

```bash
cd app
python -m uvicorn api.main:app --reload
```

Then verify the API health endpoint.

---

# 📈 Project Status

## Completed

### Core data pipeline

- [x] Photo scanning
- [x] EXIF metadata extraction
- [x] GPS parsing
- [x] Reverse geocoding
- [x] SQLite storage

### Face intelligence

- [x] Local face detection
- [x] Face embeddings
- [x] Face grouping
- [x] People database
- [x] Person renaming
- [x] Person merging

### Image intelligence

- [x] MobileCLIP2 image embeddings
- [x] Text embeddings
- [x] ChromaDB vector store
- [x] Incremental indexing
- [x] Semantic search
- [x] Hybrid search

### Agent

- [x] LangChain integration
- [x] Gemini integration
- [x] Tool-based search
- [x] Conversation context
- [x] Result extraction
- [x] Result normalization
- [x] Agent API

### File features

- [x] Local photo opening
- [x] Open file location
- [x] Exact duplicate detection
- [x] Near duplicate detection
- [x] Safe organization planner
- [x] Safe organization executor

### Frontend

- [x] Photos page
- [x] People page
- [x] Timeline page
- [x] Places page
- [x] Agent page
- [x] Duplicates page
- [x] Organization page
- [x] Shared photo viewer
- [x] Responsive layouts
- [x] Compact photo grids
- [x] Navigation
- [x] Animated UI elements

---

# ❌ Removed / Abandoned Features

A handwritten-photo detection feature was explored during development but was intentionally abandoned.

The project therefore does **not** currently rely on a handwritten detector for its main functionality.

This was a design choice to avoid keeping a feature that did not provide sufficient value relative to its complexity and model/API requirements.

---

# 🧭 Development Roadmap

The project originally followed this architectural progression:

```text
1. Photo Scanner
        ↓
2. Metadata Extraction
        ↓
3. Location Detection
        ↓
4. Face Detection
        ↓
5. Face Embeddings
        ↓
6. Person Grouping
        ↓
7. Image Embeddings
        ↓
8. Vector Database
        ↓
9. Semantic Search
        ↓
10. LangChain Agent
        ↓
11. Safe File Organization
        ↓
12. UI / Polish
```

This ordering is intentional.

Higher-level systems depend on lower-level capabilities.

For example:

```text
LangChain Agent
      ↓
needs search tools
      ↓
search tools
      ↓
need SQLite + vector retrieval
      ↓
vector retrieval
      ↓
needs image embeddings
```

Building the system bottom-up makes it easier to reason about failures.

---

# 🧠 Why This Is a Strong AI Project

PhotoAgent demonstrates more than simply calling an LLM API.

It combines several important AI engineering concepts.

## Embeddings

Both images and text are converted into numerical representations.

---

## Vector search

Embeddings are indexed in ChromaDB and retrieved using similarity.

---

## Computer vision

InsightFace performs face detection and produces face embeddings.

---

## Clustering

Face embeddings are grouped using unsupervised clustering.

---

## Retrieval

The system uses both structured and semantic retrieval.

---

## Agent orchestration

LangChain decides which application tool should be used for a natural-language request.

---

## AI + software engineering

The project also demonstrates:

```text
database design
API development
frontend development
file-system safety
testing
error handling
result normalization
```

That combination is central to the design of PhotoAgent.

---

# 🔍 Example End-to-End Query

Consider:

```text
Find beach photos from 2022.
```

A conceptual execution path is:

```text
User
 │
 ▼
React Agent UI
 │
 ▼
FastAPI
 │
 ▼
LangChain Agent
 │
 ├── understands "beach"
 │
 └── understands "2022"
 │
 ▼
Hybrid Search
 │
 ├── SQLite
 │     └── date = 2022
 │
 └── ChromaDB
       └── similarity to "beach"
 │
 ▼
Normalized Photo Results
 │
 ▼
FastAPI response
 │
 ▼
React
 │
 ▼
Photo cards
```

The key design principle is that the LLM does not need to know how SQLite or ChromaDB works internally.

It only needs to choose the appropriate application tool.

---

# 🔬 Example Face Pipeline

For a single photo:

```text
image.jpg
   │
   ▼
InsightFace
   │
   ├── face 1
   │     ├── bounding box
   │     ├── confidence
   │     └── embedding
   │
   ├── face 2
   │     ├── bounding box
   │     ├── confidence
   │     └── embedding
   │
   └── face 3
         ├── bounding box
         ├── confidence
         └── embedding
```

After processing the complete collection:

```text
23 detected faces
        ↓
17 provisional groups
```

The People page converts these groups into a human-friendly interface.

---

# 🔬 Example Semantic Search Pipeline

Query:

```text
"sunset over the ocean"
```

becomes:

```text
text
 ↓
MobileCLIP text encoder
 ↓
512-dimensional normalized vector
 ↓
ChromaDB similarity search
 ↓
photo IDs
 ↓
SQLite metadata lookup
 ↓
PhotoResult objects
 ↓
React UI
```

This separates:

```text
semantic retrieval
```

from:

```text
metadata retrieval
```

which keeps the data model clean.

---

# 🧱 Design Principles

The project follows these principles:

### Local first

Keep data on the user's machine wherever possible.

### Explicit over implicit

Do not silently change files.

### Deterministic over AI when possible

Use SQL for facts and AI for semantic understanding.

### Modular

Each major pipeline stage exists as a separate component.

### Testable

Feature-specific tests validate individual subsystems.

### Source of truth

Database/tool results are treated as authoritative rather than allowing the language model to invent records.

### Incremental indexing

Avoid recomputing expensive embeddings unnecessarily.

### Review before modification

AI may recommend filesystem changes, but user confirmation is required before execution.

---

# 🤝 Contributing

Contributions should preserve the project's local-first and safety-oriented design.

Suggested workflow:

```bash
git checkout -b feature/my-feature
```

Implement the change.

Run targeted tests.

Run the frontend build:

```bash
npm run build
```

Review the diff:

```bash
git diff
```

Commit:

```bash
git commit -m "feat: describe change"
```

Push:

```bash
git push origin feature/my-feature
```

Then open a Pull Request.

---

# 📄 License

No license has been formally specified in the current project documentation.

Before publishing the repository publicly, add a license appropriate for the intended use.

For example:

```text
MIT License
```

if the project is intended to be permissively reusable.

---

# 👤 Author

**Nishaad Dhabale**

---

# 📌 Project Summary

PhotoAgent is a full-stack AI photo-management application combining:

```text
Python
+
FastAPI
+
SQLite
+
InsightFace
+
MobileCLIP2
+
ChromaDB
+
LangChain
+
Gemini
+
React
+
Vite
```

Its architecture intentionally separates:

```text
structured metadata
```

from:

```text
semantic representations
```

and:

```text
language-model reasoning
```

resulting in a system that is easier to test, reason about, and extend.

The long-term vision is a private personal photo assistant capable of understanding:

```text
WHO
WHERE
WHEN
WHAT
SIMILARITY
ORGANIZATION
```

while keeping the actual photo collection under the user's control.

---

# ⭐ One-Line Description

> **PhotoAgent is a local-first AI photo organizer that uses computer vision, multimodal embeddings, vector search, structured metadata, and a LangChain agent to make personal photo collections searchable, understandable, and safely organizable.**
