#!/bin/bash

# 设置默认值
AUDIO_DIR="audio_data"
OUTPUT_DIR="audio_data/wav"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 显示帮助信息
show_help() {
    echo "音频处理工具"
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -l, --list             列出所有原始音频文件"
    echo "  -c, --convert [文件]    将原始音频转换为 WAV 格式"
    echo "  -p, --play [文件]       播放 WAV 文件"
    echo "  -h, --help             显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --list                    # 列出所有原始音频文件"
    echo "  $0 --convert audio_123.raw   # 转换指定的音频文件"
    echo "  $0 --play audio_123.wav      # 播放指定的 WAV 文件"
}

# 列出所有原始音频文件
list_files() {
    echo "原始音频文件列表:"
    echo "----------------"
    if [ -d "$AUDIO_DIR" ]; then
        find "$AUDIO_DIR" -name "*.raw" -type f | while read -r file; do
            filename=$(basename "$file")
            echo "$filename"
        done
    else
        echo "错误: 目录 $AUDIO_DIR 不存在"
    fi
}

# 转换音频文件
convert_audio() {
    local input_file="$1"
    local input_path="$AUDIO_DIR/$input_file"
    local output_file="${input_file%.raw}.wav"
    local output_path="$OUTPUT_DIR/$output_file"

    if [ ! -f "$input_path" ]; then
        echo "错误: 文件 $input_path 不存在"
        return 1
    fi

    echo "正在转换: $input_file -> $output_file"
    ffmpeg -f f32le -ar 48000 -i "$input_path" -acodec pcm_s16le "$output_path" -y
    if [ $? -eq 0 ]; then
        echo "转换完成: $output_path"
    else
        echo "错误: 转换失败"
    fi
}

# 播放音频文件
play_audio() {
    local file="$1"
    local file_path="$OUTPUT_DIR/$file"

    if [ ! -f "$file_path" ]; then
        echo "错误: 文件 $file_path 不存在"
        return 1
    fi

    echo "正在播放: $file"
    ffplay -autoexit "$file_path"
}

# 主程序
case "$1" in
    -l|--list)
        list_files
        ;;
    -c|--convert)
        if [ -z "$2" ]; then
            echo "错误: 请指定要转换的文件"
            show_help
            exit 1
        fi
        convert_audio "$2"
        ;;
    -p|--play)
        if [ -z "$2" ]; then
            echo "错误: 请指定要播放的文件"
            show_help
            exit 1
        fi
        play_audio "$2"
        ;;
    -h|--help)
        show_help
        ;;
    *)
        echo "错误: 未知选项"
        show_help
        exit 1
        ;;
esac 