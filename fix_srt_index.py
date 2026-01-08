import pysrt

INPUT_FILE = "files/output/v29-0.5-sim.srt"
OUTPUT_FILE = "files/output/v29-fixed.srt"

def fix_srt_indexes(input_file, output_file):
    subs = pysrt.open(input_file, encoding='utf-8')
    
    # Re-index all subtitles sequentially starting from 1
    for idx, sub in enumerate(subs, start=1):
        sub.index = idx
    
    # Optional: clean overlapping times (pysrt has a clean method)
    # subs.clean_indexes()  # just to be sure

    subs.save(output_file, encoding='utf-8')
    print(f"✔ Re-indexed SRT saved to: {output_file}")

if __name__ == "__main__":
    fix_srt_indexes(INPUT_FILE, OUTPUT_FILE)
