import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from video_gen.cli.gen_interactive import InteractiveGenerator, InteractiveState
from video_gen.core.types import PresetDimension, OptimizationMode


class TestInteractiveState:
    def test_default_state(self):
        state = InteractiveState()
        assert state.visual_preset is None
        assert state.time_preset is None
        assert state.images == []
        assert state.description == ""
        assert state.mode == OptimizationMode.FAST
        assert state.current_step == 0
        assert state.history == []

    def test_state_with_values(self):
        state = InteractiveState(
            visual_preset="realistic",
            time_preset="normal",
            images=["/path/to/image.jpg"],
            description="test description",
            mode=OptimizationMode.QUALITY,
        )
        assert state.visual_preset == "realistic"
        assert state.time_preset == "normal"
        assert state.images == ["/path/to/image.jpg"]
        assert state.description == "test description"
        assert state.mode == OptimizationMode.QUALITY


class TestInteractiveGenerator:
    def test_init(self):
        gen = InteractiveGenerator()
        assert gen._config is not None
        assert gen._registry is not None
        assert gen._state is not None
        assert gen.TOTAL_STEPS == 5

    def test_step_handlers_defined(self):
        gen = InteractiveGenerator()
        assert len(gen._step_handlers) == 5
        assert 0 in gen._step_handlers
        assert 1 in gen._step_handlers
        assert 2 in gen._step_handlers
        assert 3 in gen._step_handlers
        assert 4 in gen._step_handlers

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    @patch('video_gen.cli.gen_interactive.console.print')
    def test_step_visual_style_select_first(self, mock_print, mock_prompt):
        gen = InteractiveGenerator()
        mock_prompt.return_value = "1"
        
        result = gen._step_visual_style()
        
        assert result == "next"
        assert gen._state.visual_preset == "realistic"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    def test_step_visual_style_skip(self, mock_prompt):
        gen = InteractiveGenerator()
        mock_prompt.return_value = ""
        
        result = gen._step_visual_style()
        
        assert result == "skip"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    def test_step_visual_style_back(self, mock_prompt):
        gen = InteractiveGenerator()
        mock_prompt.return_value = "back"
        
        result = gen._step_visual_style()
        
        assert result == "back"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    @patch('video_gen.cli.gen_interactive.console.print')
    def test_step_time_sampling_select(self, mock_print, mock_prompt):
        gen = InteractiveGenerator()
        mock_prompt.return_value = "1"
        
        result = gen._step_time_sampling()
        
        assert result == "next"
        assert gen._state.time_preset == "timelapse"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    def test_step_time_sampling_skip(self, mock_prompt):
        gen = InteractiveGenerator()
        mock_prompt.return_value = ""
        
        result = gen._step_time_sampling()
        
        assert result == "skip"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    def test_step_upload_images_with_valid_path(self, mock_prompt, tmp_path):
        gen = InteractiveGenerator()
        test_file = tmp_path / "test.jpg"
        test_file.touch()
        mock_prompt.return_value = str(test_file)
        
        result = gen._step_upload_images()
        
        assert result == "next"
        assert str(test_file) in gen._state.images

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    def test_step_upload_images_skip(self, mock_prompt):
        gen = InteractiveGenerator()
        mock_prompt.return_value = ""
        
        result = gen._step_upload_images()
        
        assert result == "skip"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    def test_step_upload_images_back(self, mock_prompt):
        gen = InteractiveGenerator()
        mock_prompt.return_value = "back"
        
        result = gen._step_upload_images()
        
        assert result == "back"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    def test_step_description_with_text(self, mock_prompt):
        gen = InteractiveGenerator()
        mock_prompt.return_value = "A beautiful sunset over the ocean"
        
        result = gen._step_description()
        
        assert result == "next"
        assert gen._state.description == "A beautiful sunset over the ocean"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    def test_step_description_skip(self, mock_prompt):
        gen = InteractiveGenerator()
        mock_prompt.return_value = ""
        
        result = gen._step_description()
        
        assert result == "skip"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    def test_step_description_back(self, mock_prompt):
        gen = InteractiveGenerator()
        mock_prompt.return_value = "back"
        
        result = gen._step_description()
        
        assert result == "back"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    @patch('video_gen.cli.gen_interactive.console.print')
    def test_step_confirm_yes(self, mock_print, mock_prompt):
        gen = InteractiveGenerator()
        gen._state.images = ["/path/to/image.jpg"]
        mock_prompt.return_value = "y"
        
        result = gen._step_confirm()
        
        assert result == "done"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    @patch('video_gen.cli.gen_interactive.console.print')
    def test_step_confirm_back(self, mock_print, mock_prompt):
        gen = InteractiveGenerator()
        mock_prompt.return_value = "back"
        
        result = gen._step_confirm()
        
        assert result == "back"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    @patch('video_gen.cli.gen_interactive.console.print')
    def test_step_confirm_cancel(self, mock_print, mock_prompt):
        gen = InteractiveGenerator()
        mock_prompt.return_value = "n"
        
        result = gen._step_confirm()
        
        assert result == "cancel"

    def test_build_result(self):
        gen = InteractiveGenerator()
        gen._state.visual_preset = "realistic"
        gen._state.time_preset = "normal"
        gen._state.images = ["/path/to/image.jpg"]
        gen._state.description = "test description"
        gen._state.mode = OptimizationMode.QUALITY
        
        result = gen._build_result()
        
        assert result["visual"] == "realistic"
        assert result["time"] == "normal"
        assert result["images"] == ["/path/to/image.jpg"]
        assert result["description"] == "test description"
        assert result["mode"] == OptimizationMode.QUALITY

    def test_build_result_empty(self):
        gen = InteractiveGenerator()
        
        result = gen._build_result()
        
        assert result["visual"] is None
        assert result["time"] is None
        assert result["images"] == []
        assert result["description"] == ""
        assert result["mode"] == OptimizationMode.FAST

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    @patch('video_gen.cli.gen_interactive.console.print')
    def test_run_complete_flow(self, mock_print, mock_prompt):
        gen = InteractiveGenerator()
        
        mock_prompt.side_effect = [
            "1",
            "2",
            "",
            "test description",
            "y",
        ]
        
        with patch.object(Path, 'exists', return_value=True):
            result = gen.run()
        
        assert result is not None
        assert result["visual"] == "realistic"
        assert result["time"] == "slow_motion"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    def test_run_with_back_navigation(self, mock_prompt):
        gen = InteractiveGenerator()
        
        mock_prompt.side_effect = [
            "1",
            "back",
            "1",
            "",
            "",
            "",
            "y",
        ]
        
        result = gen.run()
        
        assert result is not None
        assert result["visual"] == "realistic"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    def test_run_cancel_at_confirm(self, mock_prompt):
        gen = InteractiveGenerator()
        
        mock_prompt.side_effect = [
            "1",
            "2",
            "",
            "",
            "n",
        ]
        
        result = gen.run()
        
        assert result is not None

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    @patch('video_gen.cli.gen_interactive.console.print')
    def test_edit_params_mode(self, mock_print, mock_prompt):
        gen = InteractiveGenerator()
        gen._state.mode = OptimizationMode.FAST
        
        mock_prompt.side_effect = ["5", "quality", "y"]
        
        result = gen._edit_params()
        
        assert gen._state.mode == OptimizationMode.QUALITY

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    def test_invalid_selection_retry(self, mock_prompt):
        gen = InteractiveGenerator()
        
        mock_prompt.side_effect = ["invalid", "1"]
        
        result = gen._step_visual_style()
        
        assert result == "next"
        assert gen._state.visual_preset == "realistic"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    def test_out_of_range_selection_retry(self, mock_prompt):
        gen = InteractiveGenerator()
        
        mock_prompt.side_effect = ["99", "1"]
        
        result = gen._step_visual_style()
        
        assert result == "next"
        assert gen._state.visual_preset == "realistic"

    @patch('video_gen.cli.gen_interactive.Prompt.ask')
    def test_multiple_images_input(self, mock_prompt, tmp_path):
        gen = InteractiveGenerator()
        
        file1 = tmp_path / "image1.jpg"
        file2 = tmp_path / "image2.jpg"
        file1.touch()
        file2.touch()
        
        mock_prompt.return_value = f"{file1}, {file2}"
        
        result = gen._step_upload_images()
        
        assert result == "next"
        assert len(gen._state.images) == 2