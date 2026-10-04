import json
import streamlit as st
from google import genai
from google.genai import types
from twilio.rest import Client as TwilioClient

from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    SUMMARY_REQUEST_PROMPT
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MacroSnap",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# COSMIC UI
# =========================================================

st.markdown("""
<style>

/* =====================================================
   GOOGLE FONTS
   ===================================================== */

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');


/* =====================================================
   MAIN BACKGROUND
   ===================================================== */

.stApp {

    background-color: #050b18;

    background-image:

        /* large blue glow */
        radial-gradient(
            circle at 15% 20%,
            rgba(32, 83, 145, 0.45) 0%,
            rgba(32, 83, 145, 0.15) 20%,
            transparent 42%
        ),

        /* golden glow */
        radial-gradient(
            circle at 82% 20%,
            rgba(190, 139, 53, 0.28) 0%,
            rgba(190, 139, 53, 0.08) 18%,
            transparent 40%
        ),

        /* lower blue glow */
        radial-gradient(
            circle at 70% 90%,
            rgba(24, 65, 125, 0.35),
            transparent 40%
        ),

        /* stars */
        radial-gradient(
            circle at 10% 15%,
            rgba(255,255,255,0.8) 0px,
            transparent 1px
        ),
        radial-gradient(
            circle at 25% 70%,
            rgba(255,220,150,0.7) 0px,
            transparent 1px
        ),
        radial-gradient(
            circle at 45% 30%,
            rgba(255,255,255,0.7) 0px,
            transparent 1px
        ),
        radial-gradient(
            circle at 70% 12%,
            rgba(255,255,255,0.7) 0px,
            transparent 1px
        ),
        radial-gradient(
            circle at 90% 45%,
            rgba(255,220,150,0.7) 0px,
            transparent 1px
        ),
        radial-gradient(
            circle at 55% 82%,
            rgba(255,255,255,0.6) 0px,
            transparent 1px
        );

    background-size:
        auto,
        auto,
        auto,
        180px 180px,
        240px 240px,
        210px 210px,
        280px 280px,
        220px 220px,
        250px 250px;

    color: #eee8dc;

    font-family: 'DM Sans', sans-serif;
}


/* =====================================================
   MAIN CONTENT
   ===================================================== */

.block-container {

    max-width: 1250px;

    padding-top: 2rem;
    padding-bottom: 5rem;
}


/* =====================================================
   TEXT
   ===================================================== */

h1,
h2,
h3 {

    font-family: 'Playfair Display', serif !important;

    color: #f4ead7 !important;

    letter-spacing: -0.5px;
}

h1 {

    font-size: 3.2rem !important;

    line-height: 1.1 !important;
}

h2 {

    font-size: 2rem !important;
}

h3 {

    font-size: 1.35rem !important;
}

p,
label {

    color: #c9c2b6;
}

.stCaption {

    color: #8f99a9 !important;
}


/* =====================================================
   SIDEBAR
   ===================================================== */

section[data-testid="stSidebar"] {

    background:

        radial-gradient(
            circle at 80% 10%,
            rgba(176, 126, 44, 0.16),
            transparent 30%
        ),

        linear-gradient(
            180deg,
            #071021 0%,
            #030814 100%
        );

    border-right: 1px solid rgba(203, 157, 74, 0.22);
}

section[data-testid="stSidebar"] * {

    color: #d9d3c8;
}


/* =====================================================
   INPUT BOXES
   ===================================================== */

.stTextInput input,
.stTextArea textarea {

    background: rgba(10, 19, 36, 0.82) !important;

    color: #f1eadf !important;

    border: 1px solid rgba(192, 150, 72, 0.35) !important;

    border-radius: 14px !important;

    min-height: 48px;

    box-shadow:
        inset 0 0 20px rgba(0,0,0,0.15);
}


.stTextInput input::placeholder {

    color: #778294 !important;
}


.stTextInput input:focus,
.stTextArea textarea:focus {

    border-color: #d0a24f !important;

    box-shadow:
        0 0 0 1px #d0a24f,
        0 0 20px rgba(208,162,79,0.15) !important;
}


/* =====================================================
   BUTTONS
   ===================================================== */

.stButton > button {

    background:

        linear-gradient(
            135deg,
            #d4a64f,
            #9d6c24
        ) !important;

    color: #090d16 !important;

    border: 1px solid #e0b866 !important;

    border-radius: 14px !important;

    min-height: 46px;

    font-weight: 700 !important;

    box-shadow:
        0 5px 25px rgba(190, 139, 53, 0.22);

    transition: all 0.25s ease;
}


.stButton > button:hover {

    transform: translateY(-2px);

    box-shadow:
        0 8px 30px rgba(210, 164, 77, 0.38);

    border-color: #f1ce83 !important;
}


/* =====================================================
   FORM
   ===================================================== */

[data-testid="stForm"] {

    background:

        linear-gradient(
            145deg,
            rgba(13, 27, 49, 0.92),
            rgba(5, 12, 25, 0.92)
        );

    border: 1px solid rgba(205, 160, 74, 0.30);

    border-radius: 26px;

    padding: 2rem;

    box-shadow:
        0 20px 70px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.04);
}


/* =====================================================
   CHAT MESSAGES
   ===================================================== */

[data-testid="stChatMessage"] {

    border-radius: 20px;

    padding: 0.8rem 1rem;

    margin-bottom: 12px;

    border: 1px solid rgba(177, 148, 91, 0.15);

    box-shadow:
        0 8px 30px rgba(0,0,0,0.15);
}


/* Assistant */

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-assistant"]
) {

    background:

        linear-gradient(
            135deg,
            rgba(16, 34, 62, 0.92),
            rgba(7, 17, 33, 0.92)
        );
}


/* User */

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-user"]
) {

    background:

        linear-gradient(
            135deg,
            rgba(74, 57, 27, 0.60),
            rgba(30, 25, 18, 0.85)
        );

    border-color:
        rgba(210, 165, 78, 0.20);
}


/* =====================================================
   CHAT INPUT
   ===================================================== */

[data-testid="stChatInput"] {

    background: transparent !important;
}


[data-testid="stChatInput"] textarea {

    background:

        linear-gradient(
            135deg,
            rgba(11, 22, 40, 0.96),
            rgba(5, 12, 25, 0.96)
        ) !important;

    color: #eee7da !important;

    border: 1px solid
        rgba(205, 160, 74, 0.40) !important;

    border-radius: 18px !important;

    box-shadow:
        0 10px 35px rgba(0,0,0,0.35),
        inset 0 0 20px rgba(0,0,0,0.2);
}


/* =====================================================
   FILE UPLOADER
   ===================================================== */

[data-testid="stFileUploader"] {

    background:
        rgba(8, 18, 34, 0.75);

    border:
        1px dashed rgba(206, 162, 77, 0.35);

    border-radius: 16px;

    padding: 0.7rem;
}


/* =====================================================
   DIVIDER
   ===================================================== */

hr {

    border-color:
        rgba(205, 160, 74, 0.18) !important;
}


/* =====================================================
   ALERTS
   ===================================================== */

div[data-testid="stAlert"] {

    border-radius: 14px !important;
}


/* =====================================================
   SELECT / OTHER CONTROLS
   ===================================================== */

div[data-baseweb="select"] > div {

    background: #0b1629 !important;

    border-color:
        rgba(205, 160, 74, 0.3) !important;

    color: #eee !important;
}


/* =====================================================
   DECORATIVE COSMIC PANEL
   ===================================================== */

.cosmic-panel {

    background:

        radial-gradient(
            circle at 50% 50%,
            rgba(46, 87, 144, 0.30),
            transparent 40%
        ),

        linear-gradient(
            135deg,
            rgba(14, 31, 56, 0.92),
            rgba(4, 10, 22, 0.95)
        );

    border:
        1px solid rgba(210, 165, 78, 0.28);

    border-radius: 30px;

    padding: 2.2rem;

    box-shadow:
        0 25px 80px rgba(0,0,0,0.45);
}


/* =====================================================
   GOLD TEXT
   ===================================================== */

.gold-text {

    color: #d7a951;
}


/* =====================================================
   STATUS
   ===================================================== */

.status {

    color: #d9b76b;

    font-size: 0.78rem;

    font-weight: 600;

    letter-spacing: 1.5px;

    text-transform: uppercase;
}


/* =====================================================
   MOBILE
   ===================================================== */

@media (max-width: 768px) {

    h1 {

        font-size: 2.3rem !important;
    }

    .block-container {

        padding-left: 1rem;
        padding-right: 1rem;
    }

}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SETTINGS
# =========================================================

MODEL_NAME = "gemini-3.5-flash"

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
TWILIO_WHATSAPP_FROM = st.secrets["TWILIO_WHATSAPP_FROM"]
TWILIO_CONTENT_SID = st.secrets["TWILIO_CONTENT_SID"]


# =========================================================
# CLIENTS
# =========================================================

twilio_client = TwilioClient(
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN
)


@st.cache_resource
def get_gemini_client():

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


gemini_client = get_gemini_client()


# =========================================================
# FUNCTIONS
# =========================================================

def add_message(role, kind, content):

    st.session_state.messages.append({

        "role": role,

        "kind": kind,

        "content": content

    })


def render_message(message):

    avatar = (
        "🥗"
        if message["role"] == "assistant"
        else "👤"
    )

    with st.chat_message(
        message["role"],
        avatar=avatar
    ):

        if message["kind"] == "text":

            st.write(
                message["content"]
            )

        elif message["kind"] == "image":

            st.image(
                message["content"],
                width=420
            )


def clean_whatsapp_text(text):

    if not text:

        return "No nutrition summary available."

    text = " ".join(
        text.split()
    )

    if len(text) > 1500:

        text = text[:1500] + "..."

    return text


def send_whatsapp(
    to_number,
    user_name,
    summary
):

    try:

        content_variables = json.dumps({

            "1": user_name,

            "2": clean_whatsapp_text(
                summary
            )

        })

        message = twilio_client.messages.create(

            from_=TWILIO_WHATSAPP_FROM,

            to=f"whatsapp:{to_number}",

            content_sid=TWILIO_CONTENT_SID,

            content_variables=content_variables

        )

        return True, message.sid

    except Exception as error:

        return False, str(error)


# =========================================================
# LOGIN / ONBOARDING
# =========================================================

if "onboarded" not in st.session_state:

    st.write("")

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        st.markdown(
            '<p class="status">✦ AI NUTRITION COMPANION ✦</p>',
            unsafe_allow_html=True
        )

        st.title("MacroSnap")

        st.markdown(
            """
            ### Your meals have a story.

            <span style="color:#aeb8c8;">
            Let AI help you discover the calories,
            macros and nutrition behind every meal.
            </span>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        with st.container(border=True):

            st.subheader(
                "Enter your details"
            )

            st.caption(
                "Set up your personal nutrition space."
            )

            with st.form("onboarding_form"):

                name = st.text_input(
                    "Your name",
                    placeholder="e.g. Uma"
                )

                whatsapp_number = st.text_input(
                    "WhatsApp number",
                    placeholder="+91XXXXXXXXXX"
                )

                st.caption(
                    "We'll use this number only when you "
                    "send your nutrition summary."
                )

                st.write("")

                submitted = st.form_submit_button(
                    "Enter MacroSnap  ✦",
                    use_container_width=True
                )

                if submitted:

                    if (
                        not name.strip()
                        or not whatsapp_number.strip()
                    ):

                        st.warning(
                            "Please enter both your name "
                            "and WhatsApp number."
                        )

                    else:

                        st.session_state.name = (
                            name.strip()
                        )

                        st.session_state.whatsapp_number = (
                            whatsapp_number.strip()
                        )

                        st.session_state.chat = (
                            gemini_client.chats.create(

                                model=MODEL_NAME,

                                config=types.GenerateContentConfig(

                                    system_instruction=SYSTEM_PROMPT

                                )

                            )
                        )

                        st.session_state.messages = []

                        st.session_state.onboarded = True

                        st.rerun()

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '<p class="status">✦ MACROSNAP</p>',
        unsafe_allow_html=True
    )

    st.title(
        "Nutrition Space"
    )

    st.write("")

    st.caption(
        "SIGNED IN AS"
    )

    st.markdown(
        f"### {st.session_state.name}"
    )

    st.divider()

    st.markdown(
        """
        **What you can do**

        📸 **Scan a meal**  
        Upload a food photo.

        ✦ **Estimate nutrition**  
        Get calories and macros.

        💬 **Ask questions**  
        Talk with your AI nutrition buddy.

        📲 **Send to WhatsApp**  
        Save your nutrition summary.
        """
    )

    st.divider()

    st.caption(
        "MacroSnap AI • Your nutrition companion"
    )


# =========================================================
# MAIN HEADER
# =========================================================

header_left, header_right = st.columns(
    [5, 2]
)


with header_left:

    st.markdown(
        '<p class="status">✦ PERSONAL AI NUTRITION SPACE</p>',
        unsafe_allow_html=True
    )

    st.title(
        "MacroSnap"
    )

    st.caption(
        f"Welcome back, {st.session_state.name}."
    )


with header_right:

    st.write("")

    if st.button(
        "📲 Send to WhatsApp",
        use_container_width=True
    ):

        with st.spinner(
            "Creating your summary..."
        ):

            try:

                summary_response = (
                    st.session_state.chat.send_message(
                        SUMMARY_REQUEST_PROMPT
                    )
                )

                summary = summary_response.text

            except Exception as error:

                st.error(
                    f"Could not create summary: {error}"
                )

                st.stop()

        success, info = send_whatsapp(

            st.session_state.whatsapp_number,

            st.session_state.name,

            summary

        )

        if success:

            st.success(
                "Summary sent to WhatsApp ✦"
            )

        else:

            st.error(
                f"Couldn't send: {info}"
            )


st.divider()


# =========================================================
# CHAT TITLE
# =========================================================

chat_left, chat_right = st.columns(
    [5, 1]
)

with chat_left:

    st.subheader(
        "Nutrition Conversation"
    )

with chat_right:

    st.markdown(
        '<p class="status">● AI ONLINE</p>',
        unsafe_allow_html=True
    )


# =========================================================
# WELCOME MESSAGE
# =========================================================

for message in st.session_state.messages:

    render_message(message)


if not st.session_state.messages:

    welcome = WELCOME_MESSAGE_TEMPLATE.format(
        name=st.session_state.name
    )

    add_message(
        "assistant",
        "text",
        welcome
    )

    render_message(
        st.session_state.messages[-1]
    )


# =========================================================
# CHAT INPUT
# =========================================================

user_input = st.chat_input(

    "Ask about your meal or attach a photo...",

    accept_file=True,

    file_type=[
        "jpg",
        "jpeg",
        "png"
    ]

)


# =========================================================
# USER MESSAGE
# =========================================================

if user_input:

    photo = (
        user_input.files[0]
        if user_input.files
        else None
    )

    text = user_input.text

    parts = []


    # IMAGE

    if photo is not None:

        photo_bytes = photo.getvalue()

        add_message(
            "user",
            "image",
            photo_bytes
        )

        parts.append(

            types.Part.from_bytes(

                data=photo_bytes,

                mime_type=photo.type

            )

        )


    # TEXT

    if text:

        add_message(
            "user",
            "text",
            text
        )

        parts.append(text)


    # IMAGE ONLY

    elif photo is not None:

        parts.append(
            """
            Analyze this meal.

            Tell me:

            1. What food is visible?
            2. Estimated calories
            3. Estimated protein
            4. Estimated carbohydrates
            5. Estimated fat

            Keep the explanation simple and practical.
            Clearly mention that the values are estimates.
            """
        )


    # GEMINI

    with st.spinner(
        "Reading your meal..."
    ):

        try:

            response = (
                st.session_state.chat.send_message(
                    parts
                )
            )

            answer = response.text

        except Exception as error:

            answer = (
                "Sorry, I couldn't process that right now.\n\n"
                f"Error: {error}"
            )


    # SAVE RESPONSE

    add_message(
        "assistant",
        "text",
        answer
    )

    render_message(
        st.session_state.messages[-1]
    )