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
        example_files: list[Path] = list(TestExample.examples_dir.rglob('*.py'))

        cwd = os.getcwd()

        # Change directory to gmatpyplus library root.
        os.chdir(TestExample.gmatpyplus_dir)

        # Run each example and check it returns a return code of 0, denoting a successful run.
        for example in example_files:
            # Get a short form of the path to the example file, removing the leading '.../.../gmatpyplus/'.
            parts: tuple[str, ...] = PurePath(example).parts
            index_of_examples_dir: int = parts.index('examples')
            parts = parts[index_of_examples_dir:]
            example_path_relative: str = '/'.join(parts)
            print(f'Testing {example_path_relative}')

            with self.subTest(example_path_relative):
                try:
                    self.run_file(example)
                except AssertionError as e:
                    print('\t- Fail!')
                    raise e
                else:
                    print('\t- Pass\n')

        os.chdir(cwd)  # Return to original working directory.


if __name__ == '__main__':
    unittest.main()
    pass
