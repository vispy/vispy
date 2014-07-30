# -*- coding: utf-8 -*-

import subprocess
import inspect


def run_subprocess(command):
    """Run command using subprocess.Popen

    Run command and wait for command to complete. If the return code was zero
    then return, otherwise raise CalledProcessError.
    By default, this will also add stdout= and stderr=subproces.PIPE
    to the call to Popen to suppress printing to the terminal.

    Parameters
    ----------
    command : list of str
        Command to run as subprocess (see subprocess.Popen documentation).

    Returns
    -------
    stdout : str
        Stdout returned by the process.
    stderr : str
        Stderr returned by the process.
    """
    # code adapted with permission from mne-python
    kwargs = dict(stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    p = subprocess.Popen(command, **kwargs)
    stdout_, stderr = p.communicate()

    output = (stdout_, stderr)
    if p.returncode:
        print(stdout_)
        print(stderr)
        err_fun = subprocess.CalledProcessError.__init__
        if 'output' in inspect.getargspec(err_fun).args:
            raise subprocess.CalledProcessError(p.returncode, command, output)
        else:
            raise subprocess.CalledProcessError(p.returncode, command)

    return output
