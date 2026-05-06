# Packaging guide

This guide details the steps for building and releasing a new version of the gmatpyplus library on GitHub and PyPI. See
also the official [Python packaging user guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

1. Squash merge into the `main` branch any pull requests that are to be included in the release.
2. Update the local `main` branch with:
    ```commandline
    git switch main
    git fetch origin -p
    git pull
    ```

3. Add a new tag for the release version and push it to GitHub. For example, for a new version of 0.10.5:
    ```commandline
    git tag v0.10.5
    git push --tags
   ``` 
   **Note:** the tag name includes the leading `v`.
4. Ensure no modified/new files are showing in PyCharm's/VS Code's commit panel. If there are any, and you want to save
   them, run `git stash`.
5. Build the wheel and archive binaries for the new release with `hatch build`. These will be saved into the `dist`
   folder. Check the names for the generated files are in the format `gmatpyplus-version_number.tar.gz` and
   `gmatpyplus-version_number-py3-none-any.whl`. For example, for a tag of `v0.10.5`, these must be:
   ```commandline
   gmatpyplus-0.10.4.tar.gz
   gmatpyplus-0.10.4-py3-none-any.whl
   ```
   **Note:** any additional file name parts will trigger PyPI to block them. If the files do have
   any extra parts (e.g. in `gmatpyplus-0.10.4.post1.dev2+g532096d3d.tar.gz` or
   `gmatpyplus-0.10.4.post1.dev2+g532096d3d-py3-none-any.whl`), you have skipped step 4, so go back and try again.
6. In GitHub, go to the [releases](https://github.com/weasdown/gmatpyplus/releases) page and click "Draft a new
   release".

   a. Under the "Tag" dropdown, select the new tag you just pushed to GitHub.

   b. Add an appropriate title. If the release has a single pull request, you can base the release title on the pull
   request title.

   c. Click "Generate release notes" to automatically generate release notes describing the difference between the new
   tag and the previous one. Before the text that this adds in the text box, add a summary of the release.

   d. Add the `.whl` and `.tar.gz` files generated earlier by dragging them into the "Attach binaries by dropping them
   here or selecting them." box.

   e. Click "Publish release" when ready to publish the release on GitHub. It will then be visible on
   the [releases page](https://github.com/weasdown/gmatpyplus/releases) and on the right of
   the [repository page](https://github.com/weasdown/gmatpyplus).

7. To add the release to the project's [PyPI page](https://pypi.org/project/gmatpyplus/), run `twine upload dist/*`. *
   *Note:** this will attempt to upload **all** files in the `dist` folder, including any for previous versions. You can
   only upload the new version by running `twine upload dist/*[version]*`, e.g. `twine upload dist/*0.10.5*`. Paste in
   your PyPI API token. If you get an `HTTPError: 400 Bad Request`, check the generated file names from step 5. Once
   complete, the release will be visible on the [PyPI page](https://pypi.org/project/gmatpyplus/).
