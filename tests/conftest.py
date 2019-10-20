from logging import getLogger

import py
import pytest
from _pytest.pytester import Testdir

log = getLogger(__name__)
MPI_ARGS = ("mpirun", "-n")


@pytest.fixture
def has_mpi4py():
    try:
        import mpi4py
        return True
    except ImportError:
        return False


class MPITestdir(Testdir):
    def __init__(self, request, tmpdir_factory):
        super().__init__(request, tmpdir_factory)
        method = self.request.config.getoption("--runpytest")
        if method == "inprocess":
            log.warn("To run the MPI tests, you need to use subprocesses")

    def runpytest_subprocess(self, *args, timeout=None, mpi_procs=2):
        """
        Based on testdir.runpytest_subprocess
        """
        p = py.path.local.make_numbered_dir(
            prefix="runpytest-", keep=None, rootdir=self.tmpdir
        )
        args = ("--basetemp=%s" % p,) + args
        plugins = [x for x in self.plugins if isinstance(x, str)]
        if plugins:
            args = ("-p", plugins[0]) + args
        args = MPI_ARGS + (str(mpi_procs),) + self._getpytestargs() + args
        return self.run(*args, timeout=timeout)

    def runpytest(self, *args, **kwargs):
        return self.runpytest_subprocess(*args, **kwargs)


@pytest.fixture
def mpi_testdir(request, tmpdir_factory):
    return MPITestdir(request, tmpdir_factory)
