# OpenDoc Rebranding & UX Sprint

I've successfully completed the final sprint to modernize the OpenDoc application and address the strict UX validation points. All "legal" terminology has been removed and replaced with document-agnostic language, and the "Corpus-wide" and "0 selected" states have been meticulously handled.

## Key Changes

### 1. Document Selection Safety (Backend)
- Updated `chats.py` and `query.py` to prevent any possibility of a silent corpus-wide leak.
- If a user explicitly submits a query with `selected_doc_ids=[]` but they possess documents in their workspace, the backend now forcefully rejects the request with a `400 Bad Request`.
- This ensures users must actively "Select All" or choose specific documents, removing the dangerous default fallback.

### 2. Fresh Workspace Initialization (Frontend)
- Updated `App.jsx` and `useChat.js` so that when a user logs in, the application inspects their most recent chat.
- If the chat has 0 messages, it reuses it.
- If it contains messages, it automatically generates a fresh, clean chat session.
- During this fresh creation, the application defaults to selecting **all** available documents in the workspace, ensuring the user is immediately ready to query their library.

### 3. Rebranding & Empty States
- Removed all "Legal/Contract" terms from the interface. 
- Modified `UploadZone.jsx` to list "Research Papers", "Technical Documentation", "Reports", etc., instead of "NDAs" and "Vendor Contracts".
- `ChatArea.jsx` now uses neutral document intelligence examples and prompts the user to "Upload your first document to start asking questions." when the workspace is empty.
- `DocumentsPanel.jsx` features "Select All" and "Deselect All" capabilities above the document list.
- `InputBar.jsx` now features a dynamic rotating placeholder with general analysis examples, disables input when 0 documents exist, and natively presents the `⚠ No documents selected` warning when documents exist but the selection is empty.

### 4. Progress Tracking
- The loading pipeline (`ThinkingIndicator.jsx`) now reads: "Searching documents..." -> "Retrieving context..." -> "Synthesizing response...".

## Verification Checklist
- [x] Backend returns 400 for empty selection (when docs exist).
- [x] Rebranding fully applied (OpenDoc, Document Workspace).
- [x] Fresh Chat generated on login.
- [x] Scope indicators correctly render "All documents selected", "0 documents", or "⚠ No documents selected".
- [x] Zero legal language remains in the UI.

The OpenDoc UX modernization is now complete!
