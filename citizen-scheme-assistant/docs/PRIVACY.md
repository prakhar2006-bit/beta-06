# Privacy & Data Retention Policy

**Citizen Scheme Assistant (नागरिक योजना सहायक)**  
Document Version: 1.0.0

---

## 1. Core Privacy Philosophy: Zero Persistence

Citizens seeking government welfare are frequently requested to share highly sensitive socio-economic details: household income, caste category, land holdings, marital status, and age.

In rural and semi-urban India, citizens frequently interact with digital services via:
- A local Common Service Centre (CSC) or cyber café computer.
- A neighborhood grocery store (kirana) owner's phone.
- A shared family smartphone passed among multiple household members.

**Our Core Privacy Mandate**:  
> No citizen's personal data should ever remain accessible on the device or in any remote database after their screening session is finished.

---

## 2. What Is Stored, Where, and For How Long?

| Data Category | Stored Locally? | Stored on Server? | Retention Duration | Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Language Preference** (`hi`/`en`) | Yes | No | Session only | Ephemeral React State |
| **Socio-economic Answers** (Income, Land, Age) | Yes (Memory only) | No | Active session only | Volatile JavaScript memory |
| **Scheme Results & Document Checklist** | Yes (Memory only) | No | Active session only | Destroyed on wipe or tab close |
| **Personal Identifiers** (Name, Phone, Aadhaar) | **NEVER ASKED / NEVER STORED** | **NEVER** | 0 seconds | Explicitly prohibited by contract |
| **Analytics / Tracking Telemetry** | **NONE** | **NONE** | 0 seconds | No third-party tracking scripts |

---

## 3. Shared Phone Protection ("Someone Else's Phone")

When a citizen uses someone else's phone, our application guarantees:

1. **Zero Browser Autofill**: All question inputs have `autocomplete="off"`, `autocorrect="off"`, `autocapitalize="off"`, and `spellcheck="false"` to prevent browser keystroke history caching.
2. **No LocalStorage or Persistent Cookies**: The application uses strictly in-memory React state (or `sessionStorage` strictly cleared upon session completion). No keys are left in `window.localStorage`.
3. **One-Tap "Wipe & Exit" (डेटा मिटाएं और बाहर निकलें)**:
   - A persistent, high-contrast button is visible in the top header on every screen.
   - Clicking it triggers an immediate purge of in-memory data, clears browser history state, and redirects to the clean onboarding screen.
4. **Automatic Idle Inactivity Purge**:
   - If the device remains untouched for 5 minutes, the active session automatically resets.
   - If the user switches away from the browser tab (`visibilitychange` event listener fires), a configurable timer initiates automatic session wiping.
5. **Print & PDF Safety**:
   - The generated document checklist exports only the names of the schemes and the required paperwork.
   - The citizen's personal income and caste information are **not printed** on the document checklist to avoid disclosing private financial details if a printed sheet or downloaded PDF is left behind at a shop.

---

## 4. Verification: How We Know Nothing Is Left Behind

To demonstrate that nothing is left behind for the next user during audits and hackathon demos:
1. **Automated DevTools Verification**:
   - Check `localStorage.length === 0`.
   - Check `sessionStorage.length === 0`.
   - Check `document.cookie === ""`.
   - Check IndexedDB contains 0 databases.
2. **Form Cache Inspection**:
   - Tapping an input field on a fresh session displays 0 historical autocomplete suggestions.
3. **Network Tab Audit**:
   - Zero outbound requests sending payload data to external servers or analytics platforms.

