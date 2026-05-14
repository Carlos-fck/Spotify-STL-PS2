import urllib.parse

def convert_spotify_link_to_code_url(spotify_url):
    # Parse the URL
    parsed_url = urllib.parse.urlparse(spotify_url)
    path_parts = parsed_url.path.strip('/').split('/')
    
    if len(path_parts) < 2:
        raise ValueError("Invalid Spotify URL format")
    
    # Extract type and ID
    item_type = path_parts[0]  # artist, track, album, playlist, etc.
    item_id = path_parts[1]    # unique ID

    # Construct the Spotify URI
    spotify_uri = f"spotify:{item_type}:{item_id}"

    # Construct the encoded download URL
    # Format: https://www.spotifycodes.com/downloadCode.php?uri=svg%2FFFFFFF%2Fblack%2F640%2Fspotify%3A{type}%3A{id}
    encoded_uri = urllib.parse.quote(f"svg/FFFFFF/black/640/{spotify_uri}", safe='')

    final_url = f"https://www.spotifycodes.com/downloadCode.php?uri={encoded_uri}"
    return {
        "type": item_type,
        "id": item_id,
        "spotify_uri": spotify_uri,
        "code_url": final_url
    }

# Example usage
spotify_link = "https://open.spotify.com/album/31hcgCSu4mlA82syOFItur?si=eTuJ8XMcQ0Wnxsus6zoZ9g"
result = convert_spotify_link_to_code_url(spotify_link)

print("Type:", result["type"])
print("ID:", result["id"])
print("Spotify URI:", result["spotify_uri"])
print("Download URL:", result["code_url"])