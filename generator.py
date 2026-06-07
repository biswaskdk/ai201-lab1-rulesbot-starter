from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)

# Chunks with a cosine distance above this are treated as too weakly related
# to the question and are dropped before building context (see spec:
# "Handling low-relevance chunks").
RELEVANCE_THRESHOLD = 0.7

# Shown when nothing relevant is found in the loaded rule books
# (see spec: "Fallback behavior").
FALLBACK_MESSAGE = "Unfortunately the question is Beyond the Game Rule's Database."


def _source_filename(game_name):
    """Reverse load_documents()'s filename -> game mapping.

    load_documents() derives the game name from the file via
    `filename.replace(".txt", "").replace("_", " ").title()`, so e.g.
    "ticket_to_ride.txt" -> "Ticket To Ride". This rebuilds the original
    filename so answers can cite the source document.
    """
    return game_name.lower().replace(" ", "_") + ".txt"


def generate_response(query, retrieved_chunks):
    """
    Generate a grounded answer from retrieved rule chunks.

    TODO — Milestone 3:

    `retrieved_chunks` is the list returned by retrieve(). Each item is a dict:
      - "text"     : the chunk text
      - "game"     : the game name
      - "distance" : similarity score (you can use this to filter weak matches)

    Before writing code, talk through these with your group:
      - How will you format the chunks into a context block for the prompt?
      - What instructions will stop the model from answering beyond what the
        rules say? (Grounding is the whole point — a confident wrong answer
        is worse than an honest "I don't know.")
      - How will you surface which game each answer comes from?

    Your response should:
      1. Answer using only the retrieved context — not the model's general knowledge
      2. Make clear which game the answer comes from
      3. Say so clearly when the answer isn't in the loaded rules

    Return the response as a plain string.
    """
    if not retrieved_chunks:
        return (
            "I couldn't find anything relevant in the loaded rule books. "
            "Try rephrasing your question — or check that your ingestion pipeline is working."
        )

    # Drop weakly-related chunks (lower distance = more similar for cosine).
    relevant_chunks = [
        c for c in retrieved_chunks if c["distance"] <= RELEVANCE_THRESHOLD
    ]
    if not relevant_chunks:
        return FALLBACK_MESSAGE

    # Format the surviving chunks as labeled rule excerpts separated by "---".
    # Each excerpt is tagged with its source filename (e.g. "monopoly.txt") so
    # the model can cite the original document rather than an in-text heading.
    # Distance scores are intentionally left out of the context.
    context = "\n---\n".join(
        f"Source: {_source_filename(c['game'])}\nGame: {c['game']}\n"
        f"Chunk:\n{c['text']}"
        for c in relevant_chunks
    )

    system_prompt = (
        "You are a board game rules assistant. Answer using only the rule text "
        "provided below. If the answer is not contained in the provided text, do "
        "not draw on outside knowledge or general board game knowledge — instead "
        f'respond with exactly: "{FALLBACK_MESSAGE}" '
        "Always cite the source document the answer comes from, using its "
        'filename exactly as given in the "Source:" field (e.g. "monopoly.txt"). '
        "Do not cite headings or titles found inside the rule text.\n\n"
        "Here are the retrieved rule chunks:\n\n"
        f"{context}"
    )

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
    )
    return response.choices[0].message.content
