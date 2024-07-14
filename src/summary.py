import ollama
import argparse
from pathlib import Path
from transformers import pipeline
import yt_dlp

OLLAMA_MODEL = "llama3"

# Function to download a video from YouTube using yt-dlp
def download_from_youtube(url: str, path: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(Path(path) / 'to_transcribe.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Function to transcribe an audio file using the transformers pipeline
def transcribe_file(file_path: str, output_file: str) -> str:
    # Load the pipeline model for automatic speech recognition with MPS
    transcriber_gpu = pipeline("automatic-speech-recognition", model="openai/whisper-large-v2", device="mps")
    
    # Transcribe the audio file
    transcribe = transcriber_gpu(file_path)
    
    # Save the transcribed text to the specified temporary file
    with open(output_file, 'w') as tmp_file:
        tmp_file.write(transcribe["text"])
        print(f"Transcription saved to file: {output_file}")
    
    # Return the transcribed text
    return transcribe["text"]

# Function to summarize a text using the Ollama model
def summarize_text(text: str, output_path: str) -> str:
    # Define the system prompt for the Ollama model
    system_prompt = f"I would like for you to assume the role of a Technical Expert"
    # Define the user prompt for the Ollama model
    user_prompt = f"""Generate a concise summary of the text below.
    Text : {text}
    Add a title to the summary.
    Make sure your summary has useful and true information about the main points of the topic.
    Begin with a short introduction explaining the topic. If you can, use bullet points to list important details,
    and finish your summary with a concluding sentence."""

    # Use the Ollama model to generate a summary
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )
    # Print the generated summary
    return response["message"]["content"]

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Download, transcribe, and summarize audio or video files.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--from-youtube", type=str, help="YouTube URL to download.")
    group.add_argument("--from-local", type=str, help="Path to the local audio file.")
    parser.add_argument("--output", type=str, default="./summary.md", help="Output markdown file path.")
    parser.add_argument("--transcript-only", action='store_true', help="Only transcribe the file, do not summarize.")
    
    args = parser.parse_args()
    
    # Set up data directory
    data_directory = Path("tmp")
    # Check if the directory exists, if not, create it
    if not data_directory.exists():
        data_directory.mkdir(parents=True)
        print(f"Created directory: {data_directory}")
  
    if args.from_youtube:
        # Download from YouTube
        print(f"Downloading YouTube video from {args.from_youtube}")
        download_from_youtube(args.from_youtube, str(data_directory))
        file_path = data_directory / "to_transcribe.mp3"
    elif args.from_local:
        # Use local file
        file_path = Path(args.from_local)
    
    print(f"Transcribing file: {file_path}")
    # Transcribe the audio file
    transcript = transcribe_file(str(file_path), data_directory / "transcript.txt")
    
    if args.transcript_only:
        print("Transcription complete. Skipping summary generation.")
        return
    
    print("Generating summary...")
    # Generate summary
    summary = summarize_text(transcript, "./")
    
    # Write summary to a markdown file
    with open(args.output, "w") as md_file:
        md_file.write("# Summary\n\n")
        md_file.write(summary)
        print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
