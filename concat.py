import sys
from pydub import AudioSegment

def main(current_wav_path, output_mp3_path):
    start = AudioSegment.from_file("new_start.mp3")
    current = AudioSegment.from_file(current_wav_path)
    end = AudioSegment.from_file("new_end.mp3")
    crossfade_duration = 6000  # 2秒

    # new_start 分段
    start_head = start[:-crossfade_duration]   # 前面不重疊的部分
    start_tail = start[-crossfade_duration:]   # 最後要 fade out 的部分

    # current 分段
    current_head = current[:crossfade_duration]  # 要重疊的前 2 秒
    current_body = current[crossfade_duration:]  # 其餘

    # 將 start_tail fade out，音量逐漸降到 0
    start_tail_faded = start_tail.fade_out(crossfade_duration)

    # 混音，讓 current 的前兩秒直接 overlay 在 new_start 的最後兩秒（保證 current 音量不變）
    cross = start_tail_faded.overlay(current_head)

    # 合併
    merged = start_head + cross + current_body + end

    # 輸出
    merged.export(output_mp3_path, format="mp3")
    print(f"合成完成: {output_mp3_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python3 concat.py current.wav out.mp3")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])

