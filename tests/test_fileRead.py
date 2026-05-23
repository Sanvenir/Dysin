# -*- coding: utf-8 -*-
"""Tests for fileRead module."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fileRead import (
    fileReadNum, fileReadFloat, fileReadStr,
    listReadInt, listReadFloat, listReadStr,
    listReadLines, listReadAllLines,
    fileReadVariable, actionFrameSetting
)


class TestFileReadNum:
    def test_fileReadNum_found(self):
        line = "animeWalkSpeed=30"
        assert fileReadNum(line, "animeWalkSpeed") == 30

    def test_fileReadNum_not_found(self):
        line = "animeWalkSpeed=30"
        assert fileReadNum(line, "other") == 0

    def test_fileReadNum_invalid(self):
        line = "value=abc"
        assert fileReadNum(line, "value") == 0


class TestFileReadFloat:
    def test_fileReadFloat_found(self):
        line = "volume=0.75"
        assert fileReadFloat(line, "volume") == 0.75

    def test_fileReadFloat_not_found(self):
        line = "volume=0.75"
        assert fileReadFloat(line, "other") == 0.0


class TestListReaders:
    def test_listReadInt_found(self):
        lines = ["other=10", "target=42", "another=20"]
        assert listReadInt(lines, "target") == 42

    def test_listReadInt_not_found(self):
        lines = ["other=10", "another=20"]
        assert listReadInt(lines, "target") == 0

    def test_listReadFloat_found(self):
        lines = ["other=1.5", "target=3.14", "another=2.0"]
        assert listReadFloat(lines, "target") == 3.14

    def test_listReadStr_found(self):
        lines = ["other=text", "target=hello", "another=world"]
        assert listReadStr(lines, "target") == "hello"

    def test_listReadStr_not_found(self):
        lines = ["other=text"]
        assert listReadStr(lines, "target") == ""


class TestListReadLines:
    def test_listReadLines(self):
        lines = ["start", "line1", "line2", "end", "after"]
        result = listReadLines("start", "end", lines)
        assert result == ["line1", "line2"]

    def test_listReadLines_no_end(self):
        lines = ["start", "line1", "line2"]
        result = listReadLines("start", "end", lines)
        assert result == ["line1", "line2"]


class TestListReadAllLines:
    def test_listReadAllLines(self):
        lines = ["start", "a1", "a2", "end", "start", "b1", "b2", "end", "after"]
        result = listReadAllLines("start", "end", lines)
        assert result == [["a1", "a2"], ["b1", "b2"]]


class TestFileReadVariable:
    def test_fileReadVariable_basic(self, tmp_path):
        content = "NAME=Dysin\nVERSION=1.0\n"
        f = tmp_path / "test.cfg"
        f.write_text(content, encoding='utf-8')
        
        result = fileReadVariable(str(f))
        assert result["NAME"] == "Dysin"
        assert result["VERSION"] == "1.0"


class TestActionFrameSetting:
    def test_actionFrameSetting(self):
        lines = ["action=0,1,2,3"]
        result = actionFrameSetting(lines, "action")
        assert result == [0, 1, 2, 3]

    def test_actionFrameSetting_single(self):
        lines = ["action=5"]
        result = actionFrameSetting(lines, "action")
        assert result == [5]
