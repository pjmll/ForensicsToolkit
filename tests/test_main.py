import unittest
from pathlib import Path
import sys
import os

# 将 src 目录添加到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestProjectStructure(unittest.TestCase):
    def test_src_exists(self):
        self.assertTrue(Path('src').exists())
        self.assertTrue(Path('src/main.py').exists())

    def test_readme_exists(self):
        self.assertTrue(Path('README.md').exists())

    def test_requirements_exists(self):
        self.assertTrue(Path('requirements.txt').exists())

if __name__ == '__main__':
    unittest.main()
