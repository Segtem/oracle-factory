"""Correr un comando con una terminal como entrada, como cuando una persona escribe.

Sólo para pruebas y arneses que simulan a una persona: un agente real usa --agente.
"""
import os
import pty
import subprocess


def en_terminal(argv, *, cwd, env=None, entrada='', timeout=90):
    madre, hija = pty.openpty()
    try:
        proceso = subprocess.Popen([str(a) for a in argv], cwd=cwd, env=env, stdin=hija, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, encoding='utf-8')
        # Lo que la persona escribe, y después fin de entrada (^D) para que una lectura de más no quede esperando.
        os.write(madre, entrada.encode('utf-8') + b'\x04')
        salida, error = proceso.communicate(timeout=timeout)
    finally:
        os.close(hija)
        os.close(madre)
    return subprocess.CompletedProcess(proceso.args, proceso.returncode, salida, error)
