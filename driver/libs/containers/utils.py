from driver.libs.types import ExecutableCommand


class ExecutionCommandBuilder:
    # Set of command templates
    timeout_command_template = ''
    time_command_template = 'time -f \"%e\" timeout {} {}'
    stdin_pipe_template = 'echo -e \"{}\" | {}'
    shell_wrapper_template = 'sh -c \'{}\''

    @staticmethod
    def build(file_execution_command: ExecutableCommand, stdin: str, time_limit: int) -> ExecutableCommand:
        """Step by step builds full execution command that will be run in Docker container"""
        time_command = ExecutionCommandBuilder.time_command_template.format(time_limit, file_execution_command)
        stdin_pipe = ExecutionCommandBuilder.stdin_pipe_template.format(stdin, time_command)
        shell_wrapper = ExecutionCommandBuilder.shell_wrapper_template.format(stdin_pipe)

        return shell_wrapper
