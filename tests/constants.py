#!usr/bin/env python3

### MusicQueue  ###
TIME_TO_FETCH_MUSIC = 8  # seconds
EMPTY_MUSIC = ""
MUSIC_1 = "a"
MUSIC_2 = "b"
MUSIC_3 = "c"
MUSIC_4 = "d"
MUSIC_5 = "e"
MUSIC_EMPTY_LIST = []
MUSIC_SINGLE_ELEMENT_LIST = [
    MUSIC_1,
]
MUSIC_SIMPLE_LIST_1 = [
    MUSIC_1,
    MUSIC_2,
]
MUSIC_SIMPLE_LIST_2 = [
    MUSIC_1,
    MUSIC_2,
    MUSIC_3,
]
MUSIC_SIMPLE_LIST_3 = [
    MUSIC_1,
    MUSIC_2,
    MUSIC_3,
    MUSIC_4,
    MUSIC_5,
]
MUSIC_COMPLEX_LIST_1 = [
    MUSIC_1,
    MUSIC_2,
    MUSIC_3,
    MUSIC_2,
    MUSIC_4,
]

### Player ###

# Youtube
YOUTUBE_URL_NO_HTTPS = "http://www.youtube.com/watch?v=1V_xRb0x9aw"
YOUTUBE_URL_1 = "https://www.youtube.com/watch?v=1V_xRb0x9aw"
YOUTUBE_URL_2 = "https://www.youtube.com/watch?v=imSefM4GPpE"
YOUTUBE_URL_3 = "https://www.youtube.com/watch?v=04mfKJWDSzI"
YOUTUBE_URL_4 = "https://www.youtube.com/watch?v=04WuoQMhhxw"
YOUTUBE_URL_5 = "https://www.youtube.com/watch?v=LFTE4W--Htk"
YOUTUBE_URL_SIMPLE_LIST = [
    YOUTUBE_URL_1,
    YOUTUBE_URL_2,
    YOUTUBE_URL_3,
]
YOUTUBE_URL_COMPLEX_LIST = [
    YOUTUBE_URL_1,
    YOUTUBE_URL_2,
    YOUTUBE_URL_3,
    YOUTUBE_URL_4,
    YOUTUBE_URL_5,
]
YOUTUBE_PLAYLIST_SOURCE_1 = (
    "https://www.youtube.com/playlist?list=PL4lCao7KL_QFVb7Iudeipvc2BCavECqzc"
)
YOUTUBE_PLAYLIST_1 = "https://www.youtube.com/watch?v=BaW_jenozKc&list=PL4lCao7KL_QFVb7Iudeipvc2BCavECqzc&index=1"
YOUTUBE_PLAYLIST_SOURCE_2 = (
    "https://www.youtube.com/playlist?list=PLhpLyZ-aL82gssiK-uYP71UD5vgm_T-ZK"
)
YOUTUBE_PLAYLIST_2 = "https://www.youtube.com/watch?v=sgLvV2pX9V0&list=PLhpLyZ-aL82gssiK-uYP71UD5vgm_T-ZK"
YOUTUBE_PLAYLIST_SOURCE_3 = (
    "https://www.youtube.com/playlist?list=PLh_2AL0cs37xUwRGScAmHpCY_vxKlgqRB"
)
YOUTUBE_PLAYLIST_3 = "https://www.youtube.com/watch?v=_-uMPb63e8U&list=PLh_2AL0cs37xUwRGScAmHpCY_vxKlgqRB"
YOUTUBE_QUERY_0 = ""
YOUTUBE_QUERY_1 = "yellow"
YOUTUBE_QUERY_2 = "submarine"

# Spotify
SPOTIFY_URL_NO_HTTPS = "http://open.spotify.com/track/7gaA3wERFkFkgivjwbSvkG"
SPOTIFY_URL_1 = "https://open.spotify.com/track/7gaA3wERFkFkgivjwbSvkG"
SPOTIFY_URL_2 = "https://open.spotify.com/track/3ZFTkvIE7kyPt6Nu3PEa7V"
SPOTIFY_URL_3 = "https://open.spotify.com/track/6y4GYuZszeXNOXuBFsJlos"
SPOTIFY_PLAYLIST_1 = "https://open.spotify.com/playlist/5137tjFBaaMh9dcH8i9fHR"
SPOTIFY_ALBUM_1 = "https://open.spotify.com/album/1amYhlukNF8WdaQC3gKkgL"

### States ###
IDLE_TIMEOUT = 2
