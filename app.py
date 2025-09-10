import streamlit as st
import pickle
import pandas as pd
import time

# --- FRONT-END ENHANCEMENTS ---
st.set_page_config(
    page_title="Song Recommender",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown(
    """
    <style>
    /* Global Background */
    .stApp {
        background-color: #FFFCF5;
        font-family: 'Comic Sans MS', 'Poppins', sans-serif;
        color: #374375;
    }

    /* Header */
    .main-header {
        text-align: center;
        color: #374375;
        font-size: 3.2rem;
        font-weight: bold;
        text-shadow: 2px 2px 6px rgba(186,189,226,0.5);
    }
    .subheader {
        text-align: center;
        color: #895115;
        font-size: 1.3rem;
        font-style: italic;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        background-color: #DFAEA1;
        color: white;
        border-radius: 25px;
        border: none;
        padding: 12px 26px;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 6px 10px rgba(55,67,117,0.2);
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #BABDE2;
        color: #374375;
        transform: scale(1.05);
    }

    /* Selectbox */
    .stSelectbox [data-baseweb="select"] {
        border-radius: 20px;
        border: 2px solid #BABDE2;
        background-color: #FFF;
        box-shadow: 0 3px 6px rgba(55,67,117,0.1);
    }

    /* Cute Cursor */
    * {
        cursor: url('https://cur.cursors-4u.net/nature/nat-11/nat1044.cur'), auto !important;
    }

    /* Recommendations Styling */
    .song-card {
        background: #BABDE2;
        color: #374375;
        margin: 10px auto;
        padding: 15px;
        border-radius: 18px;
        font-size: 1.1rem;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(55,67,117,0.2);
        transition: transform 0.2s;
        max-width: 600px;
        text-align: center;
    }
    .song-card:hover {
        background: #DFAEA1;
        color: white;
        transform: translateY(-4px);
    }

    /* Spotify Player Styling */
    .spotify-container {
        margin: 15px auto;
        max-width: 600px;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 6px 12px rgba(55,67,117,0.2);
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #895115;
        margin-top: 50px;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True
)

# --- HEADER ---
st.markdown('<h1 class="main-header">🎧 Song Recommender</h1>', unsafe_allow_html=True)
st.markdown('<p class="subheader">✨ Discover new songs based on your current favorites ✨</p>', unsafe_allow_html=True)
st.write("---")

# --- LOAD DATA ---
songs_dict = pickle.load(open('songs.pkl', 'rb'))
songs = pd.DataFrame(songs_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# --- INITIALIZE SESSION STATE (MUST BE EARLY) ---
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'show_recommendations' not in st.session_state:
    st.session_state.show_recommendations = False


# --- SPOTIFY EMBED FUNCTION ---
def display_spotify_player(track_id, song_name):
    """Display Spotify embed player for a track"""
    if track_id and str(track_id) != 'nan':
        embed_url = f"https://open.spotify.com/embed/track/{track_id}?utm_source=generator&theme=0"

        st.markdown(f"""
            <div class="spotify-container">
                <iframe src="{embed_url}" 
                        width="100%" 
                        height="152" 
                        frameBorder="0" 
                        allowfullscreen="" 
                        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
                        loading="lazy">
                </iframe>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"🎵 Spotify player not available for '{song_name}'")


# --- RECOMMENDER FUNCTION ---
def recommend(song):
    song_index = songs[songs['track_name'] == song].index[0]
    distances = similarity[song_index]
    songs_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_songs = []
    for i in songs_list:
        song_data = songs.iloc[i[0]]
        recommended_songs.append({
            'name': song_data['track_name'],
            'index': i[0]
        })

    return recommended_songs


# --- UI LAYOUT ---
col1, col2 = st.columns([3, 1])

with col1:
    selected_song_name = st.selectbox(
        "🎵 Choose a song:",
        songs['track_name'].values)

with col2:
    st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
    recommend_button = st.button('Recommend')

# --- HANDLE RECOMMENDATIONS ---
if recommend_button:
    if selected_song_name:
        with st.spinner('Finding your next favorite songs...'):
            time.sleep(1)

        st.success('🌟 Recommendations Found!')
        st.markdown("---")

        # Store recommendations in session state
        st.session_state.recommendations = recommend(selected_song_name)
        st.session_state.show_recommendations = True

# --- DISPLAY RECOMMENDATIONS ---
if st.session_state.show_recommendations and len(st.session_state.recommendations) > 0:
    st.subheader("Top 5 Recommended Songs")

    for i, song_data in enumerate(st.session_state.recommendations):
        song_name = song_data['name']
        song_index = song_data['index']

        # Display song card
        st.markdown(f"<div class='song-card'>{i + 1}. {song_name}</div>", unsafe_allow_html=True)

        # Create play button
        play_key = f"play_song_{i}_{song_index}"
        if st.button("🎵 Play", key=play_key):
            # Get track ID and display player
            try:
                track_id = songs.loc[song_index, 'track_id']
                st.markdown("### Now Playing:")
                display_spotify_player(track_id, song_name)
            except KeyError:
                st.warning("⚠️ Track ID column not found in dataset.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

        st.markdown("---")

# --- FOOTER ---
st.markdown(
    '<div class="footer">🎶 A machine learning project built with Python & Streamlit 🎶</div>',
    unsafe_allow_html=True
)
