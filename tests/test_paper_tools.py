"""Tests for paper retrieval and settings extraction."""

import json
from unittest.mock import MagicMock, patch

import pytest

from md_agent.utils.parsers import convert_units, normalize_extracted_settings


class TestUnitConversion:
    def test_kcal_to_kj(self):
        assert convert_units(1.0, "kcal/mol", "kJ/mol") == pytest.approx(4.184)

    def test_angstrom_to_nm(self):
        assert convert_units(10.0, "Å", "nm") == pytest.approx(1.0)

    def test_identity(self):
        assert convert_units(5.0, "nm", "nm") == pytest.approx(5.0)

    def test_unsupported_raises(self):
        with pytest.raises(ValueError):
            convert_units(1.0, "parsec", "nm")


class TestNormalizeExtractedSettings:
    def test_kcal_hills_converted(self):
        settings = {
            "plumed": {
                "hills_height": 1.0,
                "hills_height_unit": "kcal/mol",
            }
        }
        result = normalize_extracted_settings(settings)
        assert result["plumed"]["hills_height"] == pytest.approx(4.184)
        assert "hills_height_unit" not in result["plumed"]

    def test_angstrom_sigma_converted(self):
        settings = {
            "plumed": {
                "hills_sigma": [3.5, 5.0],
                "sigma_unit": "Å",
            }
        }
        result = normalize_extracted_settings(settings)
        assert result["plumed"]["hills_sigma"][0] == pytest.approx(0.35)
        assert result["plumed"]["hills_sigma"][1] == pytest.approx(0.5)

    def test_no_conversion_needed(self):
        settings = {
            "plumed": {
                "hills_height": 1.2,
            }
        }
        result = normalize_extracted_settings(settings)
        assert result["plumed"]["hills_height"] == pytest.approx(1.2)


class TestMDSettingsExtractor:
    def _make_extractor(self, response_text: str):
        from md_agent.tools.paper_tools import MDSettingsExtractor

        mock_client = MagicMock()
        mock_block = MagicMock()
        mock_block.text = response_text
        mock_block.type = "text"
        mock_response = MagicMock()
        mock_response.content = [mock_block]
        mock_client.messages.create.return_value = mock_response
        return MDSettingsExtractor(mock_client)

    def test_extracts_valid_json(self):
        response = json.dumps({
            "method": "metadynamics",
            "gromacs": {"dt": 0.002, "temperature": 300},
            "plumed": {"hills_height": 1.2, "hills_sigma": [0.35], "hills_pace": 500},
            "system": {"forcefield": "charmm36m"},
            "notes": "",
            "confidence": "high",
        })
        extractor = self._make_extractor(response)
        result = extractor.extract_md_settings_from_text("paper text")
        assert result["method"] == "metadynamics"
        assert result["gromacs"]["temperature"] == 300

    def test_handles_no_json_in_response(self):
        extractor = self._make_extractor("I cannot find simulation parameters.")
        result = extractor.extract_md_settings_from_text("text")
        assert "error" in result
