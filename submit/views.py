from django.shortcuts import render
from django.http import HttpResponse
from submit.forms import CodeSubmissionForm
from django.conf import settings
import os
import uuid
import subprocess
from pathlib import Path
from django.contrib.auth.decorators import login_required

@login_required
def submit(request):
    if request.method == "POST":
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save()
            print(submission.language)
            print(submission.code)
            output = run_code(
                submission.language, submission.code, submission.input_data
            )
            submission.output_data = output
            submission.save()
            return render(request, "result.html", {"submission": submission})
    else:
        form = CodeSubmissionForm()
    return render(request, "index.html", {"form": form})


def run_code(language, code, input_data):
    project_path = Path(settings.BASE_DIR)
    directories = ["codes", "inputs", "outputs"]

    for directory in directories:
        dir_path = project_path / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

    unique = str(uuid.uuid4())
    code_file_name = f"{unique}.cpp" if language == "cpp" else f"{unique}.py"
    input_file_name = f"{unique}.txt"
    output_file_name = f"{unique}_output.txt"

    codes_dir = project_path / "codes"
    inputs_dir = project_path / "inputs"
    outputs_dir = project_path / "outputs"
    code_file_path = codes_dir / code_file_name
    input_file_path = inputs_dir / input_file_name
    output_file_path = outputs_dir / output_file_name

    # Write code and input to respective files
    with open(code_file_path, "w") as code_file:
        code_file.write(code)
    with open(input_file_path, "w") as input_file:
        input_file.write(input_data)

    if language == "cpp":
        # Compile the C++ code using g++
        executable_path = codes_dir / unique
        compile_result = subprocess.run(
            ["g++", str(code_file_path), "-o", str(executable_path)],
            capture_output=True,
            text=True
        )

        if compile_result.returncode != 0:
            return compile_result.stderr  # Return the compilation error

        # Run the compiled executable
        with open(input_file_path, "r") as input_file, open(output_file_path, "w") as output_file:
            subprocess.run(
                [str(executable_path)],
                stdin=input_file,
                stdout=output_file
            )
    elif language == "py":
        # Execute Python code
        with open(input_file_path, "r") as input_file, open(output_file_path, "w") as output_file:
            subprocess.run(
                ["python3", str(code_file_path)],
                stdin=input_file,
                stdout=output_file
            )

    # Read the output from the output file
    with open(output_file_path, "r") as output_file:
        output_data = output_file.read()

    return output_data


