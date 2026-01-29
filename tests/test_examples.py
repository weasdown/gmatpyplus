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

            # try:
            #     # process: sp.CompletedProcess = sp.run(['python', example], stdout=sp.PIPE, stderr=sp.PIPE)
            #     # # process.check_returncode()
            #     # err = process.stderr
            #
            #     p: sp.Popen = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE)
            #     # output = sp.check_call(command)
            #     results = p.communicate()
            #     out = results[0]
            #     err = results[1]
            #     code = p.returncode
            #     print('\nResults:\n'
            #           f'\t- stdout: {out}\n'
            #           f'\t- stderr: {err}\n'
            #           f'\t- return code: {code}')
            #
            #     return out, err, code
            #
            # except CalledProcessError as cpe:
            #     print('Got CPE!')
            #     print(f'output: {cpe.output}')
            #     print(f'cpe.stderr: {cpe.stderr}')
            #     print(f'cause: {cpe.__cause__}')
            #     raise cpe
            #
            # except Exception:
            #     print('Got an exception!')
            #     raise

        with self.subTest(example_path_relative):
            # try:
            # stdout, stderr, return_code = run_file(example)
            run_file(example)
            # stdout = process.stdout
            # stderr = process.stderr
            # return_code = process.returncode

            # if stderr:
            #     print(type(stderr))
            #     # raise stderr
            #     sys.exit(1)
            #     # self.fail(f'{example_path_relative} failed raised an exception!\n{e}')

            #     self.assertEqual(return_code, 0,
            #                      f'Example {example_path_relative} failed with:\n'
            #                      f'\t- return code {return_code},\n'
            #                      f'\t- stdout {stdout},\n'
            #                      f'\t- stderr {stderr}.')

            # except Exception as ex:
            #     self.fail(f'{example_path_relative} raised an exception!\n{ex}')

            pass
        print(f'\n### Completed testing of example {example_path_relative} ###\n')

    def test_all_examples(self):
        print(f'{TestExample.examples_dir = }')
        example_files: list[Path] = list(TestExample.examples_dir.rglob('*.py'))

        # Run each example and check it returns a return code of 0, denoting a successful run.
        for example in example_files:
            self.test_example(example)


if __name__ == '__main__':
    unittest.main()
    pass
