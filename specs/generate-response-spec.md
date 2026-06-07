# Spec: `generate_response()`

**File:** `generator.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user query and a list of retrieved rule chunks, generate a response that directly answers the question using only the retrieved text as context. The response must be grounded — it should not draw on the model's general knowledge of board games, only on what was retrieved.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's original question |
| `retrieved_chunks` | `list[dict]` | Ranked list of chunks from `retrieve()`, each with `"text"`, `"game"`, and `"distance"` |

**Output:** `str`

A plain string containing the response to show the user. The response should:
- Answer the question using only the retrieved rule text
- Identify which game the answer comes from
- Acknowledge clearly when the answer is not found in the loaded rules

Returns a fallback string (not an error) when `retrieved_chunks` is empty.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Context formatting

*How will you format the retrieved chunks before passing them to the LLM? Describe the structure — not the code. Consider: will you label chunks by game? Include distance scores? Separate chunks with delimiters?*

```
Format the retrieved chunks as a list of labeled rule excerpts. For each chunk, show the game name followed by the chunk text, and separate chunks with a delimiter like "---". Do not include distance scores.
```

---

### System prompt — grounding instruction

*Write the exact system prompt instruction you will use to prevent the model from answering beyond the retrieved text. This is the most important design decision in this function.*

```
Answer using only the rule text provided below. If the answer is not contained in the provided text, say so explicitly and do not draw on outside knowledge or general board game knowledge.
```

---

### System prompt — citation instruction

*Write the exact instruction you will use to tell the model to identify which game its answer comes from.*

```
Always cite the game document from which the answer comes.
```

---

### Fallback behavior

*What should the response say when the answer isn't found in the loaded rule books? Write the exact fallback message.*

```
Unfortunately the question is Beyond the Game Rule's Database.
```

---

### Handling low-relevance chunks

*`retrieved_chunks` may include chunks with high distance scores (weak relevance). Will you filter these out before building context, pass them all in, or handle them another way? What are the tradeoffs?*

```
I will filter out chunks with distance above 0.7 before building context. The tradeoff is that some queries may then return no answer and trigger the fallback response.
```

---

### Message structure

*Describe how you will structure the messages list for the API call — what goes in the system message vs. the user message?*

```
System message:
Answer using only the rule text provided below. If the answer is not contained in the provided text, say so explicitly and do not draw on outside knowledge. Always cite the game document from which the answer comes.

Here are the retrieved rule chunks:

Game: Catan
Chunk:
When a 7 is rolled, no resources are produced. Every player with more than 7 resource cards must discard half.

---
Game: Monopoly
Chunk:
Houses and hotels may be bought only when you own all properties in a color group.

Question: {user query}
```

---

## Implementation Notes

*Fill this in after implementing and testing.*

**Test query and response:**

```
Query: how do i win Monopoly?
Response: According to the Monopoly rules, "The last player remaining after all others have gone bankrupt wins the game." (Source: monopoly.txt)
Correctly grounded? [yes / no] Yes
Cited the right game? [yes / no] Yes
```

**One thing you changed from your original spec after seeing the actual output:**

```
I expected the model to paraphrase or expand on the rules more, but the output was mostly the retrieved rule text with only light rephrasing and minimal additional content.
```
