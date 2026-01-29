import os
import subprocess as sp
import unittest
from pathlib import Path, PurePath


class TestExample(unittest.TestCase):
    """Tests all the example programs in the examples directory."""
    tests_dir: Path = Path(os.path.abspath(__file__)).parent
    gmatpyplus_dir: Path = tests_dir.parent
    examples_folder_name: str = 'examples'
    examples_dir: Path = gmatpyplus_dir / examples_folder_name

    def run_file(self, file: Path):
        command: list[str] = ['python', file, 'PYTHONUNBUFFERED=1']

        try:
            # Returns a sp.CompletedProcess or raises a sp.CalledProcessError.
            sp.run(command,
                   capture_output=True,
                   check=True
                   )

        except sp.CalledProcessError as e:
            return_code = e.returncode
            stderr_text = e.stderr.decode('utf-8').rstrip()

            print(f'stderr_text: "{stderr_text}"')
            raise self.failureException(f'Failed with return code {return_code} and the stderr below:\n\n'
                                        f'"{stderr_text}"') from None

    def test_all_examples(self):
        print(f'{TestExample.examples_dir = }')
        example_files: list[Path] = list(TestExample.examples_dir.rglob('*.py'))

        # Run each example and check it returns a return code of 0, denoting a successful run.
        for example in example_files:
            self.test_example(example)


if __name__ == '__main__':
    unittest.main()
    pass
