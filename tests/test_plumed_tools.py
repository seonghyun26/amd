"""Tests for PlumedGenerator."""

import pytest

from md_agent.tools.plumed_tools import PlumedGenerator


@pytest.fixture
def gen():
    return PlumedGenerator()


@pytest.fixture
def distance_cv():
    return {"name": "d1", "type": "DISTANCE", "atoms": [1, 100]}


@pytest.fixture
def torsion_cv():
    return {"name": "phi", "type": "TORSION", "atoms": [5, 7, 9, 15]}


class TestGenerateMetadynamics:
    def test_creates_file(self, gen, tmp_path, distance_cv):
        out = str(tmp_path / "plumed.dat")
        result = gen.generate_metadynamics(
            output_path=out,
            cvs=[distance_cv],
            hills_height=1.2,
            hills_sigma=[0.35],
            hills_pace=500,
            biasfactor=10,
            temperature=300,
        )
        assert result["success"] is True
        content = open(out).read()
        assert "METAD" in content
        assert "d1: DISTANCE" in content
        assert "BIASFACTOR=10" in content
        assert "FLUSH" in content

    def test_sigma_length_mismatch(self, gen, tmp_path, distance_cv, torsion_cv):
        result = gen.generate_metadynamics(
            output_path=str(tmp_path / "p.dat"),
            cvs=[distance_cv, torsion_cv],
            hills_height=1.0,
            hills_sigma=[0.35],  # only 1 sigma for 2 CVs
            hills_pace=500,
        )
        assert "error" in result

    def test_standard_metadynamics_no_biasfactor(self, gen, tmp_path, distance_cv):
        out = str(tmp_path / "plumed.dat")
        result = gen.generate_metadynamics(
            output_path=out, cvs=[distance_cv],
            hills_height=1.0, hills_sigma=[0.3], hills_pace=500,
            biasfactor=None,
        )
        assert result["success"] is True
        content = open(out).read()
        assert "BIASFACTOR" not in content


class TestGenerateUmbrella:
    def test_creates_file(self, gen, tmp_path, distance_cv):
        out = str(tmp_path / "umbrella.dat")
        result = gen.generate_umbrella(
            output_path=out,
            cv_definition=distance_cv,
            window_center=2.0,
            force_constant=1000.0,
        )
        assert result["success"] is True
        content = open(out).read()
        assert "RESTRAINT" in content
        assert "AT=2.0" in content
        assert "KAPPA=1000.0" in content


class TestGenerateSteered:
    def test_creates_file(self, gen, tmp_path, distance_cv):
        out = str(tmp_path / "steered.dat")
        result = gen.generate_steered(
            output_path=out,
            cv_definition=distance_cv,
            initial_value=1.0,
            final_value=4.0,
            force_constant=500.0,
            total_steps=1000000,
        )
        assert result["success"] is True
        content = open(out).read()
        assert "MOVINGRESTRAINT" in content
        assert "AT0=1.0" in content
        assert "AT1=4.0" in content
