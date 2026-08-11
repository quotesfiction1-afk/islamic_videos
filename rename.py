import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"}
UR_PATTERN = re.compile(r"^ur-(\d{6})$", re.IGNORECASE)
BASE_URL = "https://github.com/quotesfiction1-afk/islamic_videos"
CATEGORY = "Reminder"


def is_video_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS


def get_existing_numbers(files: list[Path]) -> list[int]:
    numbers: list[int] = []
    for file in files:
        match = UR_PATTERN.match(file.stem)
        if match:
            numbers.append(int(match.group(1)))
    return numbers


def rename_new_files(files: list[Path]) -> None:
    existing_numbers = get_existing_numbers(files)
    next_num = max(existing_numbers, default=0) + 1

    files_to_rename = sorted(
        file
        for file in files
        if not UR_PATTERN.match(file.stem)
    )

    for file in files_to_rename:
        new_name = f"ur-{next_num:06d}{file.suffix.lower()}"
        new_path = file.with_name(new_name)

        while new_path.exists():
            next_num += 1
            new_name = f"ur-{next_num:06d}{file.suffix.lower()}"
            new_path = file.with_name(new_name)

        file.rename(new_path)
        print(f"Renamed '{file.name}' to '{new_name}'")
        next_num += 1


def build_manifest(files: list[Path]) -> dict:
    videos = []

    for file in sorted(files, key=lambda path: path.stem):
        match = UR_PATTERN.match(file.stem)
        if not match:
            continue

        video_id = file.stem.lower()
        videos.append(
            {
                "id": video_id,
                "category": CATEGORY,
                "url": f"{BASE_URL}/{video_id}{file.suffix.lower()}",
            }
        )

    return {"videos": videos}


def write_manifest() -> None:
    files = [file for file in BASE_DIR.iterdir() if is_video_file(file)]
    manifest = build_manifest(files)
    manifest_path = BASE_DIR / "reels.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Created/updated '{manifest_path.name}' with {len(manifest['videos'])} records")


def rename_files() -> None:
    files = [file for file in BASE_DIR.iterdir() if is_video_file(file)]
    rename_new_files(files)
    write_manifest()


if __name__ == "__main__":
    rename_files()
