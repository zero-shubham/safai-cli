import os
import shutil
from pathlib import Path
import pytest
import typer
from typer.testing import CliRunner
from main import app

# Paths
TESTS_DIR = Path(__file__).parent
SAMPLE_DIR = TESTS_DIR / "sample_folder"

runner = CliRunner()


@pytest.fixture(autouse=True)
def setup_and_teardown_sample_folder():
    if SAMPLE_DIR.exists():
        shutil.rmtree(SAMPLE_DIR)
    SAMPLE_DIR.mkdir()

    # Documents
    (SAMPLE_DIR / "MeetingMinutes.docx").write_text("Minutes")
    (SAMPLE_DIR / "ResearchPaper.pdf").write_text("Paper")
    (SAMPLE_DIR / "ProjectPlan.xlsx").write_text("Plan")
    (SAMPLE_DIR / "PresentationDraft.pptx").write_text("Draft")
    # Media
    (SAMPLE_DIR / "VacationPhoto.jpg").write_text("Photo")
    (SAMPLE_DIR / "CompanyLogo.png").write_text("Logo")
    (SAMPLE_DIR / "LectureRecording.mp3").write_text("Audio")
    (SAMPLE_DIR / "ProductDemo.mp4").write_text("Video")
    # SystemFiles
    (SAMPLE_DIR / "SoftwareUpdate.exe").write_text("Update")
    (SAMPLE_DIR / "SystemBackup.iso").write_text("Backup")
    # Extra images in a subdirectory
    extra_images_dir = SAMPLE_DIR / "extra_images"
    extra_images_dir.mkdir()
    (extra_images_dir / "extra1.jpg").write_text("Extra Image 1")
    (extra_images_dir / "extra2.png").write_text("Extra Image 2")

    yield
    shutil.rmtree(SAMPLE_DIR)


@pytest.mark.parametrize("platform", ["openai", "claude", "gemini"])
def test_organize_sample_folder(mocker, platform):
    mock_ret_val = {
        "Documents": [
            "MeetingMinutes.docx",
            "ResearchPaper.pdf",
            "ProjectPlan.xlsx",
            "PresentationDraft.pptx",
        ],
        "Media": {
            "Images": ["VacationPhoto.jpg", "CompanyLogo.png"],
            "Audio": ["LectureRecording.mp3"],
            "Video": ["ProductDemo.mp4"],
        },
        "SystemFiles": ["SoftwareUpdate.exe", "SystemBackup.iso"],
    }
    if platform == "openai":
        mocker.patch("src.model_proxy.openai.Client", autospec=True)
        mocker.patch(
            "src.model_proxy.openai.OpenaiProxy.get_suggestion",
            return_value=mock_ret_val,
        )
    elif platform == "gemini":
        mocker.patch("src.model_proxy.gemini.genai.Client", autospec=True)
        mocker.patch(
            "src.model_proxy.gemini.GeminiProxy.get_suggestion",
            return_value=mock_ret_val,
        )
    elif platform == "claude":
        mocker.patch("src.model_proxy.claude.Client", autospec=True)
        mocker.patch(
            "src.model_proxy.claude.ClaudeProxy.get_suggestion",
            return_value=mock_ret_val,
        )

    result = runner.invoke(
        app,
        [
            str(SAMPLE_DIR),
            "--platform",
            platform,
            "--api_key",
            "dummy-key",
            "--model",
            "dummy-model",
            "--one_shot",
        ],
    )
    if result.exit_code != 0:
        print("CLI output:\n", result.output)
    assert result.exit_code == 0

    # Check expected folder structure
    docs = SAMPLE_DIR / "Documents"
    media = SAMPLE_DIR / "Media"
    images = media / "Images"
    audio = media / "Audio"
    video = media / "Video"
    system = SAMPLE_DIR / "SystemFiles"
    assert (docs / "MeetingMinutes.docx").exists()
    assert (docs / "ResearchPaper.pdf").exists()
    assert (docs / "ProjectPlan.xlsx").exists()
    assert (docs / "PresentationDraft.pptx").exists()
    assert (images / "VacationPhoto.jpg").exists()
    assert (images / "CompanyLogo.png").exists()
    assert (audio / "LectureRecording.mp3").exists()
    assert (video / "ProductDemo.mp4").exists()
    assert (system / "SoftwareUpdate.exe").exists()
    assert (system / "SystemBackup.iso").exists()


def test_path_generator_debug():
    from src.directory_handler.handler import DirectoryHandler

    suggestions = {
        "Documents": [
            "MeetingMinutes.docx",
            "ResearchPaper.pdf",
            "ProjectPlan.xlsx",
            "PresentationDraft.pptx",
        ],
        "Media": {
            "Images": [
                "VacationPhoto.jpg",
                "CompanyLogo.png",
                "extra1.jpg",
                "extra2.png",
            ],
            "Audio": ["LectureRecording.mp3"],
            "Video": ["ProductDemo.mp4"],
        },
        "SystemFiles": ["SoftwareUpdate.exe", "SystemBackup.iso"],
    }
    dh = DirectoryHandler(Path("/tmp"), ignore=[])
    paths = list(dh._path_generator(suggestions))
    print("_path_generator output:", paths)
    assert (
        ["Documents"],
        [
            "MeetingMinutes.docx",
            "ResearchPaper.pdf",
            "ProjectPlan.xlsx",
            "PresentationDraft.pptx",
        ],
    ) in paths
    assert (
        ["Media", "Images"],
        ["VacationPhoto.jpg", "CompanyLogo.png", "extra1.jpg", "extra2.png"],
    ) in paths
    assert (["Media", "Audio"], ["LectureRecording.mp3"]) in paths
    assert (["Media", "Video"], ["ProductDemo.mp4"]) in paths
    assert (["SystemFiles"], ["SoftwareUpdate.exe", "SystemBackup.iso"]) in paths


def test_list_directory_files_recursive_nested():
    from src.directory_handler.handler import DirectoryHandler

    dh = DirectoryHandler(SAMPLE_DIR, ignore=[])
    result = dh.list_directory_files(recursive=True)
    print("list_directory_files(recursive=True) output:", result)

    expected = [
        [
            "ProductDemo.mp4",
            "PresentationDraft.pptx",
            "CompanyLogo.png",
            "SystemBackup.iso",
            "LectureRecording.mp3",
            "ProjectPlan.xlsx",
            "SoftwareUpdate.exe",
            "ResearchPaper.pdf",
            "MeetingMinutes.docx",
            "VacationPhoto.jpg",
        ],
        ["extra2.png", "extra1.jpg"],
    ]

    for _, v in result.items():
        assert v in expected
