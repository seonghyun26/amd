"""Tests for GROMACSRunner."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from md_agent.tools.gromacs_tools import GROMACSRunner


@pytest.fixture
def runner(tmp_path):
    return GROMACSRunner(gmx_executable="gmx", work_dir=str(tmp_path))


def _mock_proc(returncode: int, stdout: str = "", stderr: str = "") -> MagicMock:
    proc = MagicMock()
    proc.returncode = returncode
    proc.communicate.return_value = (stdout, stderr)
    proc.poll.return_value = returncode
    return proc


class TestGrompp:
    def test_success(self, runner, tmp_path):
        tpr = str(tmp_path / "md.tpr")
        with patch("subprocess.Popen", return_value=_mock_proc(0, stderr="")) as mock_popen:
            result = runner.grompp(
                mdp_file="prod.mdp",
                topology_file="topol.top",
                coordinate_file="conf.gro",
                output_tpr=tpr,
            )
        assert result["success"] is True
        assert result["output_files"]["tpr"] == tpr

    def test_fatal_error_in_stderr(self, runner, tmp_path):
        tpr = str(tmp_path / "md.tpr")
        with patch("subprocess.Popen", return_value=_mock_proc(0, stderr="ERROR: atom not found")):
            result = runner.grompp("a.mdp", "a.top", "a.gro", tpr)
        assert result["success"] is False

    def test_nonzero_returncode(self, runner, tmp_path):
        with patch("subprocess.Popen", return_value=_mock_proc(1, stderr="Fatal error")):
            result = runner.grompp("a.mdp", "a.top", "a.gro", str(tmp_path / "x.tpr"))
        assert result["returncode"] == 1


class TestMdrun:
    def test_starts_nonblocking(self, runner, tmp_path):
        tpr = str(tmp_path / "md.tpr")
        (tmp_path / "md.tpr").touch()
        proc = MagicMock()
        proc.pid = 12345
        proc.poll.return_value = None
        with patch("subprocess.Popen", return_value=proc):
            result = runner.mdrun(tpr_file="md.tpr", output_prefix="md")
        assert result["pid"] == 12345
        assert result["status"] == "running"
        assert runner.is_mdrun_running()

    def test_plumed_flag_included(self, runner, tmp_path):
        (tmp_path / "md.tpr").touch()
        with patch("subprocess.Popen") as mock_popen:
            mock_popen.return_value = MagicMock(pid=1, poll=MagicMock(return_value=None))
            runner.mdrun(tpr_file="md.tpr", output_prefix="md", plumed_file="plumed.dat")
        call_args = mock_popen.call_args[0][0]
        assert "-plumed" in call_args
        assert "plumed.dat" in call_args

    def test_resume_with_cpt_appends(self, runner, tmp_path):
        (tmp_path / "md.tpr").touch()
        (tmp_path / "md.cpt").touch()
        with patch("subprocess.Popen") as mock_popen:
            mock_popen.return_value = MagicMock(pid=1, poll=MagicMock(return_value=None))
            result = runner.mdrun(tpr_file="md.tpr", output_prefix="md", cpt_file="md.cpt")
        call_args = mock_popen.call_args[0][0]
        assert "-cpi" in call_args
        assert "-append" in call_args
        assert result["status"] == "running"

    def test_resume_missing_cpt_returns_error(self, runner, tmp_path):
        (tmp_path / "md.tpr").touch()
        result = runner.mdrun(tpr_file="md.tpr", output_prefix="md", cpt_file="nonexistent.cpt")
        assert "error" in result
        assert "Checkpoint file not found" in result["error"]

    def test_missing_tpr_returns_error(self, runner, tmp_path):
        result = runner.mdrun(tpr_file="nonexistent.tpr", output_prefix="md")
        assert "error" in result
        assert "TPR file not found" in result["error"]


class TestConvertTpr:
    def test_extend_time(self, runner, tmp_path):
        (tmp_path / "md.tpr").touch()
        with patch("subprocess.Popen", return_value=_mock_proc(0)) as mock_popen:
            result = runner.convert_tpr(
                input_tpr="md.tpr", output_tpr="md_ext.tpr", extend_time=5000.0
            )
        assert result["success"] is True
        assert result["output_files"]["tpr"] == "md_ext.tpr"
        call_args = mock_popen.call_args[0][0]
        assert "convert-tpr" in call_args
        assert "-extend" in call_args
        assert "5000.0" in call_args

    def test_nsteps(self, runner, tmp_path):
        (tmp_path / "md.tpr").touch()
        with patch("subprocess.Popen", return_value=_mock_proc(0)):
            result = runner.convert_tpr(
                input_tpr="md.tpr", output_tpr="md_ext.tpr", nsteps=100000
            )
        assert result["success"] is True

    def test_missing_tpr_returns_error(self, runner, tmp_path):
        result = runner.convert_tpr(
            input_tpr="nonexistent.tpr", output_tpr="out.tpr", extend_time=1000
        )
        assert "error" in result

    def test_no_extension_param_returns_error(self, runner, tmp_path):
        (tmp_path / "md.tpr").touch()
        result = runner.convert_tpr(input_tpr="md.tpr", output_tpr="out.tpr")
        assert "error" in result
