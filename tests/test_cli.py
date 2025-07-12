import shutil
from pathlib import Path
import pytest
from typer.testing import CliRunner
from safai.main import app
from yaml import dump

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
    (SAMPLE_DIR / "Order 123.docx").write_text("Order")
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
    mock_ret_val = dump(
        {
            "Documents": [
                "MeetingMinutes.docx",
                "ResearchPaper.pdf",
                "ProjectPlan.xlsx",
                "Order_123.docx",
                "PresentationDraft.pptx",
            ],
            "Media": {
                "Images": ["VacationPhoto.jpg", "CompanyLogo.png"],
                "Audio": ["LectureRecording.mp3"],
                "Video": ["ProductDemo.mp4"],
            },
            "SystemFiles": ["SoftwareUpdate.exe", "SystemBackup.iso"],
        },
        default_flow_style=False,
        sort_keys=False,
    )

    # test extra explanation added scenario
    mock_ret_val = "---\n" + mock_ret_val + "--- \nSome explaination from LLM"

    if platform == "openai":
        mocker.patch("safai.model_proxy.openai.Client", autospec=True)
        mocker.patch(
            "safai.model_proxy.openai.OpenaiProxy.get_suggestion",
            return_value=mock_ret_val,
        )
    elif platform == "gemini":
        mocker.patch("safai.model_proxy.gemini.genai.Client", autospec=True)
        mocker.patch(
            "safai.model_proxy.gemini.GeminiProxy.get_suggestion",
            return_value=mock_ret_val,
        )
    elif platform == "claude":
        mocker.patch("safai.model_proxy.claude.Client", autospec=True)
        mocker.patch(
            "safai.model_proxy.claude.ClaudeProxy.get_suggestion",
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
    assert (docs / "Order_123.docx").exists()
    assert (docs / "PresentationDraft.pptx").exists()
    assert (images / "VacationPhoto.jpg").exists()
    assert (images / "CompanyLogo.png").exists()
    assert (audio / "LectureRecording.mp3").exists()
    assert (video / "ProductDemo.mp4").exists()
    assert (system / "SoftwareUpdate.exe").exists()
    assert (system / "SystemBackup.iso").exists()


def test_path_generator_debug():
    from safai.directory_handler.handler import DirectoryHandler

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
    from safai.directory_handler.handler import DirectoryHandler

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
            "Order_123.docx",
            "SoftwareUpdate.exe",
            "ResearchPaper.pdf",
            "MeetingMinutes.docx",
            "VacationPhoto.jpg",
        ],
        ["extra2.png", "extra1.jpg"],
    ]

    for _, v in result.items():
        assert v in expected


def test_parse_suggested_dir_structure():
    test_llm_suggestion = """
    Some extra output
    ---
    Documents:
    - 'Meeting Minutes.docx'
    - 'ResearchPaper.pdf'
    - 'ProjectPlan.xlsx'
    - 'PresentationDraft.pptx'
    Media:
    Images:
        - 'VacationPhoto.jpg'
        - 'CompanyLogo.png'
    Audio:
        - 'LectureRecording.mp3'
    Video:
        - 'ProductDemo.mp4'
    SystemFiles:
    - 'SoftwareUpdate.exe'
    - 'SystemBackup.iso'
    ---
    Further explaination
    """
    
    from safai.model_proxy.model_proxy import ProxyAdapter

    pr = ProxyAdapter(None)
    parsed_suggestions = pr._parse_suggested_dir_structure(test_llm_suggestion)
    
    assert "Documents" in parsed_suggestions
    assert "Meeting Minutes.docx" in parsed_suggestions["Documents"]