import ctypes
import sys
from pathlib import Path
import sqlite3
import tkinter as tk
import tkinter.font as tkfont
import webbrowser
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Callable

import customtkinter as ctk

import database
from calculations import calculate_annual_cost, calculate_monthly_cost


# ---------------------------------------------------------------------------
# GLOBAL APPEARANCE
# ---------------------------------------------------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ---------------------------------------------------------------------------
# APP DATA OPTIONS
# ---------------------------------------------------------------------------

BILLING_FREQUENCIES = [
    "Weekly",
    "Monthly",
    "Every 3 Months",
    "Every 6 Months",
    "Yearly",
]

CATEGORIES = [
    "Entertainment",
    "Music",
    "Gaming",
    "Software",
    "Education",
    "Fitness",
    "Shopping",
    "Cloud Storage",
    "News",
    "Other",
]


# ---------------------------------------------------------------------------
# COLOURS
# ---------------------------------------------------------------------------

COLORS = {
    "background": "#0F172A",
    "surface": "#172033",
    "card": "#1E293B",
    "card_hover": "#29364D",
    "border": "#334155",
    "primary": "#6366F1",
    "primary_hover": "#4F46E5",
    "text": "#F8FAFC",
    "secondary_text": "#94A3B8",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "cancelled": "#64748B",
}


CATEGORY_COLORS = {
    "Entertainment": "#E11D48",
    "Music": "#8B5CF6",
    "Gaming": "#2563EB",
    "Software": "#0891B2",
    "Education": "#D97706",
    "Fitness": "#16A34A",
    "Shopping": "#DB2777",
    "Cloud Storage": "#0284C7",
    "News": "#475569",
    "Other": "#6366F1",
}

# ---------------------------------------------------------------------------
# BUNDLED FONT LOADING
# ---------------------------------------------------------------------------

FR_PRIVATE = 0x10


def get_resource_path(relative_path: str) -> Path:
    """
    Return the correct path for a development run or packaged application.
    """

    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path


def load_private_font(font_path: Path) -> bool:
    """
    Temporarily load a font for this application on Windows.

    The font is available only while the application is running.
    It is not permanently installed on the user's computer.
    """

    if sys.platform != "win32":
        return False

    if not font_path.exists():
        print(f"Font file was not found: {font_path}")
        return False

    result = ctypes.windll.gdi32.AddFontResourceExW(
        str(font_path),
        FR_PRIVATE,
        0,
    )

    return result > 0


def load_bundled_fonts() -> None:
    """
    Load every Space Grotesk font required by the application.
    """

    font_files = [
        "fonts/SpaceGrotesk-Light.ttf",
        "fonts/SpaceGrotesk-Regular.ttf",
        "fonts/SpaceGrotesk-Medium.ttf",
    ]

    failed_fonts: list[str] = []

    for relative_path in font_files:
        font_path = get_resource_path(relative_path)

        if not load_private_font(font_path):
            failed_fonts.append(relative_path)

    if failed_fonts:
        print(
            "The following fonts could not be loaded:",
            ", ".join(failed_fonts),
        )

# ---------------------------------------------------------------------------
# FONTS
# ---------------------------------------------------------------------------

FONT_REGULAR = "Space Grotesk"
FONT_LIGHT = "Space Grotesk Light"
FONT_MEDIUM = "Space Grotesk Medium"


def create_app_fonts() -> dict[str, ctk.CTkFont]:
    """
    Create reusable CustomTkinter font objects.

    This function must only be called after the main CTk root window
    has been created.
    """

    return {
        "tiny": ctk.CTkFont(
            family=FONT_REGULAR,
            size=10,
        ),
        "caption": ctk.CTkFont(
            family=FONT_LIGHT,
            size=11,
        ),
        "body": ctk.CTkFont(
            family=FONT_REGULAR,
            size=13,
        ),
        "button": ctk.CTkFont(
            family=FONT_MEDIUM,
            size=13,
        ),
        "section": ctk.CTkFont(
            family=FONT_MEDIUM,
            size=14,
        ),
        "card_title": ctk.CTkFont(
            family=FONT_MEDIUM,
            size=17,
        ),
        "heading": ctk.CTkFont(
            family=FONT_MEDIUM,
            size=22,
        ),
        "title": ctk.CTkFont(
            family=FONT_MEDIUM,
            size=28,
        ),
        "summary_value": ctk.CTkFont(
            family=FONT_MEDIUM,
            size=23,
        ),
        "icon": ctk.CTkFont(
            family=FONT_MEDIUM,
            size=24,
        ),
    }


# ---------------------------------------------------------------------------
# SUBSCRIPTION CARD
# ---------------------------------------------------------------------------

class SubscriptionCard(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        subscription: sqlite3.Row,
        on_open: Callable[[int], None],
        fonts: dict[str, ctk.CTkFont],
    ) -> None:
        super().__init__(
            parent,
            fg_color=COLORS["card"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"],
        )

        self.subscription = subscription
        self.on_open = on_open
        self.fonts = fonts

        self.grid_columnconfigure(1, weight=1)

        self.create_icon()
        self.create_main_information()
        self.create_price_information()
        self.create_status_badge()

        self.bind_click_events()
        self.bind_hover_events()

    def create_icon(self) -> None:
        name = self.subscription["name"].strip()
        first_letter = name[0].upper() if name else "?"

        category_colour = CATEGORY_COLORS.get(
            self.subscription["category"],
            COLORS["primary"],
        )

        self.icon_frame = ctk.CTkFrame(
            self,
            width=54,
            height=54,
            corner_radius=14,
            fg_color=category_colour,
        )
        self.icon_frame.grid(
            row=0,
            column=0,
            rowspan=2,
            padx=(16, 14),
            pady=16,
        )
        self.icon_frame.grid_propagate(False)

        self.icon_label = ctk.CTkLabel(
            self.icon_frame,
            text=first_letter,
            font=self.fonts["icon"],
            text_color="#FFFFFF",
        )
        self.icon_label.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

    def create_main_information(self) -> None:
        self.name_label = ctk.CTkLabel(
            self,
            text=self.subscription["name"],
            font=self.fonts["card_title"],
            text_color=COLORS["text"],
            anchor="w",
        )
        self.name_label.grid(
            row=0,
            column=1,
            sticky="sw",
            pady=(16, 2),
        )

        category = self.subscription["category"]
        renewal = self.subscription["next_renewal_date"]
        subtitle = f"{category}  •  Renews {renewal}"

        self.subtitle_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=self.fonts["caption"],
            text_color=COLORS["secondary_text"],
            anchor="w",
        )
        self.subtitle_label.grid(
            row=1,
            column=1,
            sticky="nw",
            pady=(2, 16),
        )

    def create_price_information(self) -> None:
        price = float(self.subscription["price"])
        frequency = self.subscription["billing_frequency"]

        monthly_cost = calculate_monthly_cost(
            price,
            frequency,
        )

        self.price_label = ctk.CTkLabel(
            self,
            text=f"£{price:.2f}",
            font=self.fonts["card_title"],
            text_color=COLORS["text"],
            anchor="e",
        )
        self.price_label.grid(
            row=0,
            column=2,
            padx=(10, 18),
            pady=(16, 2),
            sticky="se",
        )

        self.frequency_label = ctk.CTkLabel(
            self,
            text=f"{frequency} · £{monthly_cost:.2f}/month",
            font=self.fonts["caption"],
            text_color=COLORS["secondary_text"],
            anchor="e",
        )
        self.frequency_label.grid(
            row=1,
            column=2,
            padx=(10, 18),
            pady=(2, 16),
            sticky="ne",
        )

    def create_status_badge(self) -> None:
        is_cancelled = bool(
            self.subscription["is_cancelled"]
        )

        renewal_date = datetime.strptime(
            self.subscription["next_renewal_date"],
            "%Y-%m-%d",
        ).date()

        today = datetime.now().date()

        if is_cancelled:
            status_text = "Cancelled"
            status_colour = COLORS["cancelled"]
        elif renewal_date < today:
            status_text = "Overdue"
            status_colour = COLORS["danger"]
        else:
            status_text = "Active"
            status_colour = COLORS["success"]

        self.status_label = ctk.CTkLabel(
            self,
            text=status_text,
            width=82,
            height=28,
            corner_radius=14,
            fg_color=status_colour,
            text_color="#FFFFFF",
            font=self.fonts["tiny"],
        )
        self.status_label.grid(
            row=0,
            column=3,
            rowspan=2,
            padx=(0, 16),
            pady=16,
        )

    def bind_click_events(self) -> None:
        widgets = [
            self,
            self.icon_frame,
            self.icon_label,
            self.name_label,
            self.subtitle_label,
            self.price_label,
            self.frequency_label,
            self.status_label,
        ]

        for widget in widgets:
            widget.bind(
                "<Button-1>",
                self.open_details,
            )

            try:
                widget.configure(cursor="hand2")
            except (tk.TclError, ValueError):
                pass

    def bind_hover_events(self) -> None:
        widgets = [
            self,
            self.name_label,
            self.subtitle_label,
            self.price_label,
            self.frequency_label,
        ]

        for widget in widgets:
            widget.bind(
                "<Enter>",
                self.on_mouse_enter,
            )
            widget.bind(
                "<Leave>",
                self.on_mouse_leave,
            )

    def on_mouse_enter(self, _event=None) -> None:
        self.configure(
            fg_color=COLORS["card_hover"],
            border_color=COLORS["primary"],
        )

    def on_mouse_leave(self, _event=None) -> None:
        self.configure(
            fg_color=COLORS["card"],
            border_color=COLORS["border"],
        )

    def open_details(self, _event=None) -> None:
        self.on_open(
            int(self.subscription["id"])
        )


# ---------------------------------------------------------------------------
# MAIN APPLICATION
# ---------------------------------------------------------------------------

class SubscriptionApp:
    def __init__(self, root: ctk.CTk) -> None:
        self.root = root
        self.root.title("SubTrack")
        self.root.geometry("1180x760")
        self.root.minsize(940, 650)
        self.root.configure(
            fg_color=COLORS["background"]
        )

        # The CTk root now exists, so CTkFont objects can be created.
        self.fonts = create_app_fonts()

        # Apply the chosen font to standard tkinter and ttk controls.
        self.configure_default_tk_fonts()
        self.configure_styles()

        database.create_database()

        self.create_interface()
        self.refresh_subscription_cards()

    def configure_default_tk_fonts(self) -> None:
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(
            family=FONT_REGULAR,
            size=12,
        )

        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(
            family=FONT_REGULAR,
            size=12,
        )

        fixed_font = tkfont.nametofont("TkFixedFont")
        fixed_font.configure(
            family=FONT_REGULAR,
            size=12,
        )

        menu_font = tkfont.nametofont("TkMenuFont")
        menu_font.configure(
            family=FONT_REGULAR,
            size=12,
        )

        heading_font = tkfont.nametofont("TkHeadingFont")
        heading_font.configure(
            family=FONT_MEDIUM,
            size=12,
        )

        caption_font = tkfont.nametofont("TkCaptionFont")
        caption_font.configure(
            family=FONT_REGULAR,
            size=12,
        )

    def configure_styles(self) -> None:
        style = ttk.Style()

        try:
            style.theme_use("vista")
        except tk.TclError:
            pass

        style.configure(
            ".",
            font=(FONT_REGULAR, 12),
        )

        style.configure(
            "TLabel",
            font=(FONT_REGULAR, 12),
        )

        style.configure(
            "TButton",
            font=(FONT_MEDIUM, 12),
        )

        style.configure(
            "TEntry",
            font=(FONT_REGULAR, 12),
        )

        style.configure(
            "TCheckbutton",
            font=(FONT_REGULAR, 12),
        )

        style.configure(
            "TCombobox",
            font=(FONT_REGULAR, 12),
        )

        style.configure(
            "TSpinbox",
            font=(FONT_REGULAR, 12),
        )

        style.configure(
            "Treeview",
            font=(FONT_REGULAR, 11),
            rowheight=32,
        )

        style.configure(
            "Treeview.Heading",
            font=(FONT_MEDIUM, 11),
        )

    def create_interface(self) -> None:
        self.main_container = ctk.CTkFrame(
            self.root,
            fg_color="transparent",
        )
        self.main_container.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=24,
        )

        self.create_header(self.main_container)
        self.create_summary_section(self.main_container)
        self.create_filter_section(self.main_container)
        self.create_cards_section(self.main_container)

    def create_header(self, parent) -> None:
        header = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        header.pack(
            fill="x",
            pady=(0, 22),
        )

        text_container = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )
        text_container.pack(side="left")

        title = ctk.CTkLabel(
            text_container,
            text="Your subscriptions",
            font=self.fonts["title"],
            text_color=COLORS["text"],
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            text_container,
            text=(
                "Track renewals, understand your spending "
                "and cancel unwanted services."
            ),
            font=self.fonts["body"],
            text_color=COLORS["secondary_text"],
        )
        subtitle.pack(
            anchor="w",
            pady=(3, 0),
        )

        add_button = ctk.CTkButton(
            header,
            text="+  Add subscription",
            command=self.open_add_window,
            height=42,
            corner_radius=12,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=self.fonts["button"],
        )
        add_button.pack(
            side="right",
            pady=5,
        )

    def create_summary_section(self, parent) -> None:
        summary_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        summary_frame.pack(
            fill="x",
            pady=(0, 20),
        )

        summary_frame.grid_columnconfigure(
            (0, 1, 2),
            weight=1,
        )

        self.monthly_total_label = self.create_summary_card(
            summary_frame,
            column=0,
            title="Monthly cost",
            icon="M",
            colour=COLORS["primary"],
        )

        self.annual_total_label = self.create_summary_card(
            summary_frame,
            column=1,
            title="Annual cost",
            icon="Y",
            colour="#8B5CF6",
        )

        self.active_count_label = self.create_summary_card(
            summary_frame,
            column=2,
            title="Active subscriptions",
            icon="✓",
            colour=COLORS["success"],
        )

    def create_summary_card(
        self,
        parent,
        column: int,
        title: str,
        icon: str,
        colour: str,
    ) -> ctk.CTkLabel:
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["surface"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=(
                0 if column == 0 else 7,
                0 if column == 2 else 7,
            ),
        )

        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            width=38,
            height=38,
            corner_radius=12,
            fg_color=colour,
            text_color="#FFFFFF",
            font=self.fonts["section"],
        )
        icon_label.pack(
            anchor="w",
            padx=18,
            pady=(18, 10),
        )

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=self.fonts["body"],
            text_color=COLORS["secondary_text"],
        )
        title_label.pack(
            anchor="w",
            padx=18,
        )

        value_label = ctk.CTkLabel(
            card,
            text="£0.00",
            font=self.fonts["summary_value"],
            text_color=COLORS["text"],
        )
        value_label.pack(
            anchor="w",
            padx=18,
            pady=(3, 18),
        )

        return value_label

    def create_filter_section(self, parent) -> None:
        filter_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        filter_frame.pack(
            fill="x",
            pady=(0, 14),
        )

        self.search_variable = tk.StringVar()
        self.status_filter_variable = tk.StringVar(
            value="All"
        )

        search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.search_variable,
            placeholder_text="Search",
            height=40,
            width=320,
            corner_radius=12,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=self.fonts["body"],
        )
        search_entry.pack(side="left")

        search_entry.bind(
            "<KeyRelease>",
            lambda _event: self.refresh_subscription_cards(),
        )

        filter_menu = ctk.CTkSegmentedButton(
            filter_frame,
            values=[
                "All",
                "Active",
                "Overdue",
                "Cancelled",
            ],
            variable=self.status_filter_variable,
            command=lambda _value:
                self.refresh_subscription_cards(),
            fg_color=COLORS["surface"],
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
            unselected_color=COLORS["surface"],
            unselected_hover_color=COLORS["card_hover"],
            font=self.fonts["button"],
        )
        filter_menu.pack(side="right")

    def create_cards_section(self, parent) -> None:
        self.cards_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            corner_radius=0,
        )
        self.cards_frame.pack(
            fill="both",
            expand=True,
        )

        self.cards_frame.grid_columnconfigure(
            0,
            weight=1,
        )

    def refresh_subscription_cards(self) -> None:
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        subscriptions = database.get_all_subscriptions()

        search_text = (
            self.search_variable
            .get()
            .strip()
            .lower()
        )

        selected_filter = (
            self.status_filter_variable.get()
        )

        total_monthly = 0.0
        total_annual = 0.0
        active_count = 0

        visible_subscriptions: list[sqlite3.Row] = []

        for subscription in subscriptions:
            is_cancelled = bool(
                subscription["is_cancelled"]
            )

            renewal_date = datetime.strptime(
                subscription["next_renewal_date"],
                "%Y-%m-%d",
            ).date()

            today = datetime.now().date()

            is_overdue = (
                not is_cancelled
                and renewal_date < today
            )

            if not is_cancelled:
                active_count += 1

                total_monthly += calculate_monthly_cost(
                    subscription["price"],
                    subscription["billing_frequency"],
                )

                total_annual += calculate_annual_cost(
                    subscription["price"],
                    subscription["billing_frequency"],
                )

            matches_search = (
                not search_text
                or search_text
                in subscription["name"].lower()
                or search_text
                in subscription["category"].lower()
            )

            if not matches_search:
                continue

            if selected_filter == "All":
                matches_filter = True
            elif selected_filter == "Active":
                matches_filter = (
                    not is_cancelled
                    and not is_overdue
                )
            elif selected_filter == "Overdue":
                matches_filter = is_overdue
            elif selected_filter == "Cancelled":
                matches_filter = is_cancelled
            else:
                matches_filter = True

            if matches_filter:
                visible_subscriptions.append(
                    subscription
                )

        self.monthly_total_label.configure(
            text=f"£{total_monthly:.2f}"
        )

        self.annual_total_label.configure(
            text=f"£{total_annual:.2f}"
        )

        self.active_count_label.configure(
            text=str(active_count)
        )

        if not visible_subscriptions:
            self.show_empty_cards_message()
            return

        for row_number, subscription in enumerate(
            visible_subscriptions
        ):
            card = SubscriptionCard(
                self.cards_frame,
                subscription=subscription,
                on_open=self.open_subscription_details,
                fonts=self.fonts,
            )

            card.grid(
                row=row_number,
                column=0,
                sticky="ew",
                padx=2,
                pady=7,
            )

    def show_empty_cards_message(self) -> None:
        empty_frame = ctk.CTkFrame(
            self.cards_frame,
            fg_color=COLORS["surface"],
            corner_radius=18,
            border_width=1,
            border_color=COLORS["border"],
        )
        empty_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=2,
            pady=20,
        )

        icon_label = ctk.CTkLabel(
            empty_frame,
            text="○",
            font=self.fonts["title"],
            text_color=COLORS["secondary_text"],
        )
        icon_label.pack(
            pady=(30, 8),
        )

        message_label = ctk.CTkLabel(
            empty_frame,
            text="No subscriptions found",
            font=self.fonts["card_title"],
            text_color=COLORS["text"],
        )
        message_label.pack()

        help_label = ctk.CTkLabel(
            empty_frame,
            text=(
                "Add a new subscription or "
                "change your search and filter."
            ),
            font=self.fonts["body"],
            text_color=COLORS["secondary_text"],
        )
        help_label.pack(
            pady=(5, 30),
        )

    def open_add_window(self) -> None:
        SubscriptionFormWindow(
            parent=self.root,
            on_saved=self.refresh_subscription_cards,
            fonts=self.fonts,
        )

    def open_edit_window_by_id(
        self,
        subscription_id: int,
    ) -> None:
        SubscriptionFormWindow(
            parent=self.root,
            on_saved=self.refresh_subscription_cards,
            fonts=self.fonts,
            subscription_id=subscription_id,
        )

    def open_subscription_details(
        self,
        subscription_id: int,
    ) -> None:
        SubscriptionDetailsWindow(
            parent=self.root,
            subscription_id=subscription_id,
            on_changed=self.refresh_subscription_cards,
            open_edit_callback=self.open_edit_window_by_id,
            fonts=self.fonts,
        )


# ---------------------------------------------------------------------------
# ADD / EDIT FORM
# ---------------------------------------------------------------------------

class SubscriptionFormWindow:
    def __init__(
        self,
        parent,
        on_saved: Callable[[], None],
        fonts: dict[str, ctk.CTkFont],
        subscription_id: int | None = None,
    ) -> None:
        self.parent = parent
        self.on_saved = on_saved
        self.fonts = fonts
        self.subscription_id = subscription_id

        self.window = ctk.CTkToplevel(parent)

        if subscription_id is None:
            self.window.title("Add Subscription")
        else:
            self.window.title("Edit Subscription")

        self.window.geometry("620x740")
        self.window.minsize(560, 650)
        self.window.configure(
            fg_color=COLORS["background"]
        )
        self.window.transient(parent)
        self.window.grab_set()

        self.create_variables()
        self.create_form()

        if subscription_id is not None:
            self.load_subscription()

    def create_variables(self) -> None:
        self.name_variable = tk.StringVar()
        self.price_variable = tk.StringVar()
        self.frequency_variable = tk.StringVar(
            value="Monthly"
        )
        self.renewal_variable = tk.StringVar(
            value=datetime.now().strftime("%Y-%m-%d")
        )
        self.reminder_variable = tk.IntVar(value=3)
        self.category_variable = tk.StringVar(
            value="Entertainment"
        )
        self.url_variable = tk.StringVar()
        self.cancelled_variable = tk.BooleanVar(
            value=False
        )

    def create_form(self) -> None:
        container = ctk.CTkScrollableFrame(
            self.window,
            fg_color="transparent",
        )
        container.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=24,
        )

        heading_text = (
            "Add a subscription"
            if self.subscription_id is None
            else "Edit subscription"
        )

        heading = ctk.CTkLabel(
            container,
            text=heading_text,
            font=self.fonts["heading"],
            text_color=COLORS["text"],
        )
        heading.pack(
            anchor="w",
            pady=(0, 18),
        )

        self.create_field_label(
            container,
            "Subscription name",
        )

        self.name_entry = ctk.CTkEntry(
            container,
            textvariable=self.name_variable,
            height=42,
            corner_radius=10,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            font=self.fonts["body"],
        )
        self.name_entry.pack(
            fill="x",
            pady=(0, 15),
        )

        self.create_field_label(
            container,
            "Payment amount",
        )

        price_entry = ctk.CTkEntry(
            container,
            textvariable=self.price_variable,
            placeholder_text="For example: 10.99",
            height=42,
            corner_radius=10,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            font=self.fonts["body"],
        )
        price_entry.pack(
            fill="x",
            pady=(0, 15),
        )

        self.create_field_label(
            container,
            "Billing frequency",
        )

        frequency_menu = ctk.CTkOptionMenu(
            container,
            variable=self.frequency_variable,
            values=BILLING_FREQUENCIES,
            height=42,
            corner_radius=10,
            fg_color=COLORS["surface"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            font=self.fonts["body"],
            dropdown_font=self.fonts["body"],
        )
        frequency_menu.pack(
            fill="x",
            pady=(0, 15),
        )

        self.create_field_label(
            container,
            "Next renewal date",
        )

        renewal_entry = ctk.CTkEntry(
            container,
            textvariable=self.renewal_variable,
            placeholder_text="YYYY-MM-DD",
            height=42,
            corner_radius=10,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            font=self.fonts["body"],
        )
        renewal_entry.pack(
            fill="x",
        )

        date_help = ctk.CTkLabel(
            container,
            text="Use the format YYYY-MM-DD.",
            font=self.fonts["caption"],
            text_color=COLORS["secondary_text"],
        )
        date_help.pack(
            anchor="w",
            pady=(4, 15),
        )

        self.create_field_label(
            container,
            "Reminder days before renewal",
        )

        reminder_entry = ctk.CTkEntry(
            container,
            textvariable=self.reminder_variable,
            height=42,
            corner_radius=10,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            font=self.fonts["body"],
        )
        reminder_entry.pack(
            fill="x",
            pady=(0, 15),
        )

        self.create_field_label(
            container,
            "Category",
        )

        category_menu = ctk.CTkOptionMenu(
            container,
            variable=self.category_variable,
            values=CATEGORIES,
            height=42,
            corner_radius=10,
            fg_color=COLORS["surface"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            font=self.fonts["body"],
            dropdown_font=self.fonts["body"],
        )
        category_menu.pack(
            fill="x",
            pady=(0, 15),
        )

        self.create_field_label(
            container,
            "Official cancellation webpage",
        )

        url_entry = ctk.CTkEntry(
            container,
            textvariable=self.url_variable,
            placeholder_text="https://example.com/account",
            height=42,
            corner_radius=10,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            font=self.fonts["body"],
        )
        url_entry.pack(
            fill="x",
            pady=(0, 15),
        )

        self.create_field_label(
            container,
            "Cancellation instructions",
        )

        self.instructions_text = ctk.CTkTextbox(
            container,
            height=120,
            corner_radius=10,
            fg_color=COLORS["surface"],
            border_width=1,
            border_color=COLORS["border"],
            font=self.fonts["body"],
            wrap="word",
        )
        self.instructions_text.pack(
            fill="x",
            pady=(0, 15),
        )

        cancelled_checkbox = ctk.CTkCheckBox(
            container,
            text="This subscription is cancelled",
            variable=self.cancelled_variable,
            font=self.fonts["body"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        )
        cancelled_checkbox.pack(
            anchor="w",
            pady=(0, 22),
        )

        button_frame = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )
        button_frame.pack(
            fill="x",
        )

        close_button = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.window.destroy,
            height=42,
            fg_color=COLORS["surface"],
            hover_color=COLORS["card_hover"],
            border_width=1,
            border_color=COLORS["border"],
            font=self.fonts["button"],
        )
        close_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 6),
        )

        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_subscription,
            height=42,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=self.fonts["button"],
        )
        save_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(6, 0),
        )

        self.name_entry.focus_set()

    def create_field_label(
        self,
        parent,
        text: str,
    ) -> None:
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=self.fonts["section"],
            text_color=COLORS["text"],
        )
        label.pack(
            anchor="w",
            pady=(0, 5),
        )

    def load_subscription(self) -> None:
        if self.subscription_id is None:
            return

        subscription = database.get_subscription(
            self.subscription_id
        )

        if subscription is None:
            messagebox.showerror(
                "Subscription missing",
                "This subscription could not be found.",
                parent=self.window,
            )
            self.window.destroy()
            return

        self.name_variable.set(subscription["name"])
        self.price_variable.set(subscription["price"])
        self.frequency_variable.set(
            subscription["billing_frequency"]
        )
        self.renewal_variable.set(
            subscription["next_renewal_date"]
        )
        self.reminder_variable.set(
            subscription["reminder_days"]
        )
        self.category_variable.set(
            subscription["category"]
        )
        self.url_variable.set(
            subscription["cancellation_url"]
        )
        self.cancelled_variable.set(
            bool(subscription["is_cancelled"])
        )

        self.instructions_text.delete("1.0", "end")
        self.instructions_text.insert(
            "1.0",
            subscription["cancellation_instructions"],
        )

    def save_subscription(self) -> None:
        name = self.name_variable.get().strip()
        price_text = self.price_variable.get().strip()
        billing_frequency = (
            self.frequency_variable.get()
        )
        next_renewal_date = (
            self.renewal_variable.get().strip()
        )
        category = self.category_variable.get()
        cancellation_url = (
            self.url_variable.get().strip()
        )
        cancellation_instructions = (
            self.instructions_text
            .get("1.0", "end")
            .strip()
        )

        if not name:
            messagebox.showerror(
                "Missing name",
                "Enter the subscription name.",
                parent=self.window,
            )
            return

        try:
            price = float(
                price_text.replace(",", ".")
            )
        except ValueError:
            messagebox.showerror(
                "Invalid price",
                "Enter a valid price such as 10.99.",
                parent=self.window,
            )
            return

        if price < 0:
            messagebox.showerror(
                "Invalid price",
                "The price cannot be negative.",
                parent=self.window,
            )
            return

        try:
            datetime.strptime(
                next_renewal_date,
                "%Y-%m-%d",
            )
        except ValueError:
            messagebox.showerror(
                "Invalid date",
                "Use the date format YYYY-MM-DD.",
                parent=self.window,
            )
            return

        try:
            reminder_days = int(
                self.reminder_variable.get()
            )
        except (ValueError, tk.TclError):
            messagebox.showerror(
                "Invalid reminder",
                "Enter a whole number between 0 and 30.",
                parent=self.window,
            )
            return

        if not 0 <= reminder_days <= 30:
            messagebox.showerror(
                "Invalid reminder",
                "Reminder days must be between 0 and 30.",
                parent=self.window,
            )
            return

        if self.subscription_id is None:
            database.add_subscription(
                name=name,
                price=price,
                billing_frequency=billing_frequency,
                next_renewal_date=next_renewal_date,
                reminder_days=reminder_days,
                category=category,
                cancellation_url=cancellation_url,
                cancellation_instructions=
                    cancellation_instructions,
            )
        else:
            database.update_subscription(
                subscription_id=self.subscription_id,
                name=name,
                price=price,
                billing_frequency=billing_frequency,
                next_renewal_date=next_renewal_date,
                reminder_days=reminder_days,
                category=category,
                cancellation_url=cancellation_url,
                cancellation_instructions=
                    cancellation_instructions,
                is_cancelled=
                    self.cancelled_variable.get(),
            )

        self.on_saved()
        self.window.destroy()


# ---------------------------------------------------------------------------
# SUBSCRIPTION DETAILS WINDOW
# ---------------------------------------------------------------------------

class SubscriptionDetailsWindow:
    def __init__(
        self,
        parent,
        subscription_id: int,
        on_changed: Callable[[], None],
        open_edit_callback: Callable[[int], None],
        fonts: dict[str, ctk.CTkFont],
    ) -> None:
        self.parent = parent
        self.subscription_id = subscription_id
        self.on_changed = on_changed
        self.open_edit_callback = open_edit_callback
        self.fonts = fonts

        subscription = database.get_subscription(
            subscription_id
        )

        if subscription is None:
            messagebox.showerror(
                "Subscription missing",
                "This subscription could not be found.",
                parent=parent,
            )
            return

        self.subscription: sqlite3.Row = subscription

        self.window = ctk.CTkToplevel(parent)
        self.window.title(
            self.subscription["name"]
        )
        self.window.geometry("620x680")
        self.window.minsize(560, 620)
        self.window.configure(
            fg_color=COLORS["background"]
        )
        self.window.transient(parent)
        self.window.grab_set()

        self.create_interface()

    def create_interface(self) -> None:
        container = ctk.CTkScrollableFrame(
            self.window,
            fg_color="transparent",
        )
        container.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=24,
        )

        self.create_title_section(container)
        self.create_cost_section(container)
        self.create_renewal_section(container)
        self.create_cancellation_section(container)
        self.create_buttons(container)

    def create_title_section(self, parent) -> None:
        title_card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["surface"],
            corner_radius=18,
            border_width=1,
            border_color=COLORS["border"],
        )
        title_card.pack(
            fill="x",
            pady=(0, 14),
        )

        category_colour = CATEGORY_COLORS.get(
            self.subscription["category"],
            COLORS["primary"],
        )

        icon = ctk.CTkLabel(
            title_card,
            text=self.subscription["name"][:1].upper(),
            width=58,
            height=58,
            corner_radius=16,
            fg_color=category_colour,
            text_color="#FFFFFF",
            font=self.fonts["heading"],
        )
        icon.pack(
            side="left",
            padx=18,
            pady=18,
        )

        text_frame = ctk.CTkFrame(
            title_card,
            fg_color="transparent",
        )
        text_frame.pack(
            side="left",
            fill="both",
            expand=True,
            pady=18,
        )

        name_label = ctk.CTkLabel(
            text_frame,
            text=self.subscription["name"],
            font=self.fonts["heading"],
            text_color=COLORS["text"],
        )
        name_label.pack(anchor="w")

        category_label = ctk.CTkLabel(
            text_frame,
            text=self.subscription["category"],
            font=self.fonts["body"],
            text_color=COLORS["secondary_text"],
        )
        category_label.pack(
            anchor="w",
            pady=(4, 0),
        )

    def create_cost_section(self, parent) -> None:
        price = float(self.subscription["price"])
        frequency = self.subscription[
            "billing_frequency"
        ]

        monthly = calculate_monthly_cost(
            price,
            frequency,
        )

        annual = calculate_annual_cost(
            price,
            frequency,
        )

        section = self.create_section(
            parent,
            "Cost information",
        )

        self.add_detail_row(
            section,
            "Payment",
            f"£{price:.2f}",
        )

        self.add_detail_row(
            section,
            "Frequency",
            frequency,
        )

        self.add_detail_row(
            section,
            "Monthly equivalent",
            f"£{monthly:.2f}",
        )

        self.add_detail_row(
            section,
            "Annual equivalent",
            f"£{annual:.2f}",
        )

    def create_renewal_section(self, parent) -> None:
        section = self.create_section(
            parent,
            "Renewal information",
        )

        self.add_detail_row(
            section,
            "Next renewal",
            self.subscription["next_renewal_date"],
        )

        self.add_detail_row(
            section,
            "Reminder",
            (
                f"{self.subscription['reminder_days']} "
                "days before"
            ),
        )

        renewal_date = datetime.strptime(
            self.subscription["next_renewal_date"],
            "%Y-%m-%d",
        ).date()

        if bool(self.subscription["is_cancelled"]):
            status = "Cancelled"
        elif renewal_date < datetime.now().date():
            status = "Overdue"
        else:
            status = "Active"

        self.add_detail_row(
            section,
            "Status",
            status,
        )

    def create_cancellation_section(
        self,
        parent,
    ) -> None:
        section = self.create_section(
            parent,
            "Cancellation assistance",
        )

        instructions = self.subscription[
            "cancellation_instructions"
        ].strip()

        if not instructions:
            instructions = (
                "No cancellation instructions "
                "have been added."
            )

        instructions_label = ctk.CTkLabel(
            section,
            text=instructions,
            justify="left",
            wraplength=500,
            font=self.fonts["body"],
            text_color=COLORS["secondary_text"],
        )
        instructions_label.pack(
            fill="x",
            padx=16,
            pady=(4, 16),
            anchor="w",
        )

    def create_section(
        self,
        parent,
        title: str,
    ) -> ctk.CTkFrame:
        section = ctk.CTkFrame(
            parent,
            fg_color=COLORS["surface"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"],
        )
        section.pack(
            fill="x",
            pady=7,
        )

        title_label = ctk.CTkLabel(
            section,
            text=title,
            font=self.fonts["section"],
            text_color=COLORS["text"],
        )
        title_label.pack(
            anchor="w",
            padx=16,
            pady=(15, 8),
        )

        return section

    def add_detail_row(
        self,
        parent,
        label: str,
        value: str,
    ) -> None:
        row = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        row.pack(
            fill="x",
            padx=16,
            pady=5,
        )

        label_widget = ctk.CTkLabel(
            row,
            text=label,
            font=self.fonts["body"],
            text_color=COLORS["secondary_text"],
        )
        label_widget.pack(side="left")

        value_widget = ctk.CTkLabel(
            row,
            text=value,
            font=self.fonts["section"],
            text_color=COLORS["text"],
        )
        value_widget.pack(side="right")

    def create_buttons(self, parent) -> None:
        button_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        button_frame.pack(
            fill="x",
            pady=(18, 6),
        )

        edit_button = ctk.CTkButton(
            button_frame,
            text="Edit",
            command=self.edit_subscription,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            height=40,
            font=self.fonts["button"],
        )
        edit_button.pack(
            fill="x",
            pady=5,
        )

        cancellation_url = self.subscription[
            "cancellation_url"
        ].strip()

        open_button = ctk.CTkButton(
            button_frame,
            text="Open cancellation page",
            command=self.open_cancellation_page,
            fg_color=COLORS["surface"],
            hover_color=COLORS["card_hover"],
            border_width=1,
            border_color=COLORS["border"],
            height=40,
            font=self.fonts["button"],
        )
        open_button.pack(
            fill="x",
            pady=5,
        )

        if not cancellation_url:
            open_button.configure(state="disabled")

        cancellation_text = (
            "Mark active"
            if self.subscription["is_cancelled"]
            else "Mark cancelled"
        )

        cancel_button = ctk.CTkButton(
            button_frame,
            text=cancellation_text,
            command=self.toggle_cancelled,
            fg_color=COLORS["warning"],
            hover_color="#D97706",
            height=40,
            font=self.fonts["button"],
        )
        cancel_button.pack(
            fill="x",
            pady=5,
        )

        delete_button = ctk.CTkButton(
            button_frame,
            text="Delete subscription",
            command=self.delete_subscription,
            fg_color=COLORS["danger"],
            hover_color="#DC2626",
            height=40,
            font=self.fonts["button"],
        )
        delete_button.pack(
            fill="x",
            pady=5,
        )

    def edit_subscription(self) -> None:
        self.window.destroy()
        self.open_edit_callback(
            self.subscription_id
        )

    def toggle_cancelled(self) -> None:
        current_status = bool(
            self.subscription["is_cancelled"]
        )

        database.set_cancelled_status(
            self.subscription_id,
            not current_status,
        )

        self.on_changed()
        self.window.destroy()

    def open_cancellation_page(self) -> None:
        address = self.subscription[
            "cancellation_url"
        ].strip()

        if not address:
            return

        if not address.startswith(
            ("http://", "https://")
        ):
            address = "https://" + address

        try:
            webbrowser.open_new_tab(address)
        except webbrowser.Error:
            messagebox.showerror(
                "Could not open page",
                "The cancellation webpage could not be opened.",
                parent=self.window,
            )

    def delete_subscription(self) -> None:
        confirmed = messagebox.askyesno(
            "Delete subscription",
            (
                f"Delete {self.subscription['name']} "
                "permanently?"
            ),
            parent=self.window,
        )

        if not confirmed:
            return

        database.delete_subscription(
            self.subscription_id
        )

        self.on_changed()
        self.window.destroy()


# ---------------------------------------------------------------------------
# PROGRAM STARTUP
# ---------------------------------------------------------------------------

def main() -> None:
    # The bundled font files must be loaded before Tk creates any widgets.
    load_bundled_fonts()

    root = ctk.CTk()
    SubscriptionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()