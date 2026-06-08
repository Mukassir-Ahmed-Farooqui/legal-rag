# Project Status

> Last updated: 2026-06-08

---

## Citation System — All Fixed ✅

| File | Status | What |
|------|--------|------|
| `src/models/responses.py` | ✅ | Added `score` + `preview` to Citation model |
| `src/workflows/legal_graph.py` | ✅ | Only returns cited chunks, fixed O(n²) bug, added compare prompt routing |
| `src/prompts/legal_qa.py` | ✅ | Added `LEGAL_COMPARE_PROMPT`, escaped `{{}}` to fix KeyError |
| `src/api/routes/chats.py` | ✅ | Both Citation() constructors now pass `score` + `preview` |
| `frontend/src/components/chat/MessageBubble.jsx` | ✅ | Overflow fixes: `min-w-0`, `overflow-hidden`, `break-words` |

---

## Auth System — All Fixed ✅

| # | Severity | Issue | Status |
|---|----------|-------|--------|
| 1 | 🔴 Critical | CORS: `allow_credentials=True` + `allow_origins=["*"]` violates spec | ✅ |
| 2 | 🔴 Critical | 401 interceptor breaks login errors, redirects to non-existent `/login` | ✅ |
| 3 | 🔴 Critical | `login()` calls `logout()` on error destroying existing sessions | ✅ |
| 4 | 🟠 High | No password strength validation | ✅ |
| 5 | 🟠 High | ProtectedRoute only checks localStorage, not token expiry | ✅ |
| 6 | 🟠 High | TOCTOU race in `/register` → 500 on duplicate email | ✅ |
| 7 | 🟠 High | No rate limiting on login/register | ✅ |
| 8 | 🟡 Medium | `isLoading` goes false before profile fetch completes | ✅ |
| 9 | 🟡 Medium | `decodeToken` fabricates full_name from email prefix | ✅ |
| 10 | 🟡 Medium | Register auto-login failure destroys session silently | ✅ |
| 11 | 🟡 Medium | PATCH /me full_name missing max_length → potential 500 | ✅ |
| 12 | 🟢 Low | No-op `except JWTError: raise` in jwt.py | ✅ |
| 13 | 🟢 Low | Redundant `sub` check in dependencies.py | ✅ |
| 14 | 🟢 Low | No debounce on submit button | ✅ |
| 15 | 🟢 Low | Missing cleanup in useEffect initAuth | ✅ |

---

## Files Changed

| File | What |
|------|------|
| `src/api/main.py` | CORS: `["*"]` → `["http://localhost:5173"]` |
| `src/auth/schemas.py` | Password `min_length=8`, `full_name` max_length=255 |
| `src/api/routes/auth.py` | TOCTOU IntegrityError catch, slowapi rate limiting (5/min) |
| `src/auth/jwt.py` | Removed no-op try/except |
| `src/auth/dependencies.py` | Removed redundant `sub` check |
| `frontend/src/services/api.js` | 401 interceptor skips auth endpoints |
| `frontend/src/context/AuthContext.jsx` | login no longer calls logout, unmount cleanup, no fake full_name |
| `frontend/src/components/ProtectedRoute.jsx` | Token expiry check added |
| `frontend/src/components/auth/AuthModal.jsx` | Password minLength=8, double-submit guard |
