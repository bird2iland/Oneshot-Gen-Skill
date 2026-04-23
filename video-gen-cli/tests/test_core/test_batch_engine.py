import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile

from video_gen.core.batch_engine import (
    BatchEngine,
    BatchRequest,
    BatchTask,
    BatchResult,
    TaskResult,
    ProgressInfo,
)
from video_gen.core.types import OptimizationMode
from video_gen.core.engine import Config


@pytest.fixture
def batch_engine():
    return BatchEngine()


@pytest.fixture
def sample_yaml_content():
    return """
tasks:
  - visual: realistic
    time: timelapse
    camera: shuttle
    description: "City timelapse"
    images:
      - "image1.jpg"
    duration: 5.0
    ratio: "16:9"
  
  - visual: pixel_art
    description: "Pixel scene"
    images:
      - "image2.jpg"
    duration: 3.0

concurrency: 2
mode: fast
provider: jimeng
output_dir: "./output"
continue_on_error: true
"""


@pytest.fixture
def sample_yaml_file(sample_yaml_content):
    import os
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(sample_yaml_content)
        yield Path(path)
    finally:
        Path(path).unlink(missing_ok=True)


class TestBatchTask:
    def test_batch_task_defaults(self):
        task = BatchTask()
        assert task.images == []
        assert task.visual is None
        assert task.time is None
        assert task.camera is None
        assert task.description == ""
        assert task.duration == 5.0
        assert task.ratio == "16:9"
        assert task.model is None

    def test_batch_task_with_values(self):
        task = BatchTask(
            images=["img1.jpg", "img2.jpg"],
            visual="realistic",
            time="timelapse",
            camera="shuttle",
            description="Test video",
            duration=10.0,
            ratio="9:16",
            model="custom",
        )
        assert task.images == ["img1.jpg", "img2.jpg"]
        assert task.visual == "realistic"
        assert task.time == "timelapse"
        assert task.camera == "shuttle"
        assert task.description == "Test video"
        assert task.duration == 10.0
        assert task.ratio == "9:16"
        assert task.model == "custom"


class TestBatchRequest:
    def test_batch_request_defaults(self):
        request = BatchRequest()
        assert request.tasks == []
        assert request.concurrency == 3
        assert request.mode == OptimizationMode.FAST
        assert request.provider == "jimeng"
        assert request.output_dir is None
        assert request.continue_on_error is True

    def test_batch_request_with_tasks(self):
        tasks = [BatchTask(description="Task 1"), BatchTask(description="Task 2")]
        request = BatchRequest(
            tasks=tasks,
            concurrency=5,
            mode=OptimizationMode.QUALITY,
            provider="custom",
            continue_on_error=False,
        )
        assert len(request.tasks) == 2
        assert request.concurrency == 5
        assert request.mode == OptimizationMode.QUALITY
        assert request.provider == "custom"
        assert request.continue_on_error is False


class TestTaskResult:
    def test_task_result_success(self):
        result = TaskResult(
            index=0,
            success=True,
            video_path="/path/to/video.mp4",
            prompt_path="/path/to/prompt.txt",
            task_id="task-123",
        )
        assert result.index == 0
        assert result.success is True
        assert result.video_path == "/path/to/video.mp4"
        assert result.error is None

    def test_task_result_failure(self):
        result = TaskResult(
            index=1,
            success=False,
            error="Generation failed",
            error_code="GENERATION_ERROR",
        )
        assert result.index == 1
        assert result.success is False
        assert result.error == "Generation failed"
        assert result.error_code == "GENERATION_ERROR"


class TestProgressInfo:
    def test_progress_info(self):
        info = ProgressInfo(
            total=10,
            completed=5,
            succeeded=4,
            failed=1,
            current_index=5,
            current_description="Test task",
        )
        assert info.total == 10
        assert info.completed == 5
        assert info.succeeded == 4
        assert info.failed == 1
        assert info.current_index == 5
        assert info.current_description == "Test task"


class TestBatchResult:
    def test_batch_result_success(self):
        results = [
            TaskResult(index=0, success=True),
            TaskResult(index=1, success=True),
        ]
        result = BatchResult(
            success=True,
            total=2,
            succeeded=2,
            failed=0,
            results=results,
            duration=10.5,
        )
        assert result.success is True
        assert result.total == 2
        assert result.succeeded == 2
        assert result.failed == 0

    def test_batch_result_partial_failure(self):
        results = [
            TaskResult(index=0, success=True),
            TaskResult(index=1, success=False, error="Failed"),
        ]
        result = BatchResult(
            success=False,
            total=2,
            succeeded=1,
            failed=1,
            results=results,
            duration=10.5,
        )
        assert result.success is False
        assert result.total == 2
        assert result.succeeded == 1
        assert result.failed == 1


class TestBatchEngineFromYaml:
    def test_from_yaml_valid(self, batch_engine, sample_yaml_file):
        request = batch_engine.from_yaml(sample_yaml_file)
        
        assert len(request.tasks) == 2
        assert request.concurrency == 2
        assert request.mode == OptimizationMode.FAST
        assert request.provider == "jimeng"
        assert request.output_dir == Path("./output")
        assert request.continue_on_error is True

    def test_from_yaml_task_parsing(self, batch_engine, sample_yaml_file):
        request = batch_engine.from_yaml(sample_yaml_file)
        
        task1 = request.tasks[0]
        assert task1.visual == "realistic"
        assert task1.time == "timelapse"
        assert task1.camera == "shuttle"
        assert task1.description == "City timelapse"
        assert task1.images == ["image1.jpg"]
        assert task1.duration == 5.0
        assert task1.ratio == "16:9"

        task2 = request.tasks[1]
        assert task2.visual == "pixel_art"
        assert task2.description == "Pixel scene"
        assert task2.images == ["image2.jpg"]
        assert task2.duration == 3.0

    def test_from_yaml_file_not_found(self, batch_engine):
        with pytest.raises(FileNotFoundError):
            batch_engine.from_yaml(Path("/nonexistent/file.yaml"))

    def test_from_yaml_missing_tasks(self, batch_engine):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("concurrency: 3\n")
            yaml_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="'tasks' field is required"):
                batch_engine.from_yaml(yaml_path)
        finally:
            yaml_path.unlink(missing_ok=True)

    def test_from_yaml_quality_mode(self, batch_engine):
        yaml_content = """
tasks:
  - description: "Test"
    images: ["img.jpg"]
mode: quality
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_path = Path(f.name)
        
        try:
            request = batch_engine.from_yaml(yaml_path)
            assert request.mode == OptimizationMode.QUALITY
        finally:
            yaml_path.unlink(missing_ok=True)

    def test_from_yaml_single_image_string(self, batch_engine):
        yaml_content = """
tasks:
  - description: "Test"
    images: "single_image.jpg"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_path = Path(f.name)
        
        try:
            request = batch_engine.from_yaml(yaml_path)
            assert request.tasks[0].images == ["single_image.jpg"]
        finally:
            yaml_path.unlink(missing_ok=True)


class TestBatchEngineExecuteBatch:
    @pytest.mark.asyncio
    async def test_execute_batch_empty_tasks(self, batch_engine):
        request = BatchRequest(tasks=[])
        result = await batch_engine.execute_batch(request)
        
        assert result.success is True
        assert result.total == 0
        assert result.succeeded == 0
        assert result.failed == 0

    @pytest.mark.asyncio
    async def test_execute_batch_single_task_success(self, batch_engine):
        mock_engine = MagicMock()
        mock_engine.generate = AsyncMock(return_value={
            "success": True,
            "video_path": "/output/video.mp4",
            "prompt_path": "/output/prompt.txt",
            "task_id": "task-123",
            "error": None,
            "error_code": None,
        })
        batch_engine._engine = mock_engine

        request = BatchRequest(
            tasks=[BatchTask(images=["img.jpg"], description="Test")],
            concurrency=1,
        )
        result = await batch_engine.execute_batch(request)

        assert result.success is True
        assert result.total == 1
        assert result.succeeded == 1
        assert result.failed == 0
        assert len(result.results) == 1
        assert result.results[0].success is True

    @pytest.mark.asyncio
    async def test_execute_batch_single_task_failure(self, batch_engine):
        mock_engine = MagicMock()
        mock_engine.generate = AsyncMock(return_value={
            "success": False,
            "video_path": None,
            "prompt_path": "/output/prompt.txt",
            "task_id": "task-123",
            "error": "Generation failed",
            "error_code": "GENERATION_ERROR",
        })
        batch_engine._engine = mock_engine

        request = BatchRequest(
            tasks=[BatchTask(images=["img.jpg"], description="Test")],
            concurrency=1,
        )
        result = await batch_engine.execute_batch(request)

        assert result.success is False
        assert result.total == 1
        assert result.succeeded == 0
        assert result.failed == 1
        assert result.results[0].error == "Generation failed"

    @pytest.mark.asyncio
    async def test_execute_batch_multiple_tasks_concurrent(self, batch_engine):
        call_count = 0

        async def mock_generate(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return {
                "success": True,
                "video_path": f"/output/video_{call_count}.mp4",
                "prompt_path": f"/output/prompt_{call_count}.txt",
                "task_id": f"task-{call_count}",
            }

        mock_engine = MagicMock()
        mock_engine.generate = mock_generate
        batch_engine._engine = mock_engine

        request = BatchRequest(
            tasks=[
                BatchTask(images=["img1.jpg"], description="Task 1"),
                BatchTask(images=["img2.jpg"], description="Task 2"),
                BatchTask(images=["img3.jpg"], description="Task 3"),
            ],
            concurrency=2,
            continue_on_error=True,
        )
        result = await batch_engine.execute_batch(request)

        assert result.success is True
        assert result.total == 3
        assert result.succeeded == 3
        assert result.failed == 0

    @pytest.mark.asyncio
    async def test_execute_batch_continue_on_error(self, batch_engine):
        results_sequence = [
            {"success": True, "video_path": "/output/video1.mp4", "task_id": "task-1"},
            {"success": False, "error": "Failed", "error_code": "ERROR"},
            {"success": True, "video_path": "/output/video3.mp4", "task_id": "task-3"},
        ]
        call_index = 0

        async def mock_generate(*args, **kwargs):
            nonlocal call_index
            result = results_sequence[call_index]
            call_index += 1
            return result

        mock_engine = MagicMock()
        mock_engine.generate = mock_generate
        batch_engine._engine = mock_engine

        request = BatchRequest(
            tasks=[
                BatchTask(images=["img1.jpg"]),
                BatchTask(images=["img2.jpg"]),
                BatchTask(images=["img3.jpg"]),
            ],
            concurrency=1,
            continue_on_error=True,
        )
        result = await batch_engine.execute_batch(request)

        assert result.success is False
        assert result.total == 3
        assert result.succeeded == 2
        assert result.failed == 1

    @pytest.mark.asyncio
    async def test_execute_batch_stop_on_error(self, batch_engine):
        results_sequence = [
            {"success": True, "video_path": "/output/video1.mp4", "task_id": "task-1"},
            {"success": False, "error": "Failed", "error_code": "ERROR"},
            {"success": True, "video_path": "/output/video3.mp4", "task_id": "task-3"},
        ]
        call_index = 0

        async def mock_generate(*args, **kwargs):
            nonlocal call_index
            result = results_sequence[call_index]
            call_index += 1
            return result

        mock_engine = MagicMock()
        mock_engine.generate = mock_generate
        batch_engine._engine = mock_engine

        request = BatchRequest(
            tasks=[
                BatchTask(images=["img1.jpg"]),
                BatchTask(images=["img2.jpg"]),
                BatchTask(images=["img3.jpg"]),
            ],
            concurrency=1,
            continue_on_error=False,
        )
        result = await batch_engine.execute_batch(request)

        assert result.success is False
        assert result.succeeded == 1
        assert result.failed == 1

    @pytest.mark.asyncio
    async def test_execute_batch_progress_callback(self, batch_engine):
        mock_engine = MagicMock()
        mock_engine.generate = AsyncMock(return_value={
            "success": True,
            "video_path": "/output/video.mp4",
            "task_id": "task-1",
        })
        batch_engine._engine = mock_engine

        progress_calls = []

        def progress_callback(info: ProgressInfo):
            progress_calls.append(info)

        request = BatchRequest(
            tasks=[BatchTask(images=["img.jpg"], description="Test")],
            concurrency=1,
        )
        await batch_engine.execute_batch(request, progress_callback=progress_callback)

        assert len(progress_calls) == 1
        assert progress_calls[0].total == 1
        assert progress_calls[0].current_description == "Test"