import React, { useState } from "react";

function DraftBox({ draft, setDraft, onSend, isDarkMode }) {
  const [isFocused, setIsFocused] = useState(false);

  const theme = {
    boxBg: isDarkMode ? "#111B21" : "#FFFFFF",
    inputBg: isDarkMode ? "#2A3942" : "#F8FAFC",
    border: isDarkMode ? "#2F3B43" : "#E2E8F0",
    textPrimary: isDarkMode ? "#E9EDEF" : "#0F172A",
    textMuted: isDarkMode ? "#8696A0" : "#64748B",
    badgeBg: isDarkMode ? "#182229" : "#EEF2FF",
    badgeText: isDarkMode ? "#00A884" : "#4F46E5",
    buttonBg: isDarkMode ? "#00A884" : "#0F172A",
    buttonHover: isDarkMode ? "#00c49a" : "#1E293B"
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        flex: 1,
        height: "100%",
        minHeight: 0,
        backgroundColor: theme.boxBg,
        boxSizing: "border-box",
        padding: "16px",
        gap: "12px",
        fontFamily:
          "Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, sans-serif"
      }}
    >
      {/* HEADER */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexShrink: 0
        }}
      >
        <span
          style={{
            fontSize: "11px",
            fontWeight: "600",
            color: theme.badgeText,
            backgroundColor: theme.badgeBg,
            padding: "4px 8px",
            borderRadius: "6px"
          }}
        >
          Suggested Reply Draft
        </span>

        <span style={{ fontSize: "11px", color: theme.textMuted }}>
          Enter = Send • Shift + Enter = New line
        </span>
      </div>

      {/* BODY (FULL HEIGHT TEXT AREA AREA) */}
      <div
        style={{
          flex: 1,
          minHeight: 0,
          display: "flex"
        }}
      >
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="AI response suggestion will appear here..."
          style={{
            width: "100%",
            height: "100%",
            flex: 1,
            minHeight: 0,

            padding: "14px",
            borderRadius: "10px",

            border: isFocused
              ? "1.5px solid #6366F1"
              : `1px solid ${theme.border}`,

            backgroundColor: isFocused
              ? isDarkMode
                ? "#2A3942"
                : "#FFFFFF"
              : theme.inputBg,

            color: theme.textPrimary,
            fontSize: "14px",
            lineHeight: "1.6",
            resize: "none",
            outline: "none",

            boxShadow: isFocused
              ? "0 0 0 3px rgba(99, 102, 241, 0.15)"
              : "none",

            transition: "all 0.15s ease"
          }}
        />

        <style>{`
          textarea::placeholder {
            color: ${isDarkMode ? "#8696A0" : "#CBD5E1"};
          }
        `}</style>
      </div>

      {/* FOOTER */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "10px",
          flexShrink: 0
        }}
      >
        <div style={{ fontSize: "12px", color: theme.textMuted }}>
          Tip: Press{" "}
          <kbd
            style={{
              background: isDarkMode ? "#2A3942" : "#F1F5F9",
              padding: "2px 6px",
              borderRadius: "4px"
            }}
          >
            Enter
          </kbd>{" "}
          to send 
        </div>

        <button
          onClick={onSend}
          disabled={!draft.trim()}
          style={{
            width: "100%",
            padding: "12px",
            borderRadius: "10px",
            border: "none",

            backgroundColor: draft.trim()
              ? theme.buttonBg
              : isDarkMode
              ? "#2F3B43"
              : "#E2E8F0",

            color: draft.trim() ? "#fff" : theme.textMuted,
            fontSize: "14px",
            fontWeight: "600",
            cursor: draft.trim() ? "pointer" : "not-allowed",

            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",

            transition: "all 0.15s ease"
          }}
          onMouseEnter={(e) => {
            if (draft.trim()) {
              e.currentTarget.style.backgroundColor = theme.buttonHover;
            }
          }}
          onMouseLeave={(e) => {
            if (draft.trim()) {
              e.currentTarget.style.backgroundColor = theme.buttonBg;
            }
          }}
        >
          Send Message
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
          >
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
    </div>
  );
}

export default DraftBox;