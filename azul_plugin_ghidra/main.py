"""Extracting Features From A Binary Using Ghidra Headless."""

import hashlib
import os
import pathlib
import re
import shutil
import tempfile
import traceback

import pyghidra
from azul_runner import (
    FV,
    BinaryPlugin,
    DataLabel,
    Feature,
    FeatureType,
    Job,
    State,
    add_settings,
    cmdline_run,
)

# Using tempfile.template as this ensures leftover folders get cleaned up by azul runner
# Files can be left over if a timeout occurs.
GHIDRA_PREFIX = f"{tempfile.template}ghidra_"


def find_directory(name, extra_paths=None):
    """Return full path to requested directory."""
    paths = list(os.environ["PATH"].split(os.pathsep))
    if extra_paths:
        paths.extend(extra_paths)
    for p in paths:
        f = os.path.join(p, name)
        if os.path.isdir(f):
            return f
    raise BadGhidraInstallPath(f"Ghidra installation '{name}' not found in path: {paths}")


class BadGhidraInstallPath(Exception):
    """Error raised if Ghidra's installation path can't be found."""

    pass


class AzulPluginGhidra(BinaryPlugin):
    """Extracting Features From A Binary Using Ghidra Headless."""

    VERSION = "2025.12.09"
    SETTINGS = add_settings(
        # Only select text and exectuable files
        filter_data_types={"content": ["executable/windows/"]},
        filter_max_content_size="10MiB",
        max_values_per_feature="3000",  # Generally enough, however there are some binaries that exceed this
        min_length_structure=(int, 100),  # Increasing this value will remove smaller functions from output
        # ghidra config that needs to be removed between runs to prevent build up  of logs
        ghidra_config_path=(str, f"{os.path.expanduser('~')}/.config/ghidra"),
    )
    FEATURES = [
        Feature(
            "ghidra_func_structure_hash",
            desc="Taking the md5 hash of the bracket and operand structure of each function decompiled by Ghidra",
            type=FeatureType.String,
        ),
        Feature(
            "ghidra_placeholder_func_name",
            desc="The placeholder name assigned by Ghidra to an unrecognised function",
            type=FeatureType.String,
        ),
        Feature(
            "ghidra_recognised_func_name",
            desc="The name assigned by Ghidra to a recognised function",
            type=FeatureType.String,
        ),
    ]

    ghidra_plugin_path = "ghidra"

    def process_function(self, function, output, outfile):
        """Processing functions ghidra decompiles."""
        function_structure = "".join(re.findall(r"[{}\[\]()\+\=\*\-\/\!\%\;]", str(output)))
        if len(function_structure) >= self.cfg.min_length_structure:
            outfile.write("//Function: " + str(function))
            outfile.write(output)
            md5_hash = hashlib.md5((function_structure).encode("utf-8")).hexdigest()  # noqa: S324

            # Separating recognised and placeholder functions
            name = function.getName()
            if name.startswith("FUN_") or name.startswith("sub_"):
                self.add_feature_values(
                    "ghidra_func_structure_hash", FV(str(md5_hash), label=("Function: " + str(function)))
                )
                self.add_feature_values(
                    "ghidra_placeholder_func_name", FV(str(function), label=("Structure Hash: " + str(md5_hash)))
                )
            else:
                self.add_feature_values(
                    "ghidra_func_structure_hash", FV(str(md5_hash), label=("Function: " + str(function)))
                )
                self.add_feature_values(
                    "ghidra_recognised_func_name", FV(str(function), label=("Structure Hash: " + str(md5_hash)))
                )

            return 1
        else:
            return 0

    def run_ghidra(self, binary_path: str, output_path: str, project_path: str):
        """Handles accessing ghidra headless mode, running it, and parsing decompiled output."""
        # Opens program from the desired path in the ghidra instance started with .start() method.
        # iterates through functions found in the binary and outputs their decompilation to an output file

        # Initialising ghidra in headless mode
        pyghidra.start(verbose=True)
        from ghidra.app.decompiler import DecompInterface
        from ghidra.util.task import ConsoleTaskMonitor

        decomp_interface = None
        try:
            with pyghidra.open_program(binary_path, analyze=False, project_name=project_path) as flat_api:
                program = flat_api.getCurrentProgram()

                # Communicate with Decompiler Interface
                decomp_interface = DecompInterface()

                # Open current program in Decompiler interface
                try:
                    decomp_interface.openProgram(program)
                except Exception as e:
                    self.logger.warning(f"ERROR occurred while trying to open the binary in Ghidra: {e}")
                    return False

                # Get recognised functions
                functions = program.getFunctionManager().getFunctions(True)

                # Iterate over all ghidra recognised functions in the binary and output them as a file
                with open(f"{output_path}", "w") as output_file:
                    function_processed = 0
                    for function in functions:
                        # Decompilation script sourced from:
                        # https://github.com/galoget/ghidra-headless-scripts/blob/main/decompile_simple.py
                        try:
                            decomp_function = decomp_interface.decompileFunction(function, 0, ConsoleTaskMonitor())
                            output = decomp_function.getDecompiledFunction().getC()
                            # process_function will return 1 if a function is successfully written to the outfile
                            # process_function will return 0 otherwise.
                            function_processed += self.process_function(function, output, output_file)
                        except Exception as e:
                            output_file.write(
                                f"// ERROR while decompiling this function: {e}\n// Moving on to next Function\n\n"
                            )

            return function_processed > 0  # True if at least 1 function was written, otherwise False
        except Exception:
            return False
        finally:
            if decomp_interface:
                decomp_interface.closeProgram()

    def cleanup_tempfiles(self):
        """Cleanup temporary files left behind by ghidra."""
        shutil.rmtree(self.cfg.ghidra_config_path, ignore_errors=True)
        try:
            temp_dir = pathlib.Path(tempfile.gettempdir())
            for file in temp_dir.iterdir():
                # Delete all old temp files created by ghidra
                if file.is_dir() and file.name.lower().startswith(GHIDRA_PREFIX.lower()):
                    shutil.rmtree(str(file.absolute()), ignore_errors=True)
        except Exception:
            self.logger.warning(f"unable to cleanup temp directory with error {traceback.format_exc()}")

    def execute(self, job: Job):
        """Run the plugin."""
        binary = job.get_data().get_filepath()

        with tempfile.TemporaryDirectory(prefix=GHIDRA_PREFIX + str(job.id), delete=True) as temp_dir:
            # Setting name of project here so that the project is correctly cleaned up after running
            proj_name = os.path.basename(temp_dir)
            output_path_decompilation = str(os.path.join(temp_dir, "GhidraDecompilation"))
            os.makedirs(os.path.dirname(output_path_decompilation), exist_ok=True)
            # Setting ghidra install directory here is required for the running of `run_ghidra`
            # Uncomment try-except statement when testing locally, and update path to local Ghidra installation
            # try:

            ghidra_path = find_directory(self.ghidra_plugin_path)
            os.environ["GHIDRA_INSTALL_DIR"] = ghidra_path

            if not os.path.exists(ghidra_path):
                raise Exception(f"Ghidra cannot be found at the path {ghidra_path}")
            # except:
            # os.environ["GHIDRA_INSTALL_DIR"] = "/path/to/local/installation/ghidra_x.y.z_PUBLIC"
            run_success = self.run_ghidra(binary, output_path_decompilation, proj_name)
            if not run_success:
                return State(
                    State.Label.OPT_OUT,
                    message="Unable to open binary in Ghidra Headless Mode.",
                )

            with open(output_path_decompilation, "rb") as output_file:
                self.add_data_file(DataLabel.DECOMPILED_C, {}, output_file)

        self.cleanup_tempfiles()


def main():
    """Plugin command-line entrypoint."""
    cmdline_run(plugin=AzulPluginGhidra)


if __name__ == "__main__":
    main()
