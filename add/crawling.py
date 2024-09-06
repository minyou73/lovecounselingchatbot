import pandas as pd
import yt_dlp
import whisper
import os

# 엑셀 파일 경로 설정 (로컬 경로)
file_path = 'youtube_videos.xlsx'  # 로컬 경로에 있는 파일 이름

# 엑셀 파일 읽기
df = pd.read_excel(file_path)

# 링크 추출 (엑셀 파일의 '링크' 컬럼에서 링크를 가져옵니다)
video_links = df['링크'].tolist()

# Whisper 모델 로드
model = whisper.load_model("base")

# yt-dlp를 사용한 YouTube 오디오 다운로드 함수
def download_youtube_audio(url, output_path='audio.mp3'):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        # 다운로드된 파일이 실제로 audio.mp3.mp3로 저장될 수 있으므로 이름 변경
        if os.path.exists(output_path + ".mp3"):
            os.rename(output_path + ".mp3", output_path)
        print(f"Audio downloaded successfully: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

# 오디오 파일을 텍스트로 변환하는 함수
def transcribe_audio_to_text(audio_file, language="ko"):
    try:
        result = model.transcribe(audio_file, language=language)
        text = result["text"]
        print("Transcription completed successfully.")
        return text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

# 각 동영상을 처리하여 내용 컬럼에 추가
content_list = []  # 내용을 저장할 리스트
for index, video_url in enumerate(video_links):
    print(f"Processing video {index + 1}/{len(video_links)}: {video_url}")
    
    # 오디오 다운로드
    audio_file = download_youtube_audio(video_url)
    
    if audio_file:
        # 텍스트로 변환
        transcribed_text = transcribe_audio_to_text(audio_file)
        
        if transcribed_text:
            content_list.append(transcribed_text)
        else:
            content_list.append("Failed to transcribe the video.")
        
        # 오디오 파일 삭제
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"Temporary audio file {audio_file} has been deleted.")
    else:
        content_list.append("Failed to download the video.")

# 새로운 '내용' 컬럼에 텍스트 추가
df['내용'] = content_list

# 결과를 새로운 엑셀 파일로 저장 (로컬 경로)
output_file_path = 'youtube_videos_with_content.xlsx'
df.to_excel(output_file_path, index=False)
print(f"Processed Excel file saved to: {output_file_path}")
