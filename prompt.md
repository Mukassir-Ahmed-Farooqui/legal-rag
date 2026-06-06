# OpenDoc Regression Fix Sprint

During manual validation, two regressions and one UX issue were discovered.

## Regression 1 — Fresh Chat Initialization Not Working

Expected behavior:

Login
→ Open /chat
→ Fresh chat created automatically
→ Empty workspace shown

Actual behavior:

Login
→ Open /chat
→ Previous latest chat loads automatically

The implementation described in the sprint report is not functioning correctly.

Investigate:

* App.jsx
* useChat.js
* Chat initialization flow

Determine:

1. Is a new chat actually being created?
2. Is it being overwritten by chat restoration logic?
3. Is the most recent chat being loaded after fresh chat creation?
4. Is there a race condition between chat creation and chat loading?

Fix so that:

* Users start in a fresh workspace
* Previous chats remain visible in sidebar
* Previous chats are not deleted

---

## Regression 2 — New Chat Button Fails

Expected:

Click "New Chat"
→ New chat created
→ Workspace switches to new chat

Actual:

Click "New Chat"
→ "Failed to start a new chat"

Investigate:

Frontend:

* useChat.js
* App.jsx
* API service

Backend:

* POST /api/v1/chats

Verify:

* Request is sent
* Payload is valid
* Backend responds successfully
* Frontend correctly handles response

Provide root cause and fix.

---

## UX Improvement — Sidebar Modernization

Current sidebar is fixed width.

Implement modern AI workspace behavior.

Requirements:

### Collapsible Sidebar

Add:

* Collapse button
* Expand button

User can fully hide chat sidebar.

### Resizable Sidebar

Allow drag resize.

Constraints:

* Minimum width: 220px
* Maximum width: 500px

Persist width in localStorage.

### Responsive Behavior

On smaller screens:

* Sidebar collapses automatically
* Workspace gains full width

---

## Validation

Provide:

[PASS] Fresh chat created on login
[PASS] Previous chats preserved
[PASS] New Chat button works
[PASS] Chat creation API works
[PASS] Sidebar collapsible
[PASS] Sidebar resizable
[PASS] Width persists after refresh
[PASS] No regressions introduced

Include root cause analysis for both chat regressions.
