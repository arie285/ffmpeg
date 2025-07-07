from flask import Flask, request, send_file
import subprocess
import os
import uuid

app = Flask(__name__)

@app.route('/')
def home():
    return 'FFmpeg API is running!'

@app.route('/merge', methods=['POST'])
def merge_videos():
    data = request.json
    video_urls = data.get("videos")

    if not video_urls or len(video_urls) < 2:
        return {"error": "Need at least 2 video URLs"}, 400

    video_files = []
    for i, url in enumerate(video_urls):
        filename = f"video_{i}.mp4"
        try:
            subprocess.run(["curl", "-L", url, "-o", filename], check=True)
            video_files.append(filename)
        except subprocess.CalledProcessError as e:
            return {"error": f"Failed to download {url}", "details": str(e)}, 500

    list_file = "input_list.txt"
    with open(list_file, "w") as f:
        for file in video_files:
            f.write(f"file '{file}'\n")

    output_name = f'merged_{uuid.uuid4().hex[:8]}.mp4'
    command = [
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", list_file, "-c", "copy", output_name
    ]
    result = subprocess.run(command, capture_output=True)

    if result.returncode != 0:
        return {"error": result.stderr.decode()}, 500

    return send_file(output_name, mimetype='video/mp4', as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
