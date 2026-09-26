# Color and spacing tokens for the app theme

COLORS = {
    # ── Base surfaces ──
    "bg_base": "#060708",
    "bg_panel": "#0A0B0D",
    "bg_glass": "rgba(255, 255, 255, 0.05)",
    "bg_glass_strong": "rgba(255, 255, 255, 0.08)",
    "border_soft": "rgba(255, 255, 255, 0.08)",

    # ── Gradient anchors ──
    "gradient_start": "#1a0533",       # deep indigo
    "gradient_mid": "#0d2b45",         # midnight blue
    "gradient_end": "#0a3d2e",         # dark teal
    "gradient_warm": "#2a1040",        # warm violet

    # ── Accent palette ──
    "accent_violet": "#a855f7",
    "accent_violet_dim": "rgba(168, 85, 247, 0.35)",
    "accent_teal": "#2dd4bf",
    "accent_teal_dim": "rgba(45, 212, 191, 0.30)",
    "accent_amber": "#f59e0b",
    "accent_amber_dim": "rgba(245, 158, 11, 0.30)",
    "accent_rose": "#f43f5e",

    # ── Glass / frosted effects ──
    "glass_sidebar": "rgba(14, 10, 30, 0.82)",
    "glass_card": "rgba(255, 255, 255, 0.04)",
    "glass_card_hover": "rgba(255, 255, 255, 0.08)",
    "glass_input": "rgba(255, 255, 255, 0.06)",
    "glass_border": "rgba(255, 255, 255, 0.10)",

    # ── Text hierarchy ──
    "text_primary": "#F4F7FA",
    "text_secondary": "#A0A6AD",
    "text_muted": "#7D858E",
    "text_accent": "#c4b5fd",          # light violet for labels

    # ── Legacy tokens (kept for compatibility) ──
    "cyan_1": "#4FD8E8",
    "cyan_2": "#8FB8FF",
    "cyan_glow": "rgba(79, 216, 232, 0.46)",
    "red_error": "#FF726E",
    "amber_warning": "#F5B866",
    "shadow_dark": "rgba(0, 0, 0, 0.45)",
    "button_hover": "rgba(255, 255, 255, 0.10)",
    "button_active": "rgba(168, 85, 247, 0.18)",
}

SPACING = {
    "window_padding": 18,
    "titlebar_h": 38,
    "hero_gap": 18,
    "panel_radius": 20,
    "pill_radius": 999,
    "card_padding": 18,
    "input_h": 64,
    "button_size": 48,
    "sidebar_width": 300,
    "tiny_gap": 8,
    "small_gap": 12,
    "med_gap": 16,
    "large_gap": 24,
    "xlarge_gap": 32,
}

FONT_FAMILY = {
    "display": "Space Grotesk",
    "body": "Inter, Segoe UI, sans-serif",
}
