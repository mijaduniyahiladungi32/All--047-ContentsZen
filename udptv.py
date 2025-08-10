import requests
import re
from datetime import datetime

# Configuration
SOURCE_URL = "https://cdn.djdoolky76.net/m9L6CtgDVC.m3u"  # New playlist URL
EPG_URL = "https://zipline.nocn.ddnsfree.com/u/merged2_epg.xml.gz"  # EPG guide URL
OUTPUT_FILE = "UDPTV.m3u"  # Output filename
GROUP_TITLE = "UDPTV Live Streams"  # Standardized group title

def download_playlist():
    """Download the playlist from source URL"""
    try:
        response = requests.get(SOURCE_URL, timeout=15)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.RequestException as e:
        print(f"[❌] Download failed: {e}")
        exit(1)

def clean_playlist(lines):
    """Clean and process the playlist lines"""
    cleaned = []
    i = 0
    total_channels = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Process EXTINF lines
        if line.startswith("#EXTINF"):
            # Standardize group title
            if 'group-title=' in line:
                line = re.sub(r'group-title=".*?"', f'group-title="{GROUP_TITLE}"', line)
            else:
                line = line.replace("#EXTINF:", f"#EXTINF:-1 group-title=\"{GROUP_TITLE}\",")
            
            cleaned.append(line)
            
            # Add the channel URL if available
            if i+1 < len(lines) and not lines[i+1].startswith("#"):
                cleaned.append(lines[i+1].strip())
                total_channels += 1
                i += 1  # Skip the URL line in next iteration
                
        # Keep non-metadata lines
        elif not line.startswith(("#EXTM3U", "#EXTGRP", "#EXTVLCOPT", "#", "Last Updated")):
            cleaned.append(line)
            
        i += 1
    
    print(f"[ℹ] Found {total_channels} channels in playlist")
    return cleaned

def save_playlist(content):
    """Save the processed playlist to file"""
    header = f"""#EXTM3U url-tvg="{EPG_URL}"
# Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(content))
    print(f"[✔] Playlist saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    print("[↓] Downloading playlist...")
    playlist_lines = download_playlist()
    
    print("[♻] Processing playlist...")
    processed_playlist = clean_playlist(playlist_lines)
    
    print("[💾] Saving playlist...")
    save_playlist(processed_playlist)
    
    print("[✅] Done! Enjoy your streams!")
