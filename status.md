# Citation Fix Status

## What's Wrong
The citation system has several interconnected bugs making evidence panels disconnected from answers and missing key data (score, preview text).

## Changes Made

### ✅ `src/models/responses.py` — Fixed
Added `score` and `preview` fields to the `Citation` Pydantic model (previously only had `document`, `page`, `section`).

### ✅ `src/workflows/legal_graph.py` — Fixed
- `citation_node` now only returns chunks actually cited via `[N]` references in the answer text (was dumping ALL retrieved chunks blindly)
- Fixed O(n²) `.index()` bug — replaced with `enumerate()`
- Added fallback: if answer has zero `[N]` citations, returns all chunks so user still sees evidence
- Added `_build_prompt_template()` to route COMPARE queries to a separate prompt

### ✅ `src/prompts/legal_qa.py` — Fixed
Added `LEGAL_COMPARE_PROMPT` with side-by-side comparison format requiring visible evidence quotes per document.

### ✅ `src/api/routes/chats.py` — Fixed
Both locations now pass `score` and `preview`:
- **Line 188**: `get_chat_detail` route — now includes `score=c.get("score")` and `preview=c.get("preview")`
- **Line 633**: `create_message` route — same fix applied

### ✅ `src/api/routes/query.py` — Fine
Passes raw dicts directly through `QueryResponse`, Pydantic handles serialization.

### ✅ `frontend/src/components/chat/MessageBubble.jsx` — Fine
Already reads `cit.score` and `cit.preview` — just needs backend to actually send them.

## Remaining
1. ~~Fix `chats.py` line 188~~ ✅
2. ~~Fix `chats.py` line 633~~ ✅
3. Test end-to-end
