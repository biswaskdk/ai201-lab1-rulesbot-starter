# Spec: `retrieve()`

**File:** `retriever.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user's natural language query, find the most relevant chunks from the vector store using semantic similarity search. Return them ranked by relevance so that `generate_response()` can use them as context.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's natural language question |
| `n_results` | `int` | Maximum number of chunks to return (default: `N_RESULTS` from `config.py`) |

**Output:** `list[dict]`

Each dict in the returned list must contain exactly these keys:

| Key | Type | Description |
|-----|------|-------------|
| `"text"` | `str` | The chunk text |
| `"game"` | `str` | The game name this chunk came from |
| `"distance"` | `float` | Cosine distance score — lower means more similar to the query |

Results should be ordered from most to least relevant (lowest to highest distance). Returns an empty list `[]` if the collection contains no documents.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Query approach

*Describe how you will use `_collection.query()` to find relevant chunks. What arguments will you pass, and why?*

```
Use `_collection.query()` with:
- query_texts=[query]
- n_results=n_results
- include=["documents", "metadatas", "distances"]

This returns the nearest chunks for the user’s natural-language query. The raw chunk text is in `documents`, the chunk source game is in `metadatas`, and the similarity score is in `distances`. Since we only pass one query, we will unpack the result with `[0]`.
```

---

### Return structure

*Sketch out what one item in your return list looks like as a concrete example. Where does each field come from in the query results?*

```
Example:
{
    "text": "When a 7 is rolled, no resources are produced. Every player with more than 7 resource cards must discard half.",
    "game": "Catan",
    "distance": 0.15
}
Where each field comes from in _collection.query() results:
"text" ← query_results["documents"][0][i] (the raw chunk text)
"game" ← query_results["metadatas"][0][i]["game"] (extracted from the metadata dict)
"distance" ← query_results["distances"][0][i] (cosine distance score)
```

---

### Handling the nested result structure

*`_collection.query()` returns nested lists. Describe what index you need to access to get the actual list of results for a single query, and why the nesting exists.*

```
The [0] index is needed because _collection.query() always returns nested lists—one result set per query. Since you only pass one query, you unpack it with [0].
```

---

### Relevance threshold

*Will you filter out results above a certain distance score, or return all `n_results` regardless of how relevant they are? What are the tradeoffs of each approach?*

```
I will filter out results above 0.5 distance score to ensure relevance. The tradeoff of this approach is that sometimes answer might not be in the retrieved set.
```

---

### Edge cases

*How does your implementation behave when: (a) the collection is empty, (b) the query matches no chunks well, (c) the query matches chunks from multiple games?*

```
(a) collection is empty
  - If `_collection.count() == 0`, return []

(b) the query matches no chunks well
  - Query still returns the top nearest chunks.
  - Apply the distance threshold of 0.5 and return only chunks below that score.
  - If no results meet the threshold, return []

(c) the query matches chunks from multiple games
  - Return them all, ranked by distance.
  - Preserve `"game"` metadata so later code can know which game each result came from.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**Test query and top result returned:**

```
Query: What happens when you roll a 7?
Top result game: Catan
Distance score: 0.466
Does it make sense? [yes / no / explain]
yes — the top chunk should describe the 7-roll rule and the score is a strong semantic match.
```

**One thing about the query results that surprised you:**

```
The returned chunks can include multiple games when the query is generic, so preserving `"game"` metadata is important for filtering or attribution later.
```
