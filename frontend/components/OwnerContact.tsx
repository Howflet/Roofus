"use client";

import { useState, useCallback } from "react";
import type { BuildingProperties } from "@/lib/types";
import styles from "./OwnerContact.module.css";

interface OwnerContactProps {
  building: BuildingProperties;
}

export default function OwnerContact({ building }: OwnerContactProps) {
  const [toast, setToast] = useState<string | null>(null);
  const [message, setMessage] = useState(
    `Hi ${building.owner_name}, I'm interested in exploring the rooftop at ${building.address} for an urban agriculture project. The building scored ${Math.round(building.score)}/100 on our viability assessment. I'd love to discuss leasing opportunities. Would you be open to a conversation?`
  );
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  const copyToClipboard = useCallback(async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setToast(`${label} copied!`);
      setTimeout(() => setToast(null), 1700);
    } catch {
      // fallback
      setToast("Failed to copy");
      setTimeout(() => setToast(null), 1700);
    }
  }, []);

  const handleSend = useCallback(async () => {
    setSending(true);
    // Simulate API call
    await new Promise((r) => setTimeout(r, 1200));
    setSending(false);
    setSent(true);
  }, []);

  if (sent) {
    return (
      <div className={styles.successContainer}>
        <div className={styles.successCheck}>
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <circle
              cx="24"
              cy="24"
              r="20"
              stroke="#10B981"
              strokeWidth="3"
              fill="none"
              className={styles.checkCircle}
            />
            <path
              d="M15 24l6 6 12-12"
              stroke="#10B981"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
              fill="none"
              className={styles.checkMark}
            />
          </svg>
        </div>
        <h3 className={styles.successTitle}>Message Sent!</h3>
        <p className={styles.successText}>
          We&apos;ve notified the owner of {building.address}. They&apos;ll receive your message
          via email.
        </p>
        <button
          className="btn btn-outline"
          style={{ width: "100%", marginTop: 16 }}
          onClick={() => setSent(false)}
        >
          Close
        </button>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h3 className="text-label" style={{ marginBottom: 16 }}>
        Owner Contact Info
      </h3>

      {/* Owner name */}
      <div className={styles.ownerName}>{building.owner_name}</div>

      {/* Mailing address */}
      <div className={styles.address}>
        <span className={styles.icon}>📬</span>
        <span>{building.owner_address}</span>
      </div>

      {/* Email */}
      <div className={styles.contactRow}>
        <span className={styles.icon}>📧</span>
        <a
          href={`mailto:${building.owner_email}`}
          className={styles.contactLink}
        >
          {building.owner_email}
        </a>
        <button
          className={styles.copyBtn}
          onClick={() => copyToClipboard(building.owner_email, "Email")}
          title="Copy email"
        >
          📋
        </button>
      </div>

      {/* Phone */}
      <div className={styles.contactRow}>
        <span className={styles.icon}>📞</span>
        <a href={`tel:${building.owner_phone}`} className={styles.contactLink}>
          {building.owner_phone}
        </a>
        <button
          className={styles.copyBtn}
          onClick={() => copyToClipboard(building.owner_phone, "Phone")}
          title="Copy phone"
        >
          📋
        </button>
      </div>

      {/* Inline message */}
      <div className={styles.messageSection}>
        <label className="text-label" style={{ marginBottom: 8, display: "block" }}>
          Send a Message
        </label>
        <textarea
          className="textarea"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Write your message..."
        />
        <button
          className="btn btn-primary"
          style={{ width: "100%", height: 48, marginTop: 12 }}
          onClick={handleSend}
          disabled={sending || !message.trim()}
        >
          {sending ? (
            <>
              <span className={styles.spinner} />
              Sending...
            </>
          ) : (
            "Send Message"
          )}
        </button>
      </div>

      {/* Attribution */}
      <p className={styles.attribution}>
        ℹ️ Contact info from public Fulton County parcel records
      </p>

      {/* Copy toast */}
      {toast && <div className="copy-toast">{toast}</div>}
    </div>
  );
}
