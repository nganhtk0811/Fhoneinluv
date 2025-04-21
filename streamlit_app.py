
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="1fda60773c3344c188c7a3bea0c8eb58",
    client_secret="30c823bdd5954e1bb942f8811b1744ae",
    redirect_uri="http://127.0.0.1:8888/callback",  # <-- dùng 127.0.0.1
    scope="playlist-modify-public playlist-modify-private"
))

st.title("🎶 Tìm kiếm nghệ sĩ & Quản lý Playlist Spotify")

# Nhập tên nghệ sĩ
artist_name = st.text_input("🔎 Nhập tên nghệ sĩ:")

if artist_name:
    results = sp.search(q=f"artist:{artist_name}", type="track", limit=10)
    tracks = results['tracks']['items']

    if tracks:
        data = []
        for track in tracks:
            data.append({
                'Tên bài hát': track['name'],
                'Album': track['album']['name'],
                'Thời lượng (giây)': track['duration_ms'] // 1000,
                'ID': track['id']
            })

        df = pd.DataFrame(data)
        st.write("🎧 Danh sách bài hát:")
        st.dataframe(df.drop(columns=['ID']))

        selected = st.multiselect("✅ Chọn bài hát để thêm vào Playlist:", options=df['Tên bài hát'].tolist())
        name_to_id = {row['Tên bài hát']: row['ID'] for _, row in df.iterrows()}

        if selected:
            st.subheader("📂 Chọn hoặc tạo Playlist")

            tab1, tab2 = st.tabs(["🗂 Playlist có sẵn", "🆕 Tạo Playlist mới"])

            with tab1:
                playlists = sp.current_user_playlists()['items']
                playlist_names = [p['name'] for p in playlists]

                chosen_playlist = st.selectbox("📌 Chọn playlist:", playlist_names)
                playlist_id = next(p['id'] for p in playlists if p['name'] == chosen_playlist)

                if st.button("📥 Thêm vào playlist đã chọn"):
                    track_ids = [name_to_id[name] for name in selected]
                    sp.playlist_add_items(playlist_id, track_ids)
                    st.success("✅ Đã thêm vào playlist!")

            with tab2:
                new_name = st.text_input("📄 Nhập tên playlist mới:")
                new_desc = st.text_area("📝 Mô tả playlist (tuỳ chọn):", "")
                is_public = st.checkbox("Công khai", value=True)

                if st.button("🚀 Tạo playlist mới và thêm nhạc"):
                    user_id = sp.current_user()['id']
                    new_playlist = sp.user_playlist_create(
                        user=user_id,
                        name=new_name,
                        public=is_public,
                        description=new_desc
                    )
                    new_playlist_id = new_playlist['id']
                    track_ids = [name_to_id[name] for name in selected]
                    sp.playlist_add_items(new_playlist_id, track_ids)
                    st.success(f"✅ Playlist '{new_name}' đã được tạo và thêm bài hát!")
    else:
        st.warning("⚠️ Không tìm thấy bài hát nào.")
