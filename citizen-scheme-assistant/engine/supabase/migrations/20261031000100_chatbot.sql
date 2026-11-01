-- Chatbot conversation persistence grounded in scheme_catalog architecture.
-- Supports user and ephemeral session conversation histories with cascading cleanup.

CREATE TABLE IF NOT EXISTS scheme_catalog.chat_conversations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id text,
    user_id text,
    title text NOT NULL CHECK (btrim(title) <> ''),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS scheme_catalog.chat_messages (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id uuid NOT NULL REFERENCES scheme_catalog.chat_conversations(id) ON DELETE CASCADE,
    role text NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content text NOT NULL,
    structured_payload jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Performance and retrieval indexes
CREATE INDEX IF NOT EXISTS idx_chat_conversations_session ON scheme_catalog.chat_conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_conversations_user ON scheme_catalog.chat_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation ON scheme_catalog.chat_messages(conversation_id, created_at ASC);

-- These tables are part of the private application store, not the public
-- catalogue. Keep the same fail-closed RLS posture as the catalogue tables;
-- backend access must be added through an explicitly reviewed server role.
ALTER TABLE scheme_catalog.chat_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE scheme_catalog.chat_messages ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON scheme_catalog.chat_conversations, scheme_catalog.chat_messages FROM PUBLIC;

