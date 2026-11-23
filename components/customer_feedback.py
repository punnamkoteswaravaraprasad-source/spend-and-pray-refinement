
import streamlit as st
import csv
import uuid

from pathlib import Path
from datetime import datetime, timezone


# ==================================================
# 1. FILE CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

FEEDBACK_FILE = DATA_DIR / "customer_feedback.csv"


# ==================================================
# 2. FEEDBACK DATA STRUCTURE
# ==================================================

FEEDBACK_FIELDS = [
    "feedback_id",
    "order_id",
    "submitted_at",
    "reported_source",
    "source_details",
    "shopping_rating",
    "customer_feedback"
]


# ==================================================
# 3. MARKETING SOURCE OPTIONS
# ==================================================

SOURCE_OPTIONS = [
    "Instagram / Facebook Advertisement",
    "Organic Social Media",
    "Influencer / Content Creator",
    "Farmers Market",
    "Pop-up Event",
    "Friend / Family Recommendation",
    "Google / Online Search",
    "Returning Customer",
    "Other",
    "I don't remember"
]


# ==================================================
# 4. CHECK EXISTING FEEDBACK
# ==================================================

def feedback_exists(order_id):

    if not FEEDBACK_FILE.exists():
        return False

    with open(
        FEEDBACK_FILE,
        mode="r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        return any(
            row.get("order_id") == order_id
            for row in reader
        )


# ==================================================
# 5. SAVE CUSTOMER FEEDBACK
# ==================================================

def save_feedback(
    order_id,
    reported_source,
    source_details,
    shopping_rating,
    customer_feedback
):

    if feedback_exists(order_id):
        return False

    feedback_record = {
        "feedback_id": (
            "FB-" + uuid.uuid4().hex[:8].upper()
        ),

        "order_id": order_id,

        "submitted_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "reported_source": reported_source,

        "source_details": source_details.strip(),

        "shopping_rating": (
            shopping_rating
            if shopping_rating is not None
            else ""
        ),

        "customer_feedback": customer_feedback.strip()
    }

    write_header = (
        not FEEDBACK_FILE.exists()
        or FEEDBACK_FILE.stat().st_size == 0
    )

    with open(
        FEEDBACK_FILE,
        mode="a",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FEEDBACK_FIELDS
        )

        if write_header:
            writer.writeheader()

        writer.writerow(feedback_record)

    return True


# ==================================================
# 6. DISPLAY CUSTOMER FEEDBACK FORM
# ==================================================

def display_customer_feedback(order_id):

    if not order_id:
        return

    if feedback_exists(order_id):

        st.success(
            "Thank you for sharing your feedback!"
        )

        return

    skipped_key = f"feedback_skipped_{order_id}"

    if st.session_state.get(skipped_key, False):
        return

    st.divider()

    st.markdown("""
<div class="feedback-heading">
<div class="eyebrow">WE VALUE YOUR OPINION</div>
<div class="collection-title">Tell us about your experience.</div>
<div class="collection-subtitle">Help us understand how you discovered HotVile and how we can serve you better.</div>
</div>
""", unsafe_allow_html=True)

    st.caption(
        "This survey is optional and takes less than a minute."
    )

    with st.form(
        key=f"customer_feedback_form_{order_id}"
    ):

        # ------------------------------------------
        # MARKETING DISCOVERY SOURCE
        # ------------------------------------------

        reported_source = st.radio(
            "How did you first hear about HotVile?",
            options=SOURCE_OPTIONS,
            index=None
        )

        # ------------------------------------------
        # ADDITIONAL MARKETING DETAILS
        # ------------------------------------------

        source_details = st.text_input(
            "Could you tell us a little more? (Optional)",
            placeholder=(
                "Advertisement, influencer name, "
                "farmers market or event name..."
            )
        )

        # ------------------------------------------
        # CUSTOMER SHOPPING EXPERIENCE
        # ------------------------------------------

        shopping_rating = st.radio(
            "How was your shopping experience? (Optional)",
            options=[1, 2, 3, 4, 5],
            format_func=lambda rating: f"{rating} / 5",
            index=None,
            horizontal=True
        )

        # ------------------------------------------
        # GENERAL CUSTOMER FEEDBACK
        # ------------------------------------------

        customer_feedback = st.text_area(
            "Any additional feedback? (Optional)",
            placeholder=(
                "Tell us what you liked or "
                "how we could improve..."
            ),
            height=100
        )

        st.caption(
            "Please avoid including personal or "
            "payment information in your feedback."
        )

        submit_button = st.form_submit_button(
            "Submit Feedback",
            width="stretch"
        )

    # ----------------------------------------------
    # HANDLE SUBMISSION
    # ----------------------------------------------

    if submit_button:

        has_response = (
            reported_source is not None
            or bool(source_details.strip())
            or shopping_rating is not None
            or bool(customer_feedback.strip())
        )

        if not has_response:

            st.warning(
                "Please answer at least one question "
                "or skip the survey."
            )

        else:

            try:

                save_feedback(
                    order_id=order_id,
                    reported_source=reported_source or "",
                    source_details=source_details,
                    shopping_rating=shopping_rating,
                    customer_feedback=customer_feedback
                )

                st.rerun()

            except OSError:

                st.error(
                    "We couldn't save your feedback. "
                    "Please try again."
                )

    # ----------------------------------------------
    # OPTIONAL SKIP BUTTON
    # ----------------------------------------------

    if st.button(
        "Skip for Now",
        key=f"skip_feedback_{order_id}",
        width="stretch"
    ):

        st.session_state[skipped_key] = True

        st.rerun()
