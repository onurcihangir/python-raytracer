"""Modern dark theme (QSS) for the ray tracer GUI."""

# Palette
BASE = "#181822"        # window background
SURFACE = "#22222e"     # panels / inputs
SURFACE_ALT = "#2b2b3a"  # hover / alternate
BORDER = "#34344a"
TEXT = "#e6e6f0"
TEXT_MUTED = "#9a9ab4"
ACCENT = "#7c5cff"
ACCENT_HOVER = "#8f72ff"
ACCENT_PRESSED = "#6a49e6"
DANGER = "#ff5c7c"

STYLESHEET = f"""
* {{
    font-family: "Segoe UI", "Inter", system-ui, sans-serif;
    font-size: 13px;
    color: {TEXT};
}}

QMainWindow, QWidget {{
    background-color: {BASE};
}}

QDialog {{
    background-color: {BASE};
}}

/* Group boxes as cards */
QGroupBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    margin-top: 14px;
    padding: 12px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: {TEXT_MUTED};
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* Labels */
QLabel {{
    color: {TEXT};
    background: transparent;
}}
QLabel#statLabel {{
    color: {TEXT_MUTED};
    font-size: 12px;
    padding: 1px 0;
}}

/* Inputs */
QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {{
    background-color: {SURFACE_ALT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 8px;
    selection-background-color: {ACCENT};
}}
QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover, QLineEdit:hover {{
    border-color: {ACCENT};
}}
QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {{
    border-color: {ACCENT};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background-color: {SURFACE_ALT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    selection-background-color: {ACCENT};
    outline: none;
}}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    width: 16px;
    border: none;
    background: transparent;
}}

/* List */
QListWidget {{
    background-color: {SURFACE_ALT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 4px;
    outline: none;
}}
QListWidget::item {{
    padding: 6px 8px;
    border-radius: 6px;
}}
QListWidget::item:selected {{
    background-color: {ACCENT};
    color: white;
}}
QListWidget::item:hover {{
    background-color: {SURFACE};
}}

/* Buttons */
QPushButton {{
    background-color: {SURFACE_ALT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 7px 14px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {BORDER};
    border-color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: {SURFACE};
}}
QPushButton:disabled {{
    color: {TEXT_MUTED};
    background-color: {SURFACE};
    border-color: {BORDER};
}}

/* Primary action button (Start/Stop) */
QPushButton#primary {{
    background-color: {ACCENT};
    border: none;
    color: white;
    padding: 10px 16px;
    font-size: 14px;
}}
QPushButton#primary:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton#primary:pressed {{
    background-color: {ACCENT_PRESSED};
}}
QPushButton#primary:disabled {{
    background-color: {SURFACE_ALT};
    color: {TEXT_MUTED};
}}

/* Progress bar */
QProgressBar {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    height: 16px;
    text-align: center;
    color: {TEXT};
}}
QProgressBar::chunk {{
    background-color: {ACCENT};
    border-radius: 7px;
}}

/* Dialog button box */
QDialogButtonBox QPushButton {{
    min-width: 72px;
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {ACCENT};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""
