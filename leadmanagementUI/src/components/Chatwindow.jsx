import React, { useEffect, useRef } from "react";

function ChatWindow({ messages, isDarkMode, activeLead }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth"
    });
  }, [messages]);

  const formatTime = (timeString) => {
    if (!timeString) return "";
    try {
      const date = new Date(timeString);
      if (!isNaN(date)) {
        return date.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          hour12: true
        });
      }
      const parts = timeString.split(" ");
      if (parts.length > 1) {
        let cleanTime = parts[1].substring(0, 5);
        if (timeString.toLowerCase().includes("pm") && !cleanTime.includes("PM")) {
          return `${cleanTime} PM`;
        } else if (timeString.toLowerCase().includes("am") && !cleanTime.includes("AM")) {
          return `${cleanTime} AM`;
        }
        return cleanTime;
      }
      return timeString.substring(0, 5);
    } catch {
      return "";
    }
  };

  const theme = {
    bg: isDarkMode ? "#0B141A" : "#EFEAE2",
    leadBubble: isDarkMode ? "#202C33" : "#FFFFFF",
    agentBubble: isDarkMode ? "#005C4B" : "#D9FDD3",
    text: isDarkMode ? "#E9EDEF" : "#111B21",
    secondary: isDarkMode ? "#8696A0" : "#667781",
    shadow: isDarkMode ? "0 1px 1px rgba(0,0,0,.2)" : "0 1px 1px rgba(11,20,26,.13)"
  };

  return (
    <div
      style={{
        height: "100%",
        overflowY: "auto",
        display: "flex",
        flexDirection: "column",
        background: theme.bg,
        padding: "16px 24px",
        gap: "8px",
        boxSizing: "border-box",
        fontFamily: "Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, sans-serif"
      }}
    >
      {/* LEAD PROFILE OVERVIEW CARD */}
      {activeLead && (
        <div
          style={{
            alignSelf: "center",
            background: isDarkMode ? "#1F2C34" : "#FFFFFF",
            padding: "14px 20px",
            borderRadius: "8px",
            minWidth: "280px",
            boxShadow: theme.shadow,
            marginBottom: "16px",
            textAlign: "center",
            border: isDarkMode ? "1px solid #2F3B43" : "1px solid #E2E8F0"
          }}
        >
          <div style={{ fontSize: "16px", fontWeight: "600", color: theme.text }}>
            {activeLead.name || activeLead.phone_number || "Active Lead Profile"}
          </div>
          
          {/* Robust structural fallbacks for schema mismatches */}
          <div style={{ marginTop: "6px", color: theme.secondary, fontSize: "13px" }}>
            📞 {activeLead.phone_number || activeLead.phone || "No Phone Registered"}
          </div>

          {(activeLead.email || activeLead.email_address) && (
            <div style={{ marginTop: "4px", color: theme.secondary, fontSize: "13px" }}>
              ✉️ {activeLead.email || activeLead.email_address}
            </div>
          )}
        </div>
      )}

      {/* HISTORICAL MESSAGE STREAM CONTAINER */}
      {messages.map((message, index) => {
        const isAgent = message.sender === "agent" || message.sender_type === "agent";

        return (
          <div
            key={index}
            style={{
              display: "flex",
              justifyContent: isAgent ? "flex-end" : "flex-start",
              width: "100%"
            }}
          >
            <div
              style={{
                maxWidth: "65%",
                background: isAgent ? theme.agentBubble : theme.leadBubble,
                color: theme.text,
                borderRadius: isAgent ? "8px 0px 8px 8px" : "0px 8px 8px 8px",
                padding: "6px 8px 6px 10px", 
                boxShadow: theme.shadow,
                display: "flex",
                flexDirection: "column",
                position: "relative",
                minWidth: "80px"
              }}
            >
              {!isAgent && (
                <div
                  style={{
                    fontSize: "12px",
                    fontWeight: "600",
                    color: isDarkMode ? "#53BDEB" : "#008069",
                    marginBottom: "2px",
                    userSelect: "none"
                  }}
                >
                  {activeLead?.name || "Lead"}
                </div>
              )}

              <div
                style={{
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                  fontSize: "14.2px",
                  lineHeight: "19px",
                  paddingRight: "50px" 
                }}
              >
                {message.message}
              </div>

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "flex-end",
                  gap: "3px",
                  fontSize: "11px",
                  color: theme.secondary,
                  alignSelf: "flex-end",
                  marginTop: "-4px",
                  marginLeft: "auto",
                  userSelect: "none",
                  whiteSpace: "nowrap"
                }}
              >
                <span>
                  {formatTime(message.time || message.created_at || message.timestamp)}
                </span>

                {isAgent && (
                  <span style={{ color: "#53BDEB", fontSize: "14px", fontWeight: "bold", lineHeight: 1 }}>
                    ✓✓
                  </span>
                )}
              </div>
            </div>
          </div>
        );
      })}

      <div ref={bottomRef} style={{ height: "1px" }} />
    </div>
  );
}

export default ChatWindow;